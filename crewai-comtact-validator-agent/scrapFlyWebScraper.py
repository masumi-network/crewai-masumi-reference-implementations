import httpx
import bs4  # beautifulsoup
from pprint import pprint

# scrape page HTML
url = "https://web-scraping.dev/product/1"
response = httpx.get(url)
assert response.status_code == 200, f"Failed to fetch {url}, got {response.status_code}"

# parse HTML
soup = bs4.BeautifulSoup(response.text, "html.parser")
product = {}
product['name'] = soup.select_one("h3.product-title").text
product['price'] = soup.select_one("span.product-price").text
product['description'] = soup.select_one("p.product-description").text
product['features'] = {}
feature_tables = soup.select(".product-features table")

for row in feature_tables[0].select("tbody tr"):
    key, value = row.select("td")
    product['features'][key.text] = value.text


print("scraped product:")
pprint(product)