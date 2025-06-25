from crewai import Agent, Crew, Task
from logging_config import get_logger
import pandas as pd
from typing import Generator, Type
from crewai_tools import ScrapeWebsiteTool
from scrapFlyScraper import XScraper
from pydantic import BaseModel

class result(BaseModel):
    result: str
    filename: str

class ResearchCrew():
    def __init__(self, csv_path: str,source :str ,verbose=True, logger=None):
        self.verbose = verbose
        self.logger = logger or get_logger(__name__)
        self.csv_path = csv_path
        self.source = source
        self.crew = self.create_crew()
        self.logger.info("ResearchCrew initialized")

    def create_crew(self):
        self.logger.info("Creating research crew with agents")
        
        fileReader = Agent(
            role='File Reader',
            goal='Read the input text from a CSV file and return a list of all URLS, their X handle and other contact (if any), in a pure format without any additional notes or shortening',
            backstory='Expert at extracting and identifying key information in its entirety',
            verbose=self.verbose
        )

        validator = Agent(
            role ='URL Validator',
            goal = 'To scrape websites from a given context and determine if they are related to AI and AI agents',
            backstory = 'Expert at scraping websites quickly, ignoring irrelevant information and validating their content',
            verbose = self.verbose
        )

        email_generator = Agent(
            role ='Email Generator',
            goal = """To analyse an input website of a company and generate an email to pitch that company to another company whos URL is from
                    A given context. Scrape that company's url too in order to better pitch the input company, saying how it would benefit them
                    specifically.""",
            backstory = """Expert at pitching products to other companyies, able to analyze both product and client website data in order to formulate
            concise, informative and captivating emails accurately outlining why the product should be chosen and how it can help the client""",
            verbose = self.verbose
        )

        self.logger.info("Created research and writer agents")

        crew = Crew(
            agents=[fileReader,validator,email_generator],
            tasks=[
                Task(
                    description='Analyse: {text} and return a concise list of all URLS, with their corresponding X handles and contacts beside them for each company.',
                    expected_output="""A concise list of all URLS, with their corresponding X handles and contacts beside them, DO not include things in brackets.
                                        for each company, the output MUST adhere to the following output structure:

                                        Company: COMPANY_NAME 
                                            - Url: URL
                                            - X-handle: X HANDLE
                                            - Other contact: OTHER CONTACT
                                            - UrlCheck: RELATED/UNRELATED/ERROR
                                                                
                                        The following guidelines are of utmost importance:
                                            -Under NO CIRCUMSTANCES should the analysis be cut short for brevity.
                                            -The whole output must be returned no matter how long it is.
                                            - The output must be a pure list, no additional notes are to be added.
                                            - There should be the SAME amount of elements as there are companies,
                                                as each element is for each company.
                                                absolutely ZERO parts of the input text can be ignored. 
                                                All lines MUST be read and an appropriate output for each company.
                                            - If ANY of these fields cannot be identified, it should be returned as "unable to find FIELD"
                                            -The URLS would lead to a website when searched, so anomalous text should not be mistaken for a URL
                                            - All URLS should be returned as a valid https url. I.E. www.company.com = https://www.company.com
                                            -If the URL is absurdly long and does not look like one at all, ignore it.
                                        If any of said guidelines are not followed, the task is considered failed
                                        and the output completely invalid.
                                        """,
                    agent=fileReader
                ),
                Task(
                    description= 'Review the context you got and look at the URLS, ignoring all metadata, buttons and external links to determin if the website content is related to AI and AI agents.',
                    expected_output= """The same format as the context you got, but in the urlcheck field,return RELATED or UNRELATED.  ERROR if there was an error accessing the website.
                                        Ensure that the format is EXACTLY the same:
                                        
                                        Company: COMPANY_NAME 
                                            - Url: URL
                                            - X-handle: X HANDLE
                                            - Other contact: OTHER CONTACT
                                            - UrlCheck: RELATED/UNRELATED/ERROR
                                            - XCheckL: RELATED/UNRELATED/ERROR
                                            - EMAIL: Email

                                        For scraping the X handle, use the XScraper tool. pass in a valid HTTP URL e.g. https://x.com/username
                                        A valid Url MUST be passed in the tool. If one isnt found for a company i.e., it was only a username and not a url in the input,
                                        Construct a URL for the username.
                                        The twitter username will ALWAYS start with an @ in the input. ignore ALL text before the @ when looking for the twitter handle.
                                        Same with the web scraping, analyse if the x handle is related to AI and AI agents.

                                        """,
                    agent=validator,
                    tools = [ScrapeWebsiteTool(),XScraper()]
                ),
                Task(
                    description = """Review the context you got. scrape the url in the URL field of the client company AND the URL of the user company: {url}.
                    Ignore all metadata, external links, buttons and irrelevant data in the urls.
                    Then Generate a professional, concise email body pitching the user company and their product to the client company, outlining in detail
                    why the client should consider the user's services and how it would be benefitial to the client company's specifics 
                    and their projects.
                    """,

                    expected_output = """An informative, intriguing email body pitching the user's company to the client's. Advertising how it would prove benefitial
                    The output should be in the email field of the context you got while also returning the context.The email is to be FROM the user: {url}, TO the client URL from the given context. NEVER the other way around
                    The context you were given should be returned in the result field of the output_json along with the email in this format:
                    Company: COMPANY_NAME 
                                            - Url: URL
                                            - X-handle: X HANDLE
                                            - Other contact: OTHER CONTACT
                                            - UrlCheck: RELATED/UNRELATED/ERROR
                                            - XCheckL RELATED/UNRELATED/ERROR
                                            - Email: the email generated addressed from the user comapny to the client
                    
                    Ensure that the email is comprehensive and not brief, as users will edit it to their liking. What is important is that
                    it contains an abundant amount of information tailored towards the client company
                    
                    ENSURE that the output is a valid JSON string without any additional formatting or characters e.g.  wrapped in Markdown code block syntax (``` ``json ```) .
                    """,
                    agent = email_generator,
                    tools = [ScrapeWebsiteTool()],
                    output_pydantic = result
                )
            ]
        )
        self.logger.info("Crew setup completed")
        return crew
    
    def read_csv_in_chunks(self,chunk_size: int = 1) -> Generator[pd.DataFrame, None, None]:
        processed_chunks = []
        for chunk in pd.read_csv(self.csv_path,chunksize = chunk_size):
            chunk_data = chunk.to_string(index=False)  # Convert DataFrame to string without index
            chunk_data = chunk_data.replace(" ", "")  # Remove all spaces
            chunk_data = chunk_data.replace("\n", "")
            chunk_data = chunk_data.replace("NaN"," ")

            processed_chunks.append(chunk_data)
        return processed_chunks