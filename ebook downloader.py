import requests
import sys
from bs4 import BeautifulSoup

"""
Class Desc: A novel download spider.
Parameters: Null
Returns:    Null
Modify:     2021/1/8
"""


class Downloader(object):

    def __init__(self):
        self.server = 'http://www.biqukan.com/'
        self.target = 'http://www.biqukan.com/1_1094/'
        self.chapters = []  # Chapter names
        self.urls = []  # Chapter URL
        self.nums = 0  # Chapter number

    """
    Function Desc:  Get download URLs
    Returns:        Null
    Modify:     2021/1/8
    """

    def get_download_url(self):
        req = requests.get(url=self.target)
        req.encoding = req.apparent_encoding  # Fix encoding error.
        html = req.text
        div_bf = BeautifulSoup(html, 'lxml')
        div = div_bf.find_all('div', class_='listmain')
        a_bf = BeautifulSoup(str(div[0]), 'lxml')
        a = a_bf.find_all('a')
        self.nums = len(a[13:])  # Skip garbage and count chapter number
        for each in a[13:]:
            self.chapters.append(each.string)
            self.urls.append(self.server + str(each.get('href')))

    """
    Function Desc:  Fetch chapter content
    Parameters:     target  - Download URL (string)
    Returns:        texts   - Chapter contents (string)
    Modify:         2021/1/11
    """

    def get_contents(self, target):
        req = requests.get(url=target)
        req.encoding = req.apparent_encoding  # Fix encoding error.
        html = req.text
        bf = BeautifulSoup(html, 'lxml')
        texts = bf.find_all('div', class_='showtxt')
        texts = texts[0].text.replace('\xa0' * 8, '\n\n')
        return texts

    """
    Function Desc:  Save chapter content as files
    Parameters:     
        name - Chapter name (string)
        path - Working path and file name (string)
        text - Chapter contents (string)
    Returns:    Null
    Modify:     2021/1/11
    """

    def writer(self, name, path, text):
        write_flag = True
        with open(path, 'a', encoding='utf-8') as f:
            f.write(name + '\n')
            f.writelines(text)
            f.write('\n\n')


if __name__ == '__main__':
    dl = Downloader()
    dl.get_download_url()
    print('Download initialized...')
    for i in range(dl.nums):
        dl.writer(dl.chapters[i], 'ebook.txt', dl.get_contents(dl.urls[i]))
        sys.stdout.write('\r' + '    Progress: %.0f%%' % float((i + 1) * 100 / dl.nums))
        sys.stdout.flush()
    print('\n' + 'Job done!')
