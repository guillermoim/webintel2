import bs4
import queue
from urllib import request
from urllib import error
import pandas as pd
import os, errno

class WebCrawler():

    def __init__(self, seed:str, limit:int = 100):
        self.seed = seed
        self.nodes = queue.Queue()
        self.nodes.put(self.seed)
        self.visited = []
        self.limit = limit
        self.count = 0

    def searchBFS(self, output_dir:str):
        """This method extract the pages"""

        url_df = pd.DataFrame(columns=('document', 'real_url'), dtype='str')
        if not os.path.exists(output_dir):
            try:
                os.mkdir(output_dir)
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        while len(self.visited) < self.limit:
            url = self.nodes.get()

            if url in self.visited:
                print('visited', url)
                continue
            try:
                response = request.urlopen(url)
                info = dict(response.getheaders())['Content-Type'].split(';')
                content_type = info[0].strip()
                print('Visiting', url, content_type, content_type == 'text/html')
                if not content_type == 'text/html':
                    continue
                try:
                    encoding = info[1].strip().split('=')[-1]
                except IndexError:
                    encoding = 'utf-8'

                content = response.read().decode(encoding, 'replace')
                file = open(output_dir +'/document' + str(self.count) + '.html', 'w+')
                file.writelines(content)
                file.close()
                file = open(output_dir +'/document' + str(self.count) + '.html', 'r')
                soup = bs4.BeautifulSoup(file, 'html.parser')

            except error.HTTPError:
                print('Error', error.HTTPError.info(), 'retrieving data from', str(url))
                continue
            url_df = url_df.append({'document':'document'+str(self.count)+'.html','real_url':url}, ignore_index=True)
            #url_df.append(('document'+str(self.count)+'.html', url))
            self.visited.append(url)
            self.count += 1

            for link in soup.find_all('a'):
                if link.get('href'):
                    if not link.get('href').startswith('https'):
                        continue
                    href = link.get('href')
                    # print(href)
                    # Descargarnos la página de este html
                    self.nodes.put(href)

            url_df.to_csv(output_dir+'/url_repository.csv', index=False)
