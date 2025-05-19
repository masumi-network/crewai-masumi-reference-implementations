from crewai import Agent, Crew, Task
from logging_config import get_logger
from crewai_tools import ScrapeWebsiteTool

class ResearchCrew:
    def __init__(self, verbose=True, logger=None):
        self.verbose = verbose
        self.logger = logger or get_logger(__name__)
        self.crew = self.create_crew()
        self.logger.info("Mentor Crew initialized")

    def create_crew(self):
        self.logger.info("Creating Mentor crew with agent")
        
        mentor = Agent(
            role='Professional data analyst, website scraper and tutorial generator',
            goal="""Analyse, compare and contrast large amounts of content
                    scraped from multiple URLS, in order to generate a comprehensive, easily readable
                    and well formatted tutorial regarding programming topics.""",

            backstory="""You are a state-of-the-art data analyst and website scraper that can
                        easily scrape content from multiple urls to compare and contrast
                        the returned data with unparalleled accuracy and judgement.
                        You can use these results to fluidly write easily accessible tutorials
                        of utmost accuracy, correctness and relevance.""",
            verbose=self.verbose
        )

        self.logger.info("Created mentor and agent")

        crew = Crew(
            agents=[mentor],
            tasks=[
                Task(
                    description="""Look at the list of URLs in {urls}. If they arenot related to programming, 
                                    return: "I cannot help you with "{query}" as resources related to programming were not found"
                                    Conduct a thorough scrape of all websites from a list of given URLs using
                                    provided tools,Analyse Compare and contrast the content from the differing websites,
                                    noting parallels and differences in order to
                                    formulate a comprehensive, well-formatted and easy to understand
                                    tutorial based on {query}.
                                    
                                    If any data was quoted directly, the website 
                                    that it came from must be referenced. At the end, the URLS of all
                                    websites where the data originated from must be referenced.
                                    
                                    when scraping the websites, these guidelines MUST be followed:

                                    1). All Metadata should be ignored

                                    2). ALL website content should be analysed,
                                        regardless of length or relevance to the search query. 
                                        this is a requirement (except metadata). A different agent
                                        will interpret the output anyway

                                    3). avoid any use of asterisks (*) in the output, this is of utmost priority

                                    4) .If a website is inaccessible, completely ignore it and move
                                        onto the next one in the list
                                        
                                    5). At the end of the final output, state all URS visited and which ones
                                        were successfully scraped and which ones
                                        returned errors (if any)""",

                    expected_output=""" A well-written, fluid and comprehensive tutorial on {query} 
                                        using the input data as source material. the tutorial should be named
                                        "{query} - Tutorial". Any quoted material from the provided website scraped content
                                        should be referenced.
                                        The URLS of ALL websites where each scraped content was sourced from should be listed at the end

                                        The tutorial document should follow the following format:
                                        - Title: {query} - Tutorial
                                        - The first page should include an introduction to the topic,
                                            and a full explanation of the topic in simple terms, akin to college notes which includes 
                                            advantages, disadvantages, use cases and comparisons to similar things.

                                        - The second page should include the code. The code should be formatted in a way that is easy to understand.

                                        - The last part should include a detailed explanation of the code, and a final conclusion
                                           which includes a summary of the topic, and a list of references used to create the tutorial

                                           or if no websites are related to programming, return: "I cannot help you with "{query}" as resources related to programming were not found""",
                    agent=mentor,
                    tools=[ScrapeWebsiteTool()]
                )
            ]
        )
        self.logger.info("Crew setup completed")
        return crew