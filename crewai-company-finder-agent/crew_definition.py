from crewai import Agent, Crew, Task
from logging_config import get_logger
import pandas as pd
from pydantic import BaseModel
from scrapertool import Scraper



class result(BaseModel):
    result: list[str]
    prompt: str

class ResearchCrew():
    def __init__(self,verbose=True, logger=None):
        self.verbose = verbose
        self.logger = logger or get_logger(__name__)
        self.crew = self.create_crew()
        self.logger.info("ResearchCrew initialized")

    def create_crew(self):
        self.logger.info("Creating research crew with agents")
        
        companyFinder = Agent(
            role='Company Finder',
            goal='Read the prompt from the input and use tools to make a list of companies that appear and avoid duplicates',
            backstory='Expert at searching for relevant companies and compiling them into a list',
            verbose=self.verbose
        )


        self.logger.info("Created research and writer agents")

        crew = Crew(
            agents=[companyFinder],
            tasks=[
                Task(
                    description="""read {text} and use that as the input for the contact finder tool and return the URLS as a list. 
                                    If there is a country in the input, use that as the search tools country variable as a two letter word. 
                                    EXAMPLE: France -> \"fr\", Poland -> \"pl\", if none are provided, use the default of \"us\"(united states)
                                    If there are any domains in the input (.com, .io, .ie, etc.) then add them to a list and use that in the tool's 'domain' argument, if none are present then default to .com
                                    For the url argument, get the TYPE of company requested, e.g. \"Companies in Photography\" -> url = \"Photography\", \"Ai healthcare companies\" -> url = \"Ai healtchare\", NOT including the word \"company\" or \"companies\" in the url,
                                    that will be handled by the agent,so in \"AI companies\" only the attributive noun of AI is to be returned. This goes for any input
                                    returning that type in the prompt field of the basemodel output
                                      """,
                    expected_output= """A list of company base URLS, nothing else., Only return the root url, for example:https://www.company.com/contact/about-us -> https://www.company.com 
                                        And the company type from the input text e.g. \"Companies in Photography\" -> url = \"Photography\"  returned to the prompt field of the result basemodel
                                        NO DUPLICATES""", 
                    agent=companyFinder,
                    tools=[Scraper()],
                    output_pydantic = result
                )
            ]
        )
        self.logger.info("Crew setup completed")
        return crew
    
