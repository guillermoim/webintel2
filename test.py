from crawler import WebCrawler
import pandas

if __name__ == '__main__':
    wc = WebCrawler('https://www.youtube.com/watch?v=wfbEoq634ZY')
    wc.searchBFS('YouTube')

