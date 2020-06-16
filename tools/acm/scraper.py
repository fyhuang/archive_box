import argparse
import urllib.parse
from typing import Dict

from bs4 import BeautifulSoup # type: ignore
import requests

def scrape_one(args, url: str) -> Dict:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, features="html.parser")

    # populate document with information from page
    keywords = set()
    org_chart = soup.find("ol", class_="organizational-chart")
    if org_chart is not None:
        for li in org_chart.find_all("li"):
            keywords.add(li.a.string)
        assert len(keywords) > 0

    pdf_link_raw = soup.find("a", class_="btn red", title="PDF").get("href")
    assert len(pdf_link_raw) > 0

    pub_name = soup.find(class_="epub-section__title").string
    assert len(pub_name) > 0
    abstract_element = soup.find(class_="abstractSection")
    abstract = ' '.join(abstract_element.stripped_strings)
    assert len(abstract) > 0

    doc_params = {
        "needs_review": False, # we already extracted most of the info from the webpage
        "source": urllib.parse.urljoin(url, pdf_link_raw),
        "title": soup.title.string,
        "tags": list(keywords),
        "description": "{}\n\n{}".format(pub_name, abstract),
        "metadata": {
            "publication": pub_name,
        },
    }

    api_url = "{}/api/create_document/{}".format(args.abox, args.cid)
    response = requests.post(api_url, json=doc_params)
    return response.json()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('cid')
    parser.add_argument('urls', nargs='+')
    parser.add_argument('--abox', default='http://localhost:8123')
    args = parser.parse_args()

    for url in args.urls:
        try:
            status = scrape_one(args, url)
            if "doc_id" in status:
                print("{} -> {}".format(url, status["doc_id"]))
            else:
                print("{} -> (duplicate)".format(url))
        except:
            print("Failed: {}".format(url))
            raise

if __name__ == "__main__":
    main()
