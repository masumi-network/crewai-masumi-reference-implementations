# src/crew.py
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv
import openai
import os
import yaml
from .tools.LoadingTimeTracker import LoadingTimeTracker
from .tools.MobileTesting import MobileOptimizationTool
from .tools.SubpageAnalyzer import SubpageAnalyzer
from .tools.BrowserlessScraper import BrowserlessScraper
import asyncio
from typing import Dict, Any, List
import logging
from .db.database import Database

logger = logging.getLogger(__name__)

load_dotenv()

@CrewBase
class SEOAnalyseCrew():
    """
    Main class that orchestrates the SEO analysis process using multiple AI agents.
    It handles data collection, analysis, and optimization recommendations.
    """
    agents_config = os.path.join(os.path.dirname(__file__), 'config', 'agents.yaml')
    tasks_config = os.path.join(os.path.dirname(__file__), 'config', 'tasks.yaml')

    def __init__(self, website_url: str):
        """Initialize with target website URL and load config files"""
        self.website_url = website_url
        logger.info(f"Initializing SEO Analysis Crew for {website_url}")
        
        # Initialize database connection
        self.db = Database()
        
        with open(self.agents_config, 'r') as f:
            self.agents_config = yaml.safe_load(f)
        with open(self.tasks_config, 'r') as f:
            self.tasks_config = yaml.safe_load(f)
            
        self.tools = [
            BrowserlessScraper(),
            LoadingTimeTracker(),
            MobileOptimizationTool(),
            SubpageAnalyzer()
        ]
        logger.info("Tools initialized successfully")
        
        self.agents = {
            'scraper_agent': self.scraper_agent(),
            'analyse_agent': self.analyse_agent(),
            'optimization_agent': self.optimization_agent()
        }
        logger.info("Agents initialized successfully")
        
        self.tool_timeout = 60
        super().__init__()

    openai_llm = LLM(
        model='gpt-4o',
        api_key=os.getenv('OPENAI_API_KEY'),
        max_retries=3,
        temperature=0.5
    )

    @agent
    def scraper_agent(self) -> Agent:
        """Agent responsible for collecting data from the website"""        
        return Agent(
            role=self.agents_config['scraper_agent']['role'],
            goal=self.agents_config['scraper_agent']['goal'],
            backstory=self.agents_config['scraper_agent']['backstory'],
            tools=self.tools,
            verbose=True,
            llm=self.openai_llm
        )

    @agent
    def analyse_agent(self) -> Agent:
        """Agent responsible for analyzing collected data"""
        return Agent(
            role=self.agents_config['analyse_agent']['role'],
            goal=self.agents_config['analyse_agent']['goal'],
            backstory=self.agents_config['analyse_agent']['backstory'],
            verbose=True,
            llm=self.openai_llm
        )
    
    @agent
    def optimization_agent(self) -> Agent:
        """Agent responsible for providing optimization recommendations"""
        return Agent(
            role=self.agents_config['optimization_agent']['role'],
            goal=self.agents_config['optimization_agent']['goal'],
            backstory=self.agents_config['optimization_agent']['backstory'],
            verbose=True,
            llm=self.openai_llm
        )

    @task
    def data_collection_task(self) -> Task:
        """Task for collecting website data"""
        task_config = self.tasks_config['data_collection_task']
        return Task(
            description=task_config['description'].format(website_url=self.website_url),
            expected_output=task_config['expected_output'].format(website_url=self.website_url),
            agent=self.agents['scraper_agent'],
            context_variables={"website_url": self.website_url},
            max_retries=3
        )

    @task
    def analysis_task(self) -> Task:
        """Task for analyzing collected data"""
        task_config = self.tasks_config['analysis_task']
        return Task(
            description=task_config['description'].format(website_url=self.website_url),
            agent=self.agents['analyse_agent'],
            expected_output=task_config['expected_output']
        )

    @task
    def optimization_task(self) -> Task:
        """Task for generating optimization recommendations"""
        task_config = self.tasks_config['optimization_task']
        return Task(
            description=task_config['description'],
            agent=self.agents['optimization_agent'],
            expected_output=task_config['expected_output']
        )

    def _process_final_answer(self, output) -> Dict[str, Any]:
        """Process the crew's output into a structured format"""
        try:
            if isinstance(output, str):
                # If output is a string, try to extract relevant sections
                return {
                    "priority_fixes": self._extract_section(output, "Priority Fixes"),
                    "impact_forecast": self._extract_section(output, "Impact Forecast"),
                    "key_statistics": self._extract_section(output, "Key Statistics"),
                    "page_specific": self._extract_section(output, "Page-Specific Optimizations"),
                    "implementation_timeline": self._extract_section(output, "Implementation Timeline")
                }
            elif isinstance(output, dict):
                # If output is already a dictionary, return it
                return output
            else:
                # For CrewOutput object, convert to string and process
                return self._process_final_answer(str(output))
            
        except Exception as e:
            logger.error(f"Error processing final answer: {str(e)}")
            return {"error": str(e)}

    def _extract_section(self, text: str, section_name: str) -> Dict[str, Any]:
        """Extract a section from the text output"""
        try:
            # Find the section
            start = text.find(section_name + ":")
            if start == -1:
                return None
            
            # Find the next section or end of text
            next_section = float('inf')
            for section in ["Priority Fixes:", "Impact Forecast:", "Key Statistics:", 
                           "Page-Specific Optimizations:", "Implementation Timeline:"]:
                pos = text.find(section, start + len(section_name))
                if pos != -1 and pos < next_section:
                    next_section = pos
                
            # Extract and clean the section content
            content = text[start + len(section_name) + 1:
                          next_section if next_section != float('inf') else None]
            
            # Convert to dictionary format
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            result = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    result[key.strip()] = value.strip()
                elif '-' in line:
                    key = line.split('-', 1)[1].strip()
                    if 'items' not in result:
                        result['items'] = []
                    result['items'].append(key)
                
            return result
        
        except Exception as e:
            logger.error(f"Error extracting section {section_name}: {str(e)}")
            return None

    async def run(self, job_id: str) -> Dict[str, Any]:
        """Run the SEO analysis crew and store results"""
        try:
            crew = Crew(
                agents=[self.scraper_agent(), self.analyse_agent(), self.optimization_agent()],
                tasks=[
                    self.data_collection_task(),
                    self.analysis_task(),
                    self.optimization_task()
                ],
                process=Process.sequential,
                verbose=True
            )
            
            output = crew.kickoff()
            results = self._process_final_answer(output)
            
            # Store results in database
            self.db.update_job_results(job_id, results)
            return results
            
        except Exception as e:
            logger.error(f"Crew run error: {str(e)}")
            self.db.update_job_error(job_id, str(e))
            return {"error": str(e)}