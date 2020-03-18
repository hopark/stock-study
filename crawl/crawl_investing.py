import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import warnings
from bs4 import BeautifulSoup as bs
import pandas as pd
import sys
import json

url = 'https://kr.investing.com/stock-screener/Service/SearchStocks'
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36", "x-Requested-With": "XMLHttpRequest"}
param = {
    "country[]": "11",
    "sector": "3,1,7,6,12,2,8,9,10,11,5,4",
    "industry": "18,53,67,89,43,31,6,38,87,77,66,81,48,16,11,54,33,24,20,29,91,36,73,21,50,3,63,7,10,86,78,101,27,90,85,82,2,96,8,22,14,45,92,65,40,70,42,39,99,98,79,64,80,15,26,44,74,97,76,88,17,12,47,62,68,83,84,57,35,72,51,25,28,5,60,19,4,61,37,34,93,71,30,102,100,58,95,94,32,13,46,1,52,23,75,56,59,41,49,55,69,9",
    "equityType": "ORD,DRC,Preferred,Unit,ClosedEnd,REIT,ELKS,OpenEnd,Right,ParticipationShare,CapitalSecurity,PerpetualCapitalSecurity,GuaranteeCertificate,IGC,Warrant,SeniorNote,Debenture,ETF,ADR,ETC,ETN",
    "exchange[]": ["130", "110", "60"],
    "order[col]": "eq_market_cap",
    "order[dir]": "d"
}

warnings.simplefilter('ignore',InsecureRequestWarning)
stock_list = []
with requests.Session() as s:
    def getBalanceSheet(pair_ID):
        bal_url = f'https://kr.investing.com/instruments/Financials/changereporttypeajax?action=change_report_type&pair_ID={pair_ID}&report_type=BAL&period_type=Annual'
        page = s.get(bal_url, headers=headers, verify=False, timeout=30)
        html = page.text
        return bs(html, 'html.parser')

    pages = int(int(sys.argv[1])/50)
    num = 0
    for pn in range(pages):
        stock = s.post(url, headers=headers, verify=False, data={**param, "pn": str(pn+1)}).json()['hits']
        for i in range(len(stock)):
            balance_sheet = getBalanceSheet(stock[i]['pair_ID'])
            rows = balance_sheet.select('tr.pointer')
            for row in rows:
                cell = row.select('td')
                field = cell[0].text
                data = cell[1].text
                stock[i][field] = data
            print(f'progress.. {num}/{sys.argv[1]}')
            num += 1    
        stock_list += stock
pd.DataFrame(stock_list).to_csv('stock_info.csv', encoding='utf-8', sep=',', index=False)