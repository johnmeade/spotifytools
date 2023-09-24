import requests
from tqdm import tqdm
from bs4 import BeautifulSoup


def new_releases(pbar=False, pages=5):
    releases = []
    pages = range(1, pages+1)
    if pbar:
        pages = tqdm(pages)
    for i in pages:
        resp = requests.get(f'https://www.albumoftheyear.org/releases/{i}/')
        soup = BeautifulSoup(resp.content, 'html.parser')
        blocks = soup.find_all(class_='albumBlock')
        for block in blocks:
            try:
                releases += [dict(
                    artist=str(block.find(class_='artistTitle').string),
                    album=str(block.find(class_='albumTitle').string),
                    date=str(block.find(class_='date').string),
                )]
            except:
                pass
    return releases
