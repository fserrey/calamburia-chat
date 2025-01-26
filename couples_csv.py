import requests
from bs4 import BeautifulSoup
import time
import csv


def scrape_couples_csv():
    base_url = "https://reinodecalamburia.com/"
    # Replace with the actual URL that holds <div class="eael-grid-post-holder-inner">
    page_with_couples = base_url + "conoce-las-parejas/"

    response = requests.get(page_with_couples)
    if response.status_code != 200:
        print(f"Error fetching {page_with_couples}. Status = {response.status_code}")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    # Find the relevant divs
    post_divs = soup.find_all("div", class_="eael-grid-post-holder-inner")

    all_couples_data = []

    for div_item in post_divs:
        overlay_div = div_item.find("div", class_="eael-entry-overlay")
        if not overlay_div:
            continue

        link_tag = overlay_div.find("a", href=True)
        if not link_tag:
            continue

        url = link_tag["href"]
        if url.startswith("/"):
            url = base_url.rstrip("/") + url

        print(f"Fetching link: {url}")
        page_resp = requests.get(url)
        if page_resp.status_code != 200:
            print(f"  -> Could not fetch {url}, status={page_resp.status_code}")
            continue

        tale_soup = BeautifulSoup(page_resp.text, "html.parser")

        # Grab the main content (WordPress often uses "div.entry-content")
        content_div = tale_soup.find("div", class_="entry-content")
        if not content_div:
            content_text = tale_soup.get_text(separator="\n")
        else:
            paragraphs = content_div.find_all("p")
            content_text = "\n\n".join(p.get_text() for p in paragraphs)

        # Optionally capture a title from <h1 class="entry-title">
        title_tag = tale_soup.find("h1", class_="entry-title")
        if title_tag:
            page_title = title_tag.get_text(strip=True)
        else:
            page_title = url  # fallback if no <h1>

        all_couples_data.append({
            "couple_title": page_title,
            "couple_link": url,
            "couple_text_info": content_text
        })

        time.sleep(1)  # optional delay

    # Write the data to a CSV file
    output_csv = "calamburia_couples.csv"
    with open(output_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["couple_title", "couple_link", "couple_text_info"]
        )
        # Write header row once
        writer.writeheader()
        # Write each couple’s data as a row
        for item in all_couples_data:
            writer.writerow(item)

    print(f"Done! Wrote {len(all_couples_data)} rows to '{output_csv}'.")


if __name__ == "__main__":
    scrape_couples_csv()
