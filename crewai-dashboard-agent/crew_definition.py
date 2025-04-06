from crewai import Agent, Crew, Task
from logging_config import get_logger
from tools.dashboard_tools import DataFetcherTool, ChartDesignerTool
from tools.jupyter_tools import JupyterDashboardTool

class DashboardCrew:
    def __init__(self, verbose=True, logger=None):
        self.verbose = verbose
        self.logger = logger or get_logger(__name__)
        self.crew = self.create_crew()
        self.logger.info("DashboardCrew initialized")

    def create_crew(self):
        self.logger.info("Creating dashboard crew with agents")
        
        interpreter = Agent(
            role='Prompt Interpreter',
            goal='Understand user requirements and translate them into structured data requests',
            backstory='Expert at analyzing natural language requests and extracting key dashboard requirements',
            verbose=self.verbose
        )

        data_fetcher = Agent(
            role='Data Fetcher',
            goal='Retrieve and prepare data from various sources',
            backstory='Specialist in data extraction and preparation from multiple sources',
            tools=[DataFetcherTool()],
            verbose=self.verbose
        )

        designer = Agent(
            role='Chart Designer',
            goal='Design optimal visualizations for data insights',
            backstory='Expert in data visualization and chart selection',
            tools=[ChartDesignerTool()],
            verbose=self.verbose
        )

        jupyter_builder = Agent(
            role='Jupyter Dashboard Builder',
            goal='Create interactive Jupyter notebooks with dashboards',
            backstory='Expert in creating interactive Jupyter dashboards with widgets',
            tools=[JupyterDashboardTool()],
            verbose=self.verbose
        )

        self.logger.info("Created all dashboard agents")

        crew = Crew(
            agents=[interpreter, data_fetcher, designer, jupyter_builder],
            tasks=[
                Task(
                    description='Interpret dashboard requirements: {text}',
                    expected_output='Structured dashboard requirements including data sources and visualization needs',
                    agent=interpreter
                ),
                Task(
                    description='Fetch and prepare required data',
                    expected_output='Clean, processed dataset ready for visualization',
                    agent=data_fetcher
                ),
                Task(
                    description='Design optimal visualizations',
                    expected_output='Chart specifications and layout recommendations',
                    agent=designer
                ),
                Task(
                    description='Build interactive Jupyter dashboard',
                    expected_output='Complete Jupyter notebook with interactive dashboard',
                    agent=jupyter_builder
                )
            ]
        )
        self.logger.info("Dashboard crew setup completed")
        return crew