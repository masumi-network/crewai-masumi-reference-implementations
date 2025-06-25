from crewai.tools import BaseTool
from dotenv import load_dotenv
import os.path

import base64
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose"
]

class Draft_tool(BaseTool):
    name: str = "gmail draft creator"
    description: str = "Create drafts for listed contacts"

    def _run(self, contact: str, body: str) -> list[dict]:
        """Creates a Gmail draft with the specified contact and body."""
        creds = None
        
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open("token.json", "w") as token:
                    token.write(creds.to_json())

        def gmail_create_draft(creds,contact:str,body:str):
            
            try:
                # create gmail api client
                service = build("gmail", "v1", credentials=creds)

                message = EmailMessage()
                message.set_content(body)

                message["To"] = contact
                message["From"] = "gduser2@workspacesamples.dev"
                message["Subject"] = "Automated draft"

                # encoded message
                encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

                create_message = {"message": {"raw": encoded_message}}
                # pylint: disable=E1101
                draft = (
                    service.users()
                    .drafts()
                    .create(userId="me", body=create_message)
                    .execute()
                )

                print(f'Draft id: {draft["id"]}\nDraft message: {draft["message"]}')

            except HttpError as error:
                print(f"An error occurred: {error}")
                draft = None
            return draft
        
        draft = gmail_create_draft(creds, contact, body)
        return draft

        
