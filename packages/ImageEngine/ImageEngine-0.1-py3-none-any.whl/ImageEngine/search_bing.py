from icrawler.builtin import BingImageCrawler
import logging

logging.disable(logging.CRITICAL)

def searchBing(term, path, max_images = 30):
    print(f"Searching Images of {term} from Bing...")
    bing_crawler = BingImageCrawler(downloader_threads=4, storage={'root_dir': r'' + path +''})
    bing_crawler.crawl(keyword=term, filters=None, offset=0, max_num=max_images)


def search_bing_entry():
    import argparse
    parser = argparse.ArgumentParser(description='Search for images on Bing.')
    parser.add_argument('term', type=str, help='Search term')
    parser.add_argument('path', type=str, help='Directory to save images')
    parser.add_argument('--max_images', type=int, default=10, help='Maximum number of images to download')
    args = parser.parse_args()
    searchBing(term=args.term, path=args.path, max_images=args.max_images)