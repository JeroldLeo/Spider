import requests
from bs4 import BeautifulSoup
import xlwt

"""
Initialize workbook
"""
book = xlwt.Workbook(encoding='utf-8', style_compression=0)
sheet = book.add_sheet('top', cell_overwrite_ok=True)
sheet.write(0, 0, '排名')
sheet.write(0, 1, '名称')
sheet.write(0, 2, '评分')
sheet.write(0, 3, '简评')


def main(pages):
    url = 'https://movie.douban.com/top250?start=' + str(pages * 25) + '&filter='
    soup = response_douban(url)
    result = parse(soup)
    for each in result:
        rows = int(each['Index: '])
        sheet.write(rows, 0, each['Index: '])
        sheet.write(rows, 1, each['Title: '])
        sheet.write(rows, 2, each['Rating: '])
        sheet.write(rows, 3, each['Quote: '])


def response_douban(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/87.0.4280.141 Safari/537.36',
        'Connection': 'keep-alive',
        'Host': 'movie.douban.com'
    }
    try:
        response = requests.get(url=url, headers=headers)
        if response.status_code == 200:
            return response.text
    except requests.RequestException:
        # print('Error code:' + str(response.status_code))
        return None


def parse(soup):
    content = BeautifulSoup(soup, 'lxml')
    lists = content.find(class_='grid_view').find_all('li')
    for item in lists:
        index = item.find('em').string
        title = item.find('span', class_='title').string
        rating = item.find('span', class_='rating_num').string
        if item.find('span', class_='inq') is not None:
            quote = item.find('span', class_='inq').string
        yield {
            'Index: ': index,
            'Title: ': title,
            'Rating: ': rating,
            'Quote: ': quote
        }


if __name__ == '__main__':
    for page in range(10):
        main(page)

book.save(u'top250.xls')
