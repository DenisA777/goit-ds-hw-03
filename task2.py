import requests
from bs4 import BeautifulSoup
import json
from pymongo import MongoClient


MONGODB_URI = "mongodb+srv://mongo_power:fodsom-3dyjny-dezqaF@cluster0.yzdglvd.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DATABASE_NAME = "quotes_db"
AUTHORS_COLLECTION = "authors"
QUOTES_COLLECTION = "quotes"


def scrape_quotes_and_authors(base_url="http://quotes.toscrape.com"):
    quotes = []
    authors = {}
    next_page = "/"

    while next_page:
        resp = requests.get(base_url + next_page)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        for quote_block in soup.select(".quote"):
            text = quote_block.select_one(".text").get_text(strip=True)
            author_name = quote_block.select_one(".author").get_text(strip=True)
            tags = [tag.get_text(strip=True) for tag in quote_block.select(".tag")]

            quotes.append({
                "quote": text,
                "author": author_name,
                "tags": tags
            })

            if author_name not in authors:
                author_link = quote_block.select_one("a[href*='/author']")["href"]
                authors[author_name] = scrape_author_details(base_url + author_link)

        next_btn = soup.select_one("li.next > a")
        next_page = next_btn["href"] if next_btn else None

    return quotes, list(authors.values())


def scrape_author_details(author_url):
    resp = requests.get(author_url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    fullname = soup.select_one("h3.author-title").get_text(strip=True)
    born_date = soup.select_one("span.author-born-date").get_text(strip=True)
    born_location = soup.select_one("span.author-born-location").get_text(strip=True)
    description = soup.select_one("div.author-description").get_text(strip=True)

    return {
        "fullname": fullname,
        "born_date": born_date,
        "born_location": born_location,
        "description": description
    }


def save_to_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_into_mongodb(quotes_file="quotes.json", authors_file="authors.json"):
    client = MongoClient(MONGODB_URI)
    db = client[DATABASE_NAME]

    if AUTHORS_COLLECTION in db.list_collection_names():
        db.drop_collection(AUTHORS_COLLECTION)
    if QUOTES_COLLECTION in db.list_collection_names():
        db.drop_collection(QUOTES_COLLECTION)

    with open(authors_file, "r", encoding="utf-8") as f:
        authors_data = json.load(f)
    with open(quotes_file, "r", encoding="utf-8") as f:
        quotes_data = json.load(f)

    db[AUTHORS_COLLECTION].insert_many(authors_data)
    db[QUOTES_COLLECTION].insert_many(quotes_data)

    print(f"Inserted {len(authors_data)} authors and {len(quotes_data)} quotes into MongoDB.")


if __name__ == "__main__":
    print("Scraping quotes and authors...")
    quotes_list, authors_list = scrape_quotes_and_authors()

    print("Saving to quotes.json and authors.json...")
    save_to_json(quotes_list, "quotes.json")
    save_to_json(authors_list, "authors.json")

    print("Loading data into MongoDB Atlas...")
    load_into_mongodb()
    print("Done!")