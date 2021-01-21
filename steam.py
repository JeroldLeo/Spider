import requests
import xlwt
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
import os
import sys


def request_main_page(url):
    try:
        html = requests.get(url=url)
        if html.status_code == 200:
            return html.text
    except requests.RequestException:
        return None


def parse_main_page(html, limit):
    soup = BeautifulSoup(html, 'lxml')
    limit = min(100, limit)
    titles = soup(class_='gameLink', limit=limit)
    users = soup(class_='currentServers', limit=limit * 2)
    return [titles, users]


def parse_detailed_page(detailed_url):
    html_detail = requests.get(detailed_url)
    soup_detail = BeautifulSoup(html_detail.text, 'lxml')
    # focus = SoupStrainer(class_='user_reviews_summary_row')
    reviews = soup_detail(class_='user_reviews_summary_row')
    if len(reviews) == 0:
        current_review_summary, total_review_summary = 'n/a', 'n/a'
    elif len(reviews) == 1:
        current_review_summary = reviews[0].get('data-tooltip-html')
        total_review_summary = 'n/a'
    else:
        current_review_summary = reviews[0].get('data-tooltip-html')
        total_review_summary = reviews[1].get('data-tooltip-html')
    return current_review_summary, total_review_summary


if __name__ == '__main__':
    separator = ' | '
    limit = 100
    file = 'steam.xls'
    url = 'https://store.steampowered.com/stats/'
    html = request_main_page(url)
    titles = parse_main_page(html, limit)[0]
    users = parse_main_page(html, limit)[1]
    if os.path.exists(file):
        os.remove(file)
    book = xlwt.Workbook(encoding='utf-8', style_compression=0)
    sheet = book.add_sheet('top', cell_overwrite_ok=True)
    sheet.write(0, 0, '游戏')
    sheet.write(0, 1, '当前玩家数')
    sheet.write(0, 2, '今日峰值')
    sheet.write(0, 3, '链接')
    sheet.write(0, 4, '最近评价')
    sheet.write(0, 5, '全部评价')
    for i in range(limit):
        title = titles[i].string
        cu = users[2 * i].string
        pcu = users[2 * i + 1].string
        link = titles[i].get('href')
        current_review_summary = parse_detailed_page(link)[0]
        total_review_summary = parse_detailed_page(link)[1]
        # print(separator.join((title, cu, pcu, link, current_review_summary, total_review_summary)), end='\n\r')
        sys.stdout.write('\r' + separator.join((title, cu, pcu, link, current_review_summary, total_review_summary)))
        sys.stdout.flush()
        row = i + 1
        sheet.write(row, 0, title)
        sheet.write(row, 1, cu)
        sheet.write(row, 2, pcu)
        sheet.write(row, 3, link)
        sheet.write(row, 4, current_review_summary)
        sheet.write(row, 5, total_review_summary)
    book.save('steam.xls')
    print('\nJob done!')
