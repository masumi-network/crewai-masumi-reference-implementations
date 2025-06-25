from crewai import Agent, Crew, Task
from logging_config import get_logger
from pydantic import BaseModel
from scrapflyscraper import WebScraper
from contacttool import ContactScraper

class ContactResult(BaseModel):
    contact: str

class ContactCrew():
    def __init__(self,verbose=True, logger=None):
        self.verbose = verbose
        self.logger = logger or get_logger(__name__)
        self.crew = self.create_crew()
        self.logger.info("ResearchCrew initialized")

    def create_crew(self):
        self.logger.info("Creating research crew with agents")
        
        contactFinder = Agent(
            role='Company Contact Page Finder',
            goal='Given a company URL, find the most likely contact page URL.',
            backstory='Expert at searching for relevant company contact pages.',
            verbose=self.verbose
        )

        emailScraper = Agent(
            role='Contact Page Email Scraper',
            goal='Given a contact page URL, scrape it and return a the best suiting contact email address if found. if not, return the url of the contact page instead',
            backstory='Expert at scraping web pages and extracting email addresses.',
            verbose=self.verbose
        )

        self.logger.info("Created contact finder and email scraper agents")

        # Task 1: Find contact page URL
        find_contact_task = Task(
            description="""Given {text} (a company website URL), use the contact finder tool to return the most likely contact page URL.""",
            expected_output="""The contact page URL as a string.""",
            agent=contactFinder,
            tools=[ContactScraper()]
        )

        # Task 2: Scrape contact page for email
        scrape_email_task = Task(
            description="""from a given context,use the web scraper tool to extract and return the best suting email address found on the page. If no email is found, return an the page url.""",
            expected_output="""The email address found on the contact page, or the contact page url if none found.""",
            agent=emailScraper,
            tools=[WebScraper()],
            output_pydantic=ContactResult
        )

        crew = Crew(
            agents=[contactFinder, emailScraper],
            tasks=[find_contact_task, scrape_email_task]
        )
        self.logger.info("Crew setup completed")
        return crew
    
