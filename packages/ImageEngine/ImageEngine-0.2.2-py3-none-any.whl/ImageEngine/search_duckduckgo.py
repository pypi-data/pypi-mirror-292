from duckduckgo_search import DDGS
from fastai.vision.all import Path
from time import sleep
import os
import requests
from PIL import Image
from io import BytesIO

def download_images_manually(path, urls):
    if not os.path.exists(path):
        os.makedirs(path)
    
    for i, url in enumerate(urls):
        try:
            response = requests.get(url)
            img = Image.open(BytesIO(response.content))
            img.save(os.path.join(path, f'image_{i+1}.jpg'))
        except Exception as e:
            continue
            print(f"Error downloading {url}: {e}")

def searchDDG(term, path, max_images=30):
    print(f"Searching Images of '{term}' from Duck Duck Go...")
    with DDGS() as ddgs:
        search_results = ddgs.images(keywords=term, max_results=max_images)
        search_images = [search_result['image'] for search_result in search_results]
        img_path = Path.cwd() / path
        dest = img_path
        dest.mkdir(exist_ok=True, parents=True)
        download_images_manually(dest, urls=search_images)


def search_ddg_entry():
    import argparse
    parser = argparse.ArgumentParser(description='Search for images on DuckDuckGo.')
    parser.add_argument('term', type=str, help='Search term')
    parser.add_argument('path', type=str, help='Directory to save images')
    parser.add_argument('--max_images', type=int, default=30, help='Maximum number of images to download')
    args = parser.parse_args()
    searchDDG(term=args.term, path=args.path, max_images=args.max_images)