import requests
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin, urlparse

def get_wikipedia_article_links(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = bs(response.text, 'html.parser')
        links = []
        exclude = ['/wiki/Special:','/wiki/Help:','/wiki/Template:','/wiki/Talk:','/wiki/Category:','/wiki/File:']
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('/wiki/') and not any(href.startswith(prefix) for prefix in exclude):
                full_url = urljoin(url, href)
                links.append(full_url)
        return set(links)

    except Exception as f:
        print(f"An error occurred: {f}")
        return []

if __name__ == "__main__":
    wikipedia_url = input("Enter the URL of the Wikipedia page: ")
    links = get_wikipedia_article_links(wikipedia_url)
    print("Extracted Wikipedia Article Links:")
    print(len(links))
    for link in links:
        print(link)
