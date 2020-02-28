import bs4
import queue
from urllib import request
from urllib import error
import pandas as pd
import os, errno
from urllib import parse
from urllib.request import Request
import urllib.robotparser as robotparser
import time

class WebCrawler():

    def __init__(self, seed:str, limit:int = 100):
        self.seed = seed
        self.nodes = queue.Queue()
        self.nodes.put(self.seed)
        self.visited = set()
        self.limit = limit
        self.count = 0

    def searchBFS(self, output_dir:str):
        """This method extract the pages"""

        # pandas DataFrame to store real url and document where html is stored
        url_df = pd.DataFrame(columns=('document', 'real_url'), dtype='str')

        # pertinent os operations to create the directory to store
        if not os.path.exists(output_dir):
            try:
                os.mkdir(output_dir)
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        # while the number of visited nodes is less than the limit, search for more html pages
        while len(self.visited) < self.limit:
            # get the first url in the queue
            url = self.nodes.get()

            # Parse the robots.txt of the web server
            parsed_url = parse.urlparse(url)
            robots_url = parsed_url.scheme+'://'+parsed_url.netloc+'/robots.txt'
            rfp = robotparser.RobotFileParser(robots_url)
            rfp.read()

            # if page cannot be visited because it says so in robots.txt
            # continue and print message
            if not rfp.can_fetch('custom', url):
                print('Cannot visit', url, 'because of robots.txt')
                continue

            # if robots.txt has a crawl delay
            # for security sleep that time
            if rfp.crawl_delay('custom'):
                delay = rfp.crawl_delay('custom')
                print('Delayed', delay)
                time.sleep(delay)

            # if url already visited
            # continue
            if url in self.visited:
                print('visited', url)
                continue

            # try to download the html
            try:
                # build request & get response
                req = Request(url)
                req.add_header('User-agent', 'custom')
                response = request.urlopen(req)
                # get the content type
                try:
                    info = dict(response.getheaders())['Content-Type'].split(';')
                    content_type = info[0].strip()
                except KeyError:
                    print('Continue no content type')
                    continue
                print('Visiting', url, content_type, content_type == 'text/html')
                # if the content is not html, discard page and cotinue crawling
                if not content_type == 'text/html':
                    continue
                # try to get coding or set utf-8
                try:
                    encoding = info[1].strip().split('=')[-1]
                except IndexError:
                    encoding = 'utf-8'

                # get the content in proper encoding and save it in pertinent place
                content = response.read().decode(encoding, 'replace')
                file = open(output_dir +'/document' + str(self.count) + '.html', 'w+')
                file.writelines(content)
                file.close()
                file = open(output_dir +'/document' + str(self.count) + '.html', 'r')
                soup = bs4.BeautifulSoup(file, 'html.parser')

            # catch any unexpected HTTPError
            except error.HTTPError:
                print('Error', error.HTTPError.info(), 'retrieving data from', str(url))
                continue
            # save the pair <url,document> in pandas df
            url_df = url_df.append({'document':'document'+str(self.count)+'.html','real_url':url}, ignore_index=True)
            #url_df.append(('document'+str(self.count)+'.html', url))
            self.visited.add(url)
            self.count += 1

            # get all links in current page
            for link in soup.find_all('a'):
                if link.get('href'):
                    if not link.get('href').startswith('https'):
                        continue
                    href = link.get('href')
                    # print(href)
                    self.nodes.put(href)
            # Download html
            url_df.to_csv(output_dir+'/url_repository.csv', index=False)
