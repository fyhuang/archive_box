import argparse
import urllib.parse

from bs4 import BeautifulSoup
import requests

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('cid')
    parser.add_argument('url')
    parser.add_argument('--abox', default='http://localhost:8123')
    args = parser.parse_args()

    response = requests.get(args.url)
    soup = BeautifulSoup(response.text, features="html.parser")

    # populate document with information from page
    keywords = set()
    org_chart = soup.find("ol", class_="organizational-chart")
    for li in org_chart.find_all("li"):
        keywords.add(li.a.string)

    pdf_link_raw = soup.find("a", class_="btn red", title="PDF").get("href")

    doc_params = {
        "source": urllib.parse.urljoin(args.url, pdf_link_raw),
        "title": soup.title.string,
        "tags": list(keywords),
        "description": soup.find(class_="abstractSection").p.string,
        "metadata": {
            "publication": soup.find(class_="epub-section__title").string,
        },
    }

    api_url = "{}/api/create_document/{}".format(args.abox, args.cid)
    requests.post(api_url, json=doc_params)

if __name__ == "__main__":
    main()
