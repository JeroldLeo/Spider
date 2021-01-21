import re
import requests
import json
import os
import sys
import time


def request_html(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # print("Connected")
            return response.text
    except requests.RequestException:
        return None


def parse_result(html):
    pattern = re.compile(
        r'<li.*?list_num.*?(\d+).</div>.*?<img src="(.*?)".*?<div class="name">.*?title="(.*?)".*?<div '
        'class="star">.*?<span class="tuijian">(.*?)</span>.*?<div class="publisher_info"><span>.*?target="_blank">('
        '.*?)</a>.*?<p>.*?<span class="price_n">&yen;(.*?)</span>',
        re.S)
    items = re.findall(pattern, html)
    for item in items:
        yield {
            'Rank': item[0],
            # 'Cover': item[1],
            'Title': item[2],
            'Recommend': item[3],
            'Publisher': item[4],
            'Price': item[5]
        }


def write_item_to_file(item):
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')
        f.close()


def main(page):
    url = 'http://bang.dangdang.com/books/bestsellers/01.00.00.00.00.00-recent30-0-0-1-' + str(page)
    html = request_html(url)
    items = parse_result(html)
    for item in items:
        write_item_to_file(item)


if __name__ == "__main__":
    filename = 'Book_Ranking.txt'
    if os.path.exists(filename):
        os.remove(filename)
    for i in range(1, 26):
        main(i)
        sys.stdout.write('\r' + 'Progress: %.0f %%' % float(100 * i / 25))
        sys.stdout.flush()
    print('\nJob done!')

