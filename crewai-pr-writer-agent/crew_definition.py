from crewai import Agent, Crew, Task
from logging_config import get_logger
from crewai_tools import ScrapeWebsiteTool
from pydantic import BaseModel

class PressRelease(BaseModel):
    filename: str
    content: str

class ResearchCrew:
    def __init__(self, verbose=True, logger=None):
        self.verbose = verbose
        self.logger = logger or get_logger(__name__)
        self.crew = self.create_crew()
        self.logger.info("ResearchCrew initialized")

    def create_crew(self):
        self.logger.info("Creating research crew with agents")
        

        writer = Agent(
            role='PR Writer',
            goal='Create clear, high quality and informative Press Releases',
            backstory='Skilled at transforming complex information into expertly written press releases',
            verbose=self.verbose
        )

        self.logger.info("Created research and writer agents")

        crew = Crew(
            agents=[writer],
            tasks=[
                Task(
                    description="""Write a Press Release based on the input info: {text}, If a URL is in it, scrape its website and Analyze the contents,All Metadata should be ignored along with other external info like button names and ads.
                    Based on the text in the input along with the information from the URL (if url provided) Create an engaging, clear and informative press release.

                    You should return a python dictionary with the following fields:

                    -filename: a filename for this pr. make it short and relevant to its topic.
                    -content: the actual press release. the whole generated press release.

                    your press release should satisfy all requirements in the input info.
                    DO NOT attempt to add contact information that is not stated in the invoice info or that is not in the web scraped
                    data.
                    """,
                    expected_output='A python Dictionary matching the PressRelease model structure',
                    agent=writer,
                    tools=[ScrapeWebsiteTool()],
                    output_json=PressRelease
                )
            ]
        )
        self.logger.info("Crew setup completed")
        return crew