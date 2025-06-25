from crewai.tools import BaseTool
from dotenv import load_dotenv
import http.client
import json
import os

load_dotenv()

class Scraper(BaseTool):
    name: str = "contact finder"
    description: str = "Search the the prompt for a list of companies"

    def _run(self, url: str,country: str,domain_list:list,after:str,before:str) -> list[dict]:

        conn = http.client.HTTPSConnection("google.serper.dev")
        domains = ""
        for domain in domain_list:
            domains += str(domain)
            if domain != domain_list[-1]:
                domains += " OR "
        payload = json.dumps({
        "q": f"{url} (\"About Us\" OR \"Our Company\") site:*{domains} -site:forbes.com -site:nytimes.com -site:mckinsey.com -site:cnn.com -site:medium.com -site:linkedin.com -site:twitter.com -site:facebook.com -site:youtube.com -site:reddit.com -site:quora.com -inurl:blog -inurl:blogs -inurl:article -inurl:insights after:{after} before:{before}",
        "gl": country,
        "num": 100})

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

        """
        tool = SerperDevTool(
            location = country,
            n_results= 100,
        )

        


        search_query =f"{url} (\"About Us\" OR \"Our Company\" OR \"Contact Us\" ) site:*.com -site:forbes.com -site:nytimes.com -site:mckinsey.com -site:cnn.com -site:medium.com -site:linkedin.com -site:twitter.com -site:facebook.com -site:youtube.com -site:reddit.com -site:quora.com -inurl:blog -inurl:article -inurl:insights"

        result = tool.run(search_query=search_query)
        return result
        """