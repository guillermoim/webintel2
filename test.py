from crawler import WebCrawler
import pandas

if __name__ == '__main__':
    wc = WebCrawler('https://www.reddit.com/', limit=10)
    wc.searchBFS('reddit')

