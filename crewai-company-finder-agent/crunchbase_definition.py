from crewai import Agent, Crew, Task
from logging_config import get_logger
import pandas as pd
from typing import Generator, Type
from pydantic import BaseModel
from crunchbase_search import CrunchbaseSearch



class result(BaseModel):
    result: str

class CrunchbaseCrew():
    def __init__(self,verbose=True, logger=None):
        self.verbose = verbose
        self.logger = logger or get_logger(__name__)
        self.crew = self.create_crew()
        self.logger.info("ResearchCrew initialized")

    def create_crew(self):
        self.logger.info("Creating research crew with agents")

        searcher = Agent(
            role='Crunchbase URL searcher',
            goal='Read the given URL,use a tool to parse a google search for a crunchbase company url and return the first contact email address from the snippets in the results',
            backstory='Expert at finding crunchbase company profiles from given input, then find and return the first main contact email from returned snippets ',
            verbose=self.verbose
        )

        self.logger.info("Created research and writer agents")

        crew = Crew(
            agents=[searcher],
            tasks=[
                Task(
                    description="""Read {text}. {canonical} and {prompt} use tools to make a google search for a crunchbase company profile, scan the results and return the first email from the returned snippets and NOTHING else
                                ONLY if this input: {email} \"is CANNOT FIND EMAIL\" or in fact not an email adress at all. If it IS an email address, then DO NOT run the tool and instead return \"SATISFIED\" 
                                ELSE, run the tool with domain parameter as {text}, the canonical parameter as {canonical} and prompt parameter as {prompt} and return the first email address from the returned snippets""",
                    expected_output= """The best matching email address from the tool, if not found, return \"CANNOT FIND EMAIL\"""",
                    agent=searcher,
                    tools=[CrunchbaseSearch()],
                    output_pydantic = result
                )
            ]
        )
        self.logger.info("Crew setup completed")
        return crew