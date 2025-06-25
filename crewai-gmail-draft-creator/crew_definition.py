from crewai import Agent, Crew, Task
from logging_config import get_logger
from gmail_tool import Draft_tool

class ResearchCrew:
    def __init__(self, verbose=True, logger=None):
        self.verbose = verbose
        self.logger = logger or get_logger(__name__)
        self.crew = self.create_crew()
        self.logger.info("ResearchCrew initialized")

    def create_crew(self):
        self.logger.info("Creating research crew with agents")
        
        draft_creator = Agent(
            role='Gmail Draft Creator',
            goal='Create Gmail Drafts to contacts from input',
            backstory='Expert at Reading and identifying contact info and drafts, then copying those drafts to new gmail drafts to send to contacts',
            verbose=self.verbose
        )


        self.logger.info("Created research and writer agents")

        crew = Crew(
            agents=[draft_creator],
            tasks=[
                Task(
                    description='Analyze {text} and create a gmail draft to the recipient company, the draft body being the pre-generated email in the input which is to be identified (will most likely be after a header like "Email: "), the "contact" and "body" fields of the tool being the provided email address and email bodies respectively',
                    expected_output='A Gmail draft containing the provided email body addressed to the recipient',
                    agent=draft_creator,
                    tools=[Draft_tool()]
                )

            ]
        )
        self.logger.info("Crew setup completed")
        return crew