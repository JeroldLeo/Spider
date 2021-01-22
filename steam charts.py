import requests
from bs4 import BeautifulSoup, SoupStrainer
import re
import os
import xlwt
import time
from prettytable import PrettyTable


def request_contents(url):
    try:
        html = requests.get(url)
        if html.status_code == 200:
            return html.text
    except requests.RequestException:
        html = requests.get(url)
        print(html.status_code)
        return None


def get_trend(html, url, title1):
    focus = SoupStrainer(id='trending-recent')
    soup = BeautifulSoup(html, 'lxml', parse_only=focus)
    titles = soup('a')
    growth = soup(class_='gain')
    current_players = soup(class_='num')
    trend_table = PrettyTable(title1, align='l')
    for k in range(5):
        trend_table.add_row(
            [titles[k].string.strip(), growth[k].string, current_players[k].string, url + titles[k].get('href')]
        )
    print(trend_table)
    return titles, growth, current_players


def get_top_records(html, url, title2):
    focus = SoupStrainer(id='toppeaks')
    soup = BeautifulSoup(html, 'lxml', parse_only=focus)
    titles = soup('a')
    peak_players = soup(class_='num')
    date = soup(id=re.compile('toppeaks_.*?_time'))
    record_table = PrettyTable(title2, align='l')
    for p in range(10):
        record_table.add_row(
            [titles[p].string.strip(), peak_players[p].string, date[p].string.strip('T00:00:00Z'),
             url + titles[p].get('href')]
        )
    print(record_table)
    return titles, peak_players, date


def get_top_games(html, url):
    focus = SoupStrainer('tbody')
    soup = BeautifulSoup(html, 'lxml', parse_only=focus)
    titles = soup('a')
    # ids = soup(class_='chart period-col')
    current_players = soup(class_='num')
    peak_players = soup(class_='num period-col peak-concurrent')
    hours_played = soup(class_='num period-col player-hours')
    patten_x = 'elem.datax = (.*?);'
    patten_y = 'elem.datay = (.*?);'
    dates_hours_played = re.findall(patten_x, html)
    daily_hours_played = re.findall(patten_y, html)
    for n in range(25):
        print(' - '.join(
            [titles[n].string.strip(), current_players[int(n * 3)].string, peak_players[n].string,
             hours_played[n].string, url + titles[n].get('href')]))
    return titles, current_players, peak_players, hours_played, dates_hours_played, daily_hours_played


if __name__ == '__main__':
    """
    Top games are shown in separated web-pages. This parameter determined how deep (how many pages) do you want to 
    dig into.
    """
    pages = 4
    """
    Initialize excel workbook.
    Name is dynamically created by date.
    """
    name = r'./download/steam_chart-' + time.strftime("%Y-%m-%d") + '.xls'
    if os.path.exists(name):
        os.remove(name)
    book = xlwt.Workbook(encoding='utf-8', style_compression=0)
    sheet1 = book.add_sheet('Trends', cell_overwrite_ok=True)
    titles1 = ['Name', '24-hour Change', 'Current Players', 'Link']
    for tn1 in range(len(titles1)):
        sheet1.write(0, tn1, titles1[tn1])
    sheet2 = book.add_sheet('Top Records', cell_overwrite_ok=True)
    titles2 = ['Name', 'Peak Players', 'Time', 'Link']
    for tn2 in range(len(titles2)):
        sheet2.write(0, tn2, titles2[tn2])
    sheet3 = book.add_sheet('Top ' + str(pages * 25) + ' Games', cell_overwrite_ok=True)
    titles3 = ['Name', 'Current Players', 'Peak Players', 'Hours Played (last 30 Days)'] + [''] * 30 + ['Link']
    for tn3 in range(len(titles3)):
        sheet3.write(0, tn3, titles3[tn3])
    """
    Get Trend and Top Records from a same url.
    """
    url_1 = 'https://steamcharts.com'
    html_1 = request_contents(url_1)
    print('[Trend]')
    trend = get_trend(html_1, url_1, titles1)
    for rn in range(5):
        sheet1.write(rn + 1, 0, trend[0][rn].string.strip())
        sheet1.write(rn + 1, 1, trend[1][rn].string)
        sheet1.write(rn + 1, 2, int(trend[2][rn].string))
        sheet1.write(rn + 1, 3, url_1 + trend[0][rn].get('href'))
    print('\n[Top Records]')
    records = get_top_records(html_1, url_1, titles2)
    for tn in range(10):
        sheet2.write(tn + 1, 0, records[0][tn].string.strip())
        sheet2.write(tn + 1, 1, int(records[1][tn].string))
        sheet2.write(tn + 1, 2, re.sub('-01T00:00:00Z', '', records[2][tn].string))
        sheet2.write(tn + 1, 3, url_1 + records[0][tn].get('href'))
    """
    Get top games data from another url.
    """
    print('\n[Top %d Games] -- by current players' % (25 * pages))
    print('-' * 120)
    url_2 = 'https://steamcharts.com/top/p.'
    for i in range(1, pages + 1):
        url_3 = url_2 + str(i)
        html_2 = request_contents(url_3)
        games = get_top_games(html_2, url_1)
        dates = re.findall('"(.*?)T00:00:00Z",', games[4][0])
        details = games[5]
        for gn in range(25):
            rows = gn + (i - 1) * 25 + 1
            detail = re.findall(r'(\d*),', details[gn])
            if len(detail) < 30:
                detail = [''] * (30 - len(detail)) + detail
            sheet3.write(rows, 0, games[0][gn].string.strip())
            sheet3.write(rows, 1, int(games[1][gn * 3].string))
            sheet3.write(rows, 2, int(games[2][gn].string))
            sheet3.write(rows, 3, int(games[3][gn].string))
            sheet3.write(rows, 34, url_1 + games[0][gn].get('href'))
            for col in range(30):
                sheet3.write(rows, 4 + col, '' if detail[col] == '' else int(detail[col]))
        for dn in range(30):
            sheet3.write(0, 4 + dn, dates[dn])
    # Save workbook.
    book.save(name)
