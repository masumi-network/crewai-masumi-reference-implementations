from crewai.tools import BaseTool
from dotenv import load_dotenv
import http.client
import json
import os

load_dotenv()

class CrunchbaseSearch(BaseTool):
    name: str = "contact finder"
    description: str = "Search the the prompt for a list of companies"

    def _run(self, domain: str,canonical:str,prompt:str) -> list[dict]:

        conn = http.client.HTTPSConnection("google.serper.dev")

      
        payload = json.dumps({
        "q": f"{domain} {canonical} {prompt} \"contact\" \"email\" site:crunchbase.com",
        "num": 10})

        headers = {
        'X-API-KEY': os.getenv("SERPER_API_KEY"),
        'Content-Type': 'application/json'
        }
        conn.request("POST", "/search", payload, headers)
        res = conn.getresponse()
        data = res.read()


        result = json.loads(data.decode("utf-8"))
        snippets = [item.get("snippet", "") for item in result.get("organic", [])]

        return snippets

        """
        tool = SerperDevTool(
            location = country,
            n_results= 100,
        )

        


        search_query =f"{url} (\"About Us\" OR \"Our Company\" OR \"Contact Us\" ) site:*.com -site:forbes.com -site:nytimes.com -site:mckinsey.com -site:cnn.com -site:medium.com -site:linkedin.com -site:twitter.com -site:facebook.com -site:youtube.com -site:reddit.com -site:quora.com -inurl:blog -inurl:article -inurl:insights"

        result = tool.run(search_query=search_query)
        return result
        """