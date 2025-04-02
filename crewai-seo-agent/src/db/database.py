# src/db/database.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import json
import logging
from urllib.parse import urlparse
from typing import Any, Dict, Optional
from threading import Lock

logger = logging.getLogger(__name__)

class Database:
    """Database connection manager with connection pooling"""
    
    def __init__(self):
        """Initialize database connection manager"""
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")
        
        self.max_connections = int(os.getenv('DB_MAX_CONNECTIONS', '5'))
        self._lock = Lock()
        self._connections = []

    @contextmanager
    def get_connection(self):
        """Get a database connection from the pool"""
        connection = None
        try:
            logger.debug(f"Connecting to database with URL: {self.database_url}")
            with self._lock:
                # Clean up any closed connections
                self._connections = [conn for conn in self._connections if not conn.closed]
                
                # Create new connection if needed
                if len(self._connections) < self.max_connections:
                    connection = psycopg2.connect(self.database_url)
                    self._connections.append(connection)
                else:
                    # Wait for an available connection
                    connection = self._connections.pop(0)
            
            yield connection
            
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            if connection:
                connection.rollback()
            raise
        
        finally:
            if connection and not connection.closed:
                with self._lock:
                    self._connections.append(connection)

    def create_job(self, website_url: str) -> str:
        """Create a new SEO analysis job"""
        with self.get_connection() as conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(
                """
                INSERT INTO seo_jobs (website_url, status) 
                VALUES (%s, 'pending') 
                RETURNING id::text, website_url, status
                """,
                (website_url,)
            )
            conn.commit()
            result = cur.fetchone()
            return result['id']  # Return just the ID as a string

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status and details"""
        with self.get_connection() as conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(
                """
                SELECT id::text as id, website_url, status, 
                       created_at, completed_at, error,
                       final_answer
                FROM seo_jobs 
                WHERE id = %s
                """,
                (job_id,)
            )
            result = cur.fetchone()
            if result is None:
                return None
            
            # Convert result to dict to ensure string key access works
            return dict(result)

    def update_job_results(self, job_id: str, results: Dict[str, Any]) -> None:
        """Update job with analysis results"""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE seo_jobs 
                SET status = 'completed',
                    completed_at = CURRENT_TIMESTAMP,
                    final_answer = %s
                WHERE id = %s
                """,
                (json.dumps(results), job_id)
            )
            conn.commit()

    def update_job_error(self, job_id: str, error: str) -> None:
        """Update job with error status"""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE seo_jobs 
                SET status = 'error',
                    completed_at = CURRENT_TIMESTAMP,
                    error = %s
                WHERE id = %s
                """,
                (error, job_id)
            )
            conn.commit()

    def cleanup_old_jobs(self, days: int = 7) -> None:
        """Clean up jobs older than specified days"""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                DELETE FROM seo_jobs 
                WHERE created_at < NOW() - INTERVAL '%s days'
                """,
                (days,)
            )
            conn.commit()