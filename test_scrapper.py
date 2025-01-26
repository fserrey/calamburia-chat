import requests
from bs4 import BeautifulSoup
import re
import time

def scrape_calamburia():
    start_url = "https://reinodecalamburia.com/todos-los-relatos/"
    base_url = "https://reinodecalamburia.com"

    # 1. Fetch the main "Todos los relatos" page
    resp = requests.get(start_url)
    if resp.status_code != 200:
        print(f"Error fetching {start_url}. Status code: {resp.status_code}")
        return

    soup = BeautifulSoup(resp.text, "html.parser")

    # 2. Find all <a class="eael-grid-post-link" ...> links
    link_tags = soup.find_all("a", class_="eael-grid-post-link")

    # This list will store tuples of (tale_number, link_text, link_url)
    tales = []

    # A helper function to extract the number from strings like "227 – LA NUEVA TRIARQUÍA" or "69. LA PUERTA DEL ESTE"
    def extract_number(title_text):
        # Match one or more digits at the very start of the text
        match = re.match(r"^(\d+)", title_text.strip())
        if match:
            return int(match.group(1))
        return None

    for link in link_tags:
        link_text = link.get_text(strip=True)  # e.g. "227 – LA NUEVA TRIARQUÍA"
        tale_num = extract_number(link_text)
        if tale_num is None:
            print(f"WARNING: Could not parse a tale number from '{link_text}'")
            continue
        
        # Make sure to get an absolute URL
        href = link["href"]
        if href.startswith("/"):
            href = base_url + href
        
        tales.append((tale_num, link_text, href))

    # 3. Sort tales by the parsed number so they appear in the correct order
    tales.sort(key=lambda x: x[0])

    all_tales_data = []

    # 4. Visit each tale link and scrape the content
    for (tale_num, tale_title, tale_url) in tales:
        print(f"Scraping tale #{tale_num}: {tale_title} ({tale_url})")
        r_tale = requests.get(tale_url)
        if r_tale.status_code != 200:
            print(f"  -> Failed to fetch {tale_url} [status={r_tale.status_code}]")
            continue
        
        tale_soup = BeautifulSoup(r_tale.text, "html.parser")
        
        # Extract the main text of the tale.
        # Often it's in <div class="entry-content"> for WordPress sites.
        content_div = tale_soup.find("div", class_="entry-content")
        if content_div:
            paragraphs = content_div.find_all("p")
            # Join all paragraph texts with double newlines
            tale_text = "\n\n".join(p.get_text() for p in paragraphs)
        else:
            # Fallback: just grab all page text
            tale_text = tale_soup.get_text()
        
        all_tales_data.append((tale_num, tale_title, tale_text))

        # Optional: be polite and avoid hammering the server
        time.sleep(1)

    # 5. Save everything into a single text file
    output_filename = "calamburia_ordered_tales.txt"
    with open(output_filename, "w", encoding="utf-8") as f:
        for (tale_num, tale_title, tale_text) in all_tales_data:
            f.write(f"{tale_num} - {tale_title}\n\n")
            f.write(tale_text)
            f.write("\n\n" + "="*60 + "\n\n")
    
    print(f"Done! Wrote {len(all_tales_data)} tales to '{output_filename}'.")

if __name__ == "__main__":
    scrape_calamburia()
