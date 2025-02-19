import httpx
import asyncio
import json
from selectolax.parser import HTMLParser
from urllib.parse import urljoin

BASE_URL = "https://www.tebra.com/care/search?neighborhood=&city=None&state=None&zip=&lat=&lng=&type=specialty&keyword=Physical+Therapist&lookup=&start={}" 

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

TOTAL_PROVIDERS = 3200
PER_PAGE = 18

async def fetch_page_data(client, start):
    url = BASE_URL.format(start)
    try:
        response = await client.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.text
    except httpx.RequestError as e:
        print(f"Failed to fetch page {start}: {e}")
        return None

def extract_provider_info(html, base_url):
    tree = HTMLParser(html)
    providers = []

    for provider in tree.css("article.search-results__providers-provider"):
        try:
            name = provider.css_first(".provider-name").text(strip=True) if provider.css_first(".provider-name") else "N/A"
            company = provider.css_first(".provider-specialty").text(strip=True) if provider.css_first(".provider-specialty") else "N/A"
            locations = provider.css(".provider-location")
            num_locations = len(locations)
            location_addresses = [loc.text(strip=True) for loc in locations] if locations else ["N/A"]
            phone = provider.css_first(".provider-phone").text(strip=True) if provider.css_first(".provider-phone") else "N/A"
            website_tag = provider.css_first("a.article-link")
            website = website_tag.attributes.get("href", "N/A") if website_tag else "N/A"
            
            if website != "N/A" and not website.startswith("http"):
                website = urljoin(base_url, website)

            providers.append({
                "Provider Name": name,
                "Company Name": company,
                "Number of Locations": num_locations,
                "Location Addresses": location_addresses,
                "Phone Number": phone,
                "Website Link": website
            })
        except Exception as e:
            print(f"Error extracting provider info: {e}")

    return providers

async def main():
    all_providers = []
    async with httpx.AsyncClient() as client:
        tasks = [fetch_page_data(client, start) for start in range(0, TOTAL_PROVIDERS, PER_PAGE)]
        results = await asyncio.gather(*tasks)

    for html in results:
        if html:
            providers = extract_provider_info(html, BASE_URL)
            if not providers:
                print("No more providers found. Scraping complete!")
                break
            all_providers.extend(providers)

    with open("providers_data.json", "w", encoding="utf-8") as file:
        json.dump(all_providers, file, indent=4, ensure_ascii=False)

    print(f"Total Providers Scraped: {len(all_providers)} (Saved to 'providers_data.json')")

asyncio.run(main())
