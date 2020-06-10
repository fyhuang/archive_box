import argparse

from bs4 import BeautifulSoup
import requests

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('url')
    args = parser.parse_args()

    response = requests.get(args.url)
    soup = BeautifulSoup(response.text, features="html.parser")

    #print(soup.title.string)

    #print(soup.find(class_="abstractSection").p.string)

    #keywords = set()
    #org_chart = soup.find("ol", class_="organizational-chart")
    #for li in org_chart.find_all("li"):
    #    keywords.add(li.a.string)

    pub_title = soup.find(class_="epub-section__title").string
    print(pub_title)

if __name__ == "__main__":
    main()
