from crewai.tools import BaseTool
from dotenv import load_dotenv
import http.client
import json
import os

load_dotenv()

class ContactScraper(BaseTool):
    name: str = "contact finder"
    description: str = "Search the the prompt for a list of companies"

    def _run(self, url:str) -> list[dict]:

        conn = http.client.HTTPSConnection("google.serper.dev")
     
        payload = json.dumps({
        "q": f"{url} \"contact\" \"email\"",
        "num": 10})

        headers = {
        'X-API-KEY': os.getenv("SERPER_API_KEY"),
        'Content-Type': 'application/json'
        }
        conn.request("POST", "/search", payload, headers)
        res = conn.getresponse()
        data = res.read()


        result = json.loads(data.decode("utf-8"))
        links = [item['link'] for item in result.get("organic", [])]

        return links
