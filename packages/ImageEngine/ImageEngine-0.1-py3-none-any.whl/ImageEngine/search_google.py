from icrawler.builtin import GoogleImageCrawler
import logging

logging.disable(logging.CRITICAL)

def searchGoogle(term, path, max_images = 30):
    print(f"Searching Images of {term} from Google...")
    google_Crawler = GoogleImageCrawler(storage = {'root_dir': r''+ path +''})
    google_Crawler.crawl(keyword = term, max_num = max_images)

def search_google_entry():
    import argparse
    parser = argparse.ArgumentParser(description='Search for images on Google.')
    parser.add_argument('term', type=str, help='Search term')
    parser.add_argument('path', type=str, help='Directory to save images')
    parser.add_argument('--max_images', type=int, default=10, help='Maximum number of images to download')
    args = parser.parse_args()
    searchGoogle(term=args.term, path=args.path, max_images=args.max_images)