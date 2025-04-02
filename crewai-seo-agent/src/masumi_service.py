#!/usr/bin/env python
import os
import uuid
import logging
import asyncio
import uvicorn
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

# Import your existing SEO Crew
from crew import SEOAnalyseCrew

# Import Masumi payment libraries
# This will be implemented in a real project
class Amount(BaseModel):
    amount: str
    unit: str

class StartJobRequest(BaseModel):
    text: str

# Initialize temporary storage
jobs = {}  # In production, use a database
payment_instances = {}  # Store payment instances by job_id

# Placeholder for Masumi Payment class
class Payment:
    def __init__(self, agent_identifier, amounts, config, identifier_from_purchaser):
        self.agent_identifier = agent_identifier
        self.amounts = amounts
        self.config = config
        self.identifier = identifier_from_purchaser
        self.payment_ids = set()
        self._monitoring = False
    
    async def create_payment_request(self):
        # Mock implementation - replace with actual API call
        return {
            "data": {
                "blockchainIdentifier": str(uuid.uuid4()),
                "submitResultTime": datetime.now().isoformat(),
                "unlockTime": (datetime.now().timestamp() + 3600),
                "externalDisputeUnlockTime": (datetime.now().timestamp() + 7200),
            }
        }
    
    async def check_payment_status(self):
        # Mock implementation - replace with actual API call
        return {"data": {"status": "completed"}}
    
    async def start_status_monitoring(self, callback):
        self._monitoring = True
        asyncio.create_task(self._monitor_status(callback))
    
    def stop_status_monitoring(self):
        self._monitoring = False
    
    async def _monitor_status(self, callback):
        while self._monitoring:
            for payment_id in self.payment_ids:
                status = await self.check_payment_status()
                if status.get("data", {}).get("status") == "completed":
                    await callback(payment_id)
            await asyncio.sleep(5)
    
    async def complete_payment(self, payment_id, result_hash):
        # Mock implementation - replace with actual API call
        print(f"Payment {payment_id} completed with result hash {result_hash}")
        return True

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="SEO Analysis API with Masumi Payments",
    description="API for analyzing websites with monetization via Masumi Network",
    version="1.0.0"
)

# Define config (replace with actual values)
config = {
    "payment_service_url": os.getenv("PAYMENT_SERVICE_URL", "http://localhost:3000"),
    "api_key": os.getenv("PAYMENT_SERVICE_API_KEY", "your-api-key")
}

# Health check endpoints
@app.get("/healthz")
async def healthz():
    """Kubernetes-style health check endpoint"""
    return {"status": "healthy"}

@app.get("/health")
async def health():
    """Health check endpoint for container monitoring"""
    return {"status": "healthy"}

@app.get("/ready")
async def ready():
    """Readiness check endpoint"""
    return {"status": "ready"}

# Execute crew task
async def execute_crew_task(input_text):
    """Execute the SEO analysis crew with the given input"""
    try:
        crew = SEOAnalyseCrew(input_text)
        result = crew.run(str(uuid.uuid4()))  # Use a unique job ID
        return result
    except Exception as e:
        logger.error(f"Error executing crew task: {str(e)}")
        raise

# ─────────────────────────────────────────────────────────────────────────────
# 1) Start Job (MIP-003: /start_job)
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/start_job")
async def start_job(data: StartJobRequest):
    """ Initiates a job and creates a payment request """
    job_id = str(uuid.uuid4())
    agent_identifier = "YOUR_AGENT_IDENTIFIER"  # Replace with your agent identifier

    # Define payment amounts (in lovelace - 1 ADA = 1,000,000 lovelace)
    amounts = [Amount(amount="10000000", unit="lovelace")]  # 10 ADA
    
    # Create a payment request using Masumi
    payment = Payment(
        agent_identifier=agent_identifier,
        amounts=amounts,
        config=config,
        identifier_from_purchaser=f"seo_analysis_{job_id}" 
    )
    
    payment_request = await payment.create_payment_request()
    payment_id = payment_request["data"]["blockchainIdentifier"]
    payment.payment_ids.add(payment_id)

    # Store job info
    jobs[job_id] = {
        "status": "awaiting_payment",
        "payment_status": "pending",
        "payment_id": payment_id,
        "input_data": data.text,
        "result": None
    }

    async def payment_callback(payment_id: str):
        await handle_payment_status(job_id, payment_id)

    # Start monitoring the payment status
    payment_instances[job_id] = payment
    await payment.start_status_monitoring(payment_callback)

    # Return response
    return {
        "status": "success",
        "job_id": job_id,
        "blockchainIdentifier": payment_request["data"]["blockchainIdentifier"],
        "submitResultTime": payment_request["data"]["submitResultTime"],
        "unlockTime": payment_request["data"]["unlockTime"],
        "externalDisputeUnlockTime": payment_request["data"]["externalDisputeUnlockTime"],
        "agentIdentifier": agent_identifier,
        "sellerVkey": "YOUR_SELLER_VKEY",  # Get this from /payment_source/ endpoint
        "identifierFromPurchaser": f"seo_analysis_{job_id}",
        "amounts": amounts
    }

# ─────────────────────────────────────────────────────────────────────────────
# 2) Process Payment and Execute AI Task
# ─────────────────────────────────────────────────────────────────────────────
async def handle_payment_status(job_id: str, payment_id: str) -> None:
    """ Executes CrewAI task after payment confirmation """
    logger.info(f"Payment {payment_id} completed for job {job_id}, executing task...")
    
    # Update job status
    jobs[job_id]["status"] = "running"
    
    try:
        # Execute the AI task
        result = await execute_crew_task(jobs[job_id]["input_data"])
        logger.info(f"Crew task completed for job {job_id}")

        # Convert result to string if needed
        result_str = str(result) if not isinstance(result, str) else result
        
        # Mark payment as completed on Masumi
        result_hash = result_str[:64] if len(result_str) >= 64 else result_str
        await payment_instances[job_id].complete_payment(payment_id, result_hash)
        logger.info(f"Payment completed for job {job_id}")

        # Update job status
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["payment_status"] = "completed"
        jobs[job_id]["result"] = result
    
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {str(e)}")
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
    
    finally:
        # Stop monitoring payment status
        if job_id in payment_instances:
            payment_instances[job_id].stop_status_monitoring()
            del payment_instances[job_id]

# ─────────────────────────────────────────────────────────────────────────────
# 3) Check Job and Payment Status (MIP-003: /status)
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/status")
async def get_status(job_id: str):
    """ Retrieves the current status of a specific job """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]

    # Check latest payment status if payment instance exists
    if job_id in payment_instances:
        status = await payment_instances[job_id].check_payment_status()
        job["payment_status"] = status.get("data", {}).get("status")

    return {
        "job_id": job_id,
        "status": job["status"],
        "payment_status": job["payment_status"],
        "result": job.get("result")
    }

# ─────────────────────────────────────────────────────────────────────────────
# 4) Check Server Availability (MIP-003: /availability)
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/availability")
async def check_availability():
    """ Checks if the server is operational """
    return {
        "status": "available",
        "message": "The SEO analysis service is running smoothly."
    }

# ─────────────────────────────────────────────────────────────────────────────
# 5) Retrieve Input Schema (MIP-003: /input_schema)
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/input_schema")
async def input_schema():
    """ Returns the expected input schema for the /start_job endpoint """
    schema_example = {
        "input_data": [
            {"key": "text", "value": "string", "description": "The URL to analyze for SEO"}
        ]
    }
    return schema_example

# Run the application
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 