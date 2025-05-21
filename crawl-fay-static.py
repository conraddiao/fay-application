import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import time

# Target site and pattern
base_url = "https://www.faynutrition.com/find"
# links to appointment pages
#  target_pattern = re.compile(r"https://provider\.faynutrition\.com/appointments/[\w\-]+", re.IGNORECASE)

# links to dietitian pages
target_pattern = re.compile(r"/dietitians/.*?", re.IGNORECASE)

# Paths to ignore
ignored_paths = ["/dietitians", "/specialties", "/insurance", "/modalities"]

# Setup
visited = set()
to_visit = [base_url]
found_links = set()

headers = {
    "User-Agent": "Mozilla/5.0 (compatible; LinkScraper/1.0)"
}

def should_ignore(url):
    path = urlparse(url).path
    return any(path.startswith(ignored) for ignored in ignored_paths)

# Crawl loop
while to_visit:
    current_url = to_visit.pop(0)
    if current_url in visited or should_ignore(current_url):
        continue
    visited.add(current_url)

    print(f"\nVisiting: {current_url}")
    try:
        response = requests.get(current_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
    
        match_count = 0
        # print(soup)

        # Check for appointment links
        for a in soup.find_all("a", href=True):
            href = a["href"]
            # Check if it's a target appointment link
            if target_pattern.match(href):
                print(href)
                if href not in found_links:
                    found_links.add(href)
                    match_count += 1

            # Queue internal links for crawling
            full_url = urljoin(current_url, href)
            if full_url.startswith(base_url) and full_url not in visited and not should_ignore(full_url):
                to_visit.append(full_url)

        print(f"  ➤ Found {match_count} matching link(s).")
        time.sleep(1)

    except Exception as e:
        print(f"  Error: {e}")

# Final results
print("\n🔗 Total Unique Links Found:")
for link in found_links:
    print(link)
print(f"\n✅ Total unique matches: {len(found_links)}")

