from crewai import Agent, Crew, Task
from logging_config import get_logger
from pydantic import BaseModel
from scrapflyscraper import WebScraper



class result(BaseModel):
    result: str
    canonical:str
    email: str

class ValidatorCrew():
    def __init__(self,verbose=True, logger=None):
        self.verbose = verbose
        self.logger = logger or get_logger(__name__)
        self.crew = self.create_crew()
        self.logger.info("ResearchCrew initialized")

    def create_crew(self):
        self.logger.info("Creating research crew with agents")

        validator = Agent(
            role='Contact Validator',
            goal='Read the list of urls from a given context, scrape them and find return the names of each company and their canonical url from their website and their main contact email address ONLY if available in website',
            backstory='Expert at finding company names, canonical urls and contact emails from urls, ensuring that the real name and email is returned should the url redirect to a different company name than what was in the url',
            verbose=self.verbose
        )

        self.logger.info("Created research and writer agents")

        crew = Crew(
            agents=[validator],
            tasks=[
                Task(
                    description="""Read {text} use tools to scrape the url and return the root domain name, canonical https url and main contact email address of the company from the website ONLY if it's a company, if it is a blog or news website, skip over it and do not return anything """,
                    expected_output= """The Top-level (.io,.com etc) and second-level domain name of the company from the scraped website along with its canoncial url returned in the \"canonical\" field of the basemodel. ONLY if it isnt a blog, news, survey or article website. the result MUST be a domain, COMPANY.io for example, it cannot be COMPANY by itself. This is imperitive for differentiating same-name companies
                                        AND the main contact email address in the email field of the result basemodel, just the main contact email address. if not found on the website, return CANNOT FIND EMAIL in the field
                                        DO NOT try to generate an email if none are found.
                                        If no canonical URLS are returned, return a blank space \" \" in the canonical field. NOTHING ELSE""",
                    agent=validator,
                    tools=[WebScraper()],
                    output_pydantic = result
                )
            ]
        )
        self.logger.info("Crew setup completed")
        return crew
    
