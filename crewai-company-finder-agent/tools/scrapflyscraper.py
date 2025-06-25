from crewai.tools import BaseTool
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import os
import re

load_dotenv()
key = os.getenv("SCRAPE_KEY")

class WebScraper(BaseTool):
    name: str = "scrapfly content extractor"
    description: str = "Extract all visible, readable text from a web page using Scrapfly."

    def _run(self, url: str) -> str:
        # Compose the Scrapfly API URL
        api_url = f"https://api.scrapfly.io/scrape?url={url}&country=us&render_js=true&key={key}"
        response = requests.get(api_url)
        data = response.json()
        html = data.get('result', {}).get('content', '')

        # 1. Extract all email addresses from the raw HTML
        email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        emails = set(re.findall(email_pattern, html))

        soup = BeautifulSoup(html, 'html.parser')

        # 2. Extract canonical URL
        canonical_url = ""
        canonical_tag = soup.find('link', rel='canonical')
        if canonical_tag and canonical_tag.get('href'):
            canonical_url = canonical_tag.get('href')

        # 3. Remove script, style, and other non-visible elements
        for tag in soup(['script', 'style', 'noscript', 'header', 'footer', 'svg', 'form', 'nav', 'meta', 'link']):
            tag.decompose()

        # 4. Get all visible text
        text = soup.get_text(separator='\n', strip=True)

        # 5. Clean up excessive blank lines
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        clean_text = '\n'.join(lines)

        # 6. Add canonical URL at the top if found
        if canonical_url:
            clean_text = f"[Canonical URL: {canonical_url}]\n\n{clean_text}"

        # 7. Append found emails at the end (or handle as you wish)
        if emails:
            clean_text += "\n\n[Extracted Emails]\n" + "\n".join(sorted(emails))

        return clean_text