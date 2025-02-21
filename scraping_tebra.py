import httpx
import asyncio
import json
from selectolax.parser import HTMLParser
from urllib.parse import urljoin

BASE_URL = "https://www.tebra.com/care/"
SEARCH_API = "https://www.tebra.com/care/search?type=specialty&keyword={}&lookup=&start={}"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}
PER_PAGE = 20
MAX_CONCURRENT_REQUESTS = 5


async def fetch_page(client, url, semaphore):
    async with semaphore:
        try:
            response = await client.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            return response.text
        except httpx.RequestError as e:
            print(f"Failed to fetch {url}: {e}")
            return None


async def get_departments(client, semaphore):
    html = await fetch_page(client, BASE_URL, semaphore)
    if not html:
        return []

    tree = HTMLParser(html)
    departments = set()

    for dept in tree.css("a.sub-nav-toggle"):
        dept_name = dept.text(strip=True)
        if dept_name and dept_name.lower() not in ["browse", "back"]:
            departments.add(dept_name)

    departments = list(departments)
    print(f"Found {len(departments)} departments: {departments}")
    return departments


def normalize_department_name(department):
    replacements = {
        "OB-GYNs": "OB-GYN",
        "Orthopedic Surgeons": "Orthopedic Surgeon",
        "Family Physicians": "Family Physician",
        "Pediatricians": "Pediatrician",
        "Physical Therapists": "Physical Therapist",
        "Psychiatrists": "Psychiatrist",
        "Dentists": "Dentist",
        "Dermatologists": "Dermatologist",
        "Chiropractors": "Chiropractor",
        "Ophthalmologists": "Ophthalmologist",
        "Podiatrists": "Podiatrist",
        "Cardiologists": "Cardiologist",
    }
    return replacements.get(department, department)


async def extract_providers_from_search(html):
    tree = HTMLParser(html)
    providers = []

    for provider in tree.css("article.search-results__providers-provider"):
        try:
            name = provider.css_first(".provider-name").text(strip=True) if provider.css_first(".provider-name") else "N/A"
            website_tag = provider.css_first("a.article-link")
            website = website_tag.attributes.get("href", "N/A") if website_tag else "N/A"

            providers.append({
                "Provider Name": name,
                "Website Link": website
            })
        except Exception as e:
            print(f"Error extracting provider info: {e}")

    return providers


async def fetch_provider_details(client, provider_url, semaphore):
    html = await fetch_page(client, provider_url, semaphore)
    if not html:
        return {"phone": "N/A", "addresses": ["N/A"], "company": "N/A"}

    tree = HTMLParser(html)

    phone_numbers = [btn.attributes.get("data-phone", "N/A") for btn in tree.css("button[data-phone]")]
    phone_numbers = phone_numbers if phone_numbers else ["N/A"]

    addresses = [addr.text(strip=True) for addr in tree.css(".practice-address")]
    addresses = addresses if addresses else ["N/A"]

    company_element = tree.css_first("p.practice-name")
    company = company_element.text(strip=True) if company_element else "N/A"

    return {"phone": phone_numbers, "addresses": addresses, "company": company}


async def scrape_department(client, department, semaphore):
    all_providers = []
    start = 0
    normalized_department = normalize_department_name(department)

    print(f"🔍 Searching for providers in: {normalized_department}")

    while True:
        url = SEARCH_API.format(normalized_department, start)
        html = await fetch_page(client, url, semaphore)
        if not html:
            print(f"⚠️ No data found for {normalized_department} at start={start}")
            break

        provider_list = await extract_providers_from_search(html)
        if not provider_list:
            print(f"⚠️ No providers found for {normalized_department}")
            break

        print(f"✅ Found {len(provider_list)} providers for {normalized_department}")

        detail_tasks = [fetch_provider_details(client, provider["Website Link"], semaphore) for provider in provider_list]
        details_results = await asyncio.gather(*detail_tasks)

        for provider, details in zip(provider_list, details_results):
            provider["Company Name"] = details["company"]
            provider["Phone Number"] = details["phone"]
            provider["Location Addresses"] = details["addresses"]
            provider["Number of Locations"] = len(details["addresses"]) if isinstance(details["addresses"], list) else 0
            all_providers.append(provider)

        start += PER_PAGE

    return {department: all_providers}


async def main():
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    all_data = {}

    async with httpx.AsyncClient() as client:
        departments = await get_departments(client, semaphore)
        tasks = [scrape_department(client, dept, semaphore) for dept in departments]
        results = await asyncio.gather(*tasks)

    for result in results:
        all_data.update(result)

    with open("providers_data.json", "w", encoding="utf-8") as file:
        json.dump(all_data, file, indent=4, ensure_ascii=False)

    print(f"✅ Data scraping complete. Saved to 'providers_data.json'")


if __name__ == "__main__":
    asyncio.run(main())
