import requests
from bs4 import BeautifulSoup
import time


def scrape_couples():
    # 1. Base URLs
    main_url = "https://reinodecalamburia.com/"  # Update if needed
    page_with_couples = main_url + "conoce-las-parejas/"
    # ^ Replace with the actual URL that has <div class="eael-grid-post-holder-inner">

    # 2. Download the main listing page
    response = requests.get(page_with_couples)
    if response.status_code != 200:
        print(f"Error fetching {page_with_couples}. Status = {response.status_code}")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    # 3. Find all the relevant divs
    #    We look for: <div class="eael-grid-post-holder-inner">
    #    and inside it -> <div class="eael-entry-overlay"> -> <a href="...">
    post_divs = soup.find_all("div", class_="eael-grid-post-holder-inner")

    # We'll store each (link_url, link_text) or (link_url, full_page_text)
    all_couples_data = []

    for div_item in post_divs:
        # Find the overlay that has the <a> with the URL
        overlay_div = div_item.find("div", class_="eael-entry-overlay")
        if not overlay_div:
            continue

        link_tag = overlay_div.find("a", href=True)
        if not link_tag:
            continue

        url = link_tag["href"]
        # Make the URL absolute if it's relative
        if url.startswith("/"):
            url = main_url.rstrip("/") + url

        print(f"Fetching link: {url}")
        # 4. Fetch the linked page
        page_resp = requests.get(url)
        if page_resp.status_code != 200:
            print(f"  -> Could not fetch {url}, status={page_resp.status_code}")
            continue

        tale_soup = BeautifulSoup(page_resp.text, "html.parser")

        # 5. Extract the text content from each linked page.
        #    Often in WordPress, it's inside <div class="entry-content"> or similar
        content_div = tale_soup.find("div", class_="entry-content")
        if not content_div:
            # If not found, fallback to entire page text
            content_text = tale_soup.get_text(separator="\n")
        else:
            # Gather paragraphs or just get all text
            paragraphs = content_div.find_all("p")
            content_text = "\n\n".join(p.get_text() for p in paragraphs)

        # Possibly also grab a title from <h1 class="entry-title">
        title_tag = tale_soup.find("h1", class_="entry-title")
        if title_tag:
            page_title = title_tag.get_text(strip=True)
        else:
            # fallback or keep the url as a "title"
            page_title = url

        # Add it to our list
        all_couples_data.append({
            "title": page_title,
            "url": url,
            "text": content_text
        })

        # Optionally sleep to avoid hammering the site
        time.sleep(1)

    # 6. Write everything to a file
    output_file = "calamburia_couples.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        for item in all_couples_data:
            f.write(f"=== {item['title']} ===\n")
            f.write(f"(Source: {item['url']})\n\n")
            f.write(item['text'])
            f.write("\n\n" + ("=" * 60) + "\n\n")

    print(f"Done! Wrote {len(all_couples_data)} entries to '{output_file}'.")


if __name__ == "__main__":
    scrape_couples()
