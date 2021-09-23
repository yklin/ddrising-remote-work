# -*- coding: utf-8 -*-
import argparse
import datetime
import json

import dateutil.parser
from requests_html import HTMLSession


URL="https://cn.investing.com/equities/apple-computer-inc-historical-data"

"""
在網頁上，我們要的實際的資料來源:
https://cn.investing.com/instruments/HistoricalDataAjax
"""
AJAX_URL="https://cn.investing.com/instruments/HistoricalDataAjax"

payload = {
    "MIME Type": "application/x-www-form-urlencoded",
    "curr_id": 6408,
    "smlID": 1159963,
    "header": "AAPL历史数据",
    "st_date": "2021/09/15",
    "end_date": "2021/09/21",
    "interval_sec": "Daily",
    "sort_col": "date",
    "sort_ord": "DESC",
    "action": "historical_data",
}
headers = {
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'text/plain, */*; q=0.01',
    'Host': 'cn.investing.com',
    'Accept-Language': 'en-us',
    #'Accept-Encoding': 'br, gzip, deflate',
    'Origin': 'https://cn.investing.com',
    'Referer': 'https://cn.investing.com/equities/apple-computer-inc-historical-data',
    'Connection': 'keep-alive',
    'Content-Length': '191',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15',
}        



def gen_data(html):
    keys = ("日期", "收盘", "开盘", "高", "低", "交易量", "涨跌幅")
    values = []
    for i, x in enumerate(html.find("table#curr_table tbody tr td"), start=1):
        values.append(x.text)
        if i % 7 == 0:
            ret = dict(zip(keys, values))
            values = []
            yield ret


def fetch(start_date, end_date):
    payload["st_date"] = start_date.strftime("%Y/%m/%d")
    payload["end_date"] = end_date.strftime("%Y/%m/%d")

    session = HTMLSession()
    response = session.post(AJAX_URL, headers=headers, data=payload)
    ret = gen_data(response.html)
    return list(ret)


def main():
    # parse argument
    parser = argparse.ArgumentParser(description='AAPL crawler')
    parser.add_argument("-s", "--start",
                        help="start date: default: 10 days ago")
    parser.add_argument("-e", "--end",
                        help="end date, default: today")
    parser.add_argument("-o", "--output",
                        help="output file", default="output.json")
    args = parser.parse_args()

    end_date = dateutil.parser.parse(args.end) if args.end else \
        datetime.date.today()
    start_date = dateutil.parser.parse(args.start) if args.start else \
        end_date - datetime.timedelta(days=10)

    # fetch data
    ret = fetch(start_date, end_date)

    # output data
    with open(args.output, "w") as outfile:
        json.dump(ret, outfile, ensure_ascii=False)


if __name__ == "__main__":
    main()

