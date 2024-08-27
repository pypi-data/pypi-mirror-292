from fastai.vision.all import Path
from .search_duckduckgo import searchDDG
from .search_google import searchGoogle
from .search_bing import searchBing
from time import sleep
import logging

logging.disable(logging.CRITICAL)

def searchWeb(term, path, max_images = 30):
    print("Fetching Images from Duck Duck Go, Google and Bing.")
    img_path = Path.cwd() / path
    dest = img_path
    dest.mkdir(exist_ok=True, parents=True)
    local_path = Path(path)
    old_items = len([file for file in local_path.iterdir() if file.is_file()])
    searchGoogle(term, path, max_images=max_images)
    sleep(10)
    searchBing(term, path, max_images=max_images)
    sleep(10)
    searchDDG(term, path, max_images=max_images)
    new_items = len([file for file in local_path.iterdir() if file.is_file()])
    print(f"ImageEngine has downloaded {abs(old_items - new_items)} new images")


def search_web_entry():
    import argparse
    parser = argparse.ArgumentParser(description='Search for images on the web.')
    parser.add_argument('term', type=str, help='Search term')
    parser.add_argument('path', type=str, help='Directory to save images')
    parser.add_argument('--max_images', type=int, default=10, help='Maximum number of images to download')
    args = parser.parse_args()
    searchWeb(term=args.term, path=args.path, max_images=args.max_images)
