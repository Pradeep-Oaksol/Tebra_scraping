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
MAX_CONCURRENT_REQUESTS = 10  # Control concurrent requests for efficiency


async def fetch_page(client, url):
    """Fetch a webpage asynchronously with error handling."""
    try:
        response = await client.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.text
    except httpx.RequestError as e:
        print(f"Failed to fetch {url}: {e}")
        return None


async def fetch_provider_details(client, provider_url):
    """Extract phone numbers and addresses from provider page."""
    html = await fetch_page(client, provider_url)
    if not html:
        return {"phone": "N/A", "addresses": ["N/A"]}

    tree = HTMLParser(html)
    
    # Extract phone numbers
    phone_numbers = [btn.attributes.get("data-phone", "N/A") for btn in tree.css("button[data-phone]")]
    phone_numbers = phone_numbers if phone_numbers else ["N/A"]
    
    # Extract addresses
    addresses = [addr.text(strip=True) for addr in tree.css(".practice-address")]
    addresses = addresses if addresses else ["N/A"]

    return {"phone": phone_numbers, "addresses": addresses}


async def extract_providers_from_search(html):
    """Extract provider data from search results."""
    tree = HTMLParser(html)
    providers = []

    for provider in tree.css("article.search-results__providers-provider"):
        try:
            name = provider.css_first(".provider-name").text(strip=True) if provider.css_first(".provider-name") else "N/A"
            company = provider.css_first(".provider-specialty").text(strip=True) if provider.css_first(".provider-specialty") else "N/A"
            website_tag = provider.css_first("a.article-link")
            website = website_tag.attributes.get("href", "N/A") if website_tag else "N/A"
            
            if website != "N/A" and not website.startswith("http"):
                website = urljoin(BASE_URL, website)

            providers.append({
                "Provider Name": name,
                "Company Name": company,
                "Website Link": website
            })
        except Exception as e:
            print(f"Error extracting provider info: {e}")

    return providers


async def main():
    """Main async function to scrape all data efficiently."""
    all_providers = []
    
    async with httpx.AsyncClient(limits=httpx.Limits(max_connections=MAX_CONCURRENT_REQUESTS)) as client:
        # Fetch all search pages in parallel
        search_tasks = [fetch_page(client, BASE_URL.format(start)) for start in range(0, TOTAL_PROVIDERS, PER_PAGE)]
        search_results = await asyncio.gather(*search_tasks)

        # Extract providers from search pages
        provider_list = []
        for html in search_results:
            if html:
                provider_list.extend(await extract_providers_from_search(html))

        print(f"Total providers found: {len(provider_list)}")

        # Fetch details (phone + addresses) for each provider concurrently
        detail_tasks = [fetch_provider_details(client, provider["Website Link"]) for provider in provider_list]
        details_results = await asyncio.gather(*detail_tasks)

        # Merge details into provider data
        for provider, details in zip(provider_list, details_results):
            provider["Phone Number"] = details["phone"]
            provider["Location Addresses"] = details["addresses"]
            provider["Number of Locations"] = len(details["addresses"]) if isinstance(details["addresses"], list) else 0
            all_providers.append(provider)

    # Save data to JSON
    with open("providers_data.json", "w", encoding="utf-8") as file:
        json.dump(all_providers, file, indent=4, ensure_ascii=False)

    print(f"Total Providers Scraped: {len(all_providers)} (Saved to 'providers_data.json')")


if __name__ == "__main__":
    asyncio.run(main())
