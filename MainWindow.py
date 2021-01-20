#region [module]
import re
import numpy as np
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
from tkinter import messagebox, filedialog, ttk
from tkinter import *
from Lotto import *
from requests.models import parse_header_links
from pandas.core.base import DataError
from bs4.element import SoupStrainer
from typing import ChainMap
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor
from os import truncate
import tkinter
from tkinter import font
import matplotlib
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Taipei Sans TC Beta']
# endregion

#region [function]


def Gen_Urls():
    # 102-1 ~ 109-9
    global Code_Urls, Award_Urls
    temp_code_urls = "https://www.etax.nat.gov.tw/etw-main/web/ETW183W2_"
    temp_award_url = "https://www.etax.nat.gov.tw/etw-main/web/ETW183W3_"
    years = ["102", "103", "104", "105", "106", "107", "108", "109"]
    months = ["01", "03", "05", "07", "09", "11"]
    for y in years:
        for m in months:
            Code_Urls.append(temp_code_urls + y + m)
            Award_Urls.append(temp_award_url + y + m)
    Code_Urls.pop()
    Award_Urls.pop()


def get_codeurl_content(url):
    period = url[-5:]
    html = requests.get(url).content.decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    unsolvedList = soup.find_all('td', class_='number')
    unsolved_str = ""
    for u in unsolvedList:
        unsolved_str += str(u)
    receipt_regex = re.compile(r"[0-9]{8}|[0-9]{3}")
    codes = receipt_regex.findall(unsolved_str)
    LottoCodeLibrary[period] = Lotto(
        period, codes[0], codes[1], codes[2:5], codes[5:])


def get_awardurl_content(url):

    period = url[-5:]
    html = requests.get(url).content.decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    # 特別獎
    XaddressList = soup.find_all('td', attrs={"headers": "companyAddress"})
    XaddressList = [add.string[0:3] for add in XaddressList]
    LottoXawardLibrary[period] = XaddressList
    # 特獎
    SaddressList = soup.find_all('td', attrs={"headers": "companyAddress2"})
    SaddressList = [add.string[0:3] for add in SaddressList]
    LottoSawardLibrary[period] = SaddressList


def Get_DataSet(thread_num=5):
    with ThreadPoolExecutor(max_workers=thread_num) as executor:
        for url in Code_Urls:
            executor.submit(get_codeurl_content, url)


def Get_AwardSet(thread_num=5):
    with ThreadPoolExecutor(max_workers=thread_num) as executor:
        for url in Award_Urls:
            executor.submit(get_awardurl_content, url)


def RedeemInput():
    global year_combox, month_combox, code_entry
    global LottoCodeLibrary

    period = year_combox.get()+month_combox.get()[0:2]
    code = code_entry.get()
    result_msg = LottoCodeLibrary[period].redeem(target=code)
    # update text
    fileResult_Text.config(state=tk.NORMAL)
    fileResult_Text.delete('1.0', END)
    fileResult_Text.insert("insert", result_msg)
    fileResult_Text.config(state=tk.DISABLED)


def LoadFile():
    global filePath_label, FileCodeList, DateCodeDict

    FileCodeList = []
    DateCodeDict = {}

    filePath = filedialog.askopenfilename()
    filePath_label.config(text=filePath)
    if(filePath[-3:] == 'txt'):
        file = open(filePath, 'r')
        codeText = file.read()
        file.close()
        FileCodeList = re.split(",|\n", codeText)
        # remove non digit
        FileCodeList = [x[2:] for x in FileCodeList]
    else:
        df = pd.read_csv(filePath)
        for m in df:
            month = df[m].tolist()
            month = [code for code in month if str(
                code) != 'nan']  # remove nan value
            month = [code[2:]
                     for code in month]                   # remove non digit
            # ex 109/9 -> 10909
            if(int(m[4:]) < 10):
                m = m[0:3] + '0' + m[4:]
            else:
                m = m[0:3] + m[4:]
            DateCodeDict[m] = month

    return filePath


def RedeemCodeFile():
    # ProcessPoolExecutor
    global fileResult_Text, FileCodeList
    global year_combox, month_combox, code_entry
    global LottoCodeLibrary
    print(FileCodeList)
    period = year_combox.get()+month_combox.get()[0:2]
    fileResult_Text.config(state=tk.NORMAL)
    fileResult_Text.delete('1.0', END)
    for code in FileCodeList:
        result_msg = LottoCodeLibrary[period].redeem(target=code)
        fileResult_Text.insert("insert", result_msg + '\n')
    fileResult_Text.config(state=tk.DISABLED)


def RedeemDateFile():
    global DateCodeDict
    print(DateCodeDict)
    fileResult_Text.config(state=tk.NORMAL)
    fileResult_Text.delete('1.0', END)
    for date, codes in DateCodeDict.items():
        fileResult_Text.insert("insert", '=============' + date + '\n')
        for code in codes:
            print(code)
            result_msg = LottoCodeLibrary[date].redeem(target=code)
            fileResult_Text.insert("insert", result_msg + '\n')
    fileResult_Text.config(state=tk.DISABLED)


def DoStatistics():

    global start_year_combobox, start_month_combobox, end_year_combobox, end_month_combobox
    global LottoXawardLibrary, LottoSawardLibrary

    start_yearmonth = start_year_combobox.get(
    ) + start_month_combobox.get()[0:2]
    end_yearmonth = end_year_combobox.get() + end_month_combobox.get()[0:2]
    start_yearmonth = int(start_yearmonth)
    end_yearmonth = int(end_yearmonth)
    print(start_yearmonth, end_yearmonth)

    prize_dict = dict()
    count_dict = dict()
    # 特獎
    for yearmonth, countries in LottoXawardLibrary.items():
        if(int(yearmonth) >= start_yearmonth and int(yearmonth) <= end_yearmonth):
            for ctry in countries:
                count_dict[ctry] = count_dict.get(ctry, 0) + 1
                prize_dict[ctry] = prize_dict.get(ctry, 0) + 10000000
    # 特別獎
    for yearmonth, countries in LottoSawardLibrary.items():
        if(int(yearmonth) >= start_yearmonth and int(yearmonth) <= end_yearmonth):
            for ctry in countries:
                count_dict[ctry] = count_dict.get(ctry, 0) + 1
                prize_dict[ctry] = prize_dict.get(ctry, 0) + 2000000

    for k, v in count_dict.items():
        print(k, v)
    for k, v in prize_dict.items():
        print(k, v)
    # 統計各縣市中獎數目
    sorted_count_values = sorted(count_dict.values(), reverse=True)
    sorted_count_keys = sorted(count_dict, key=count_dict.get, reverse=True)
    fig = Figure(figsize=(7.2, 5), dpi=65)
    fig.add_subplot(111)
    fig.add_subplot(111).bar(sorted_count_keys, sorted_count_values)
    fig.autofmt_xdate(rotation=90)
    # A tk.DrawingArea.
    countFigure_canvas = FigureCanvasTkAgg(fig, master=window)
    countFigure_canvas.draw()
    countFigure_canvas.get_tk_widget().place(x=250, y=65)
    # 統計各縣市中獎金額
    sorted_prize_values = sorted(prize_dict.values(), reverse=True)
    sorted_prize_keys = sorted(prize_dict, key=count_dict.get, reverse=True)
    fig = Figure(figsize=(7.2, 5), dpi=65)
    fig.add_subplot(111)
    fig.add_subplot(111).bar(sorted_prize_keys, sorted_prize_values)
    fig.autofmt_xdate(rotation=90)
    # A tk.DrawingArea.
    prizeFigure_canvas = FigureCanvasTkAgg(fig, master=window)
    prizeFigure_canvas.draw()
    prizeFigure_canvas.get_tk_widget().place(x=250, y=395)


def CenterWindow(win, w=300, h=200):

    # get screen width and height
    ws = win.winfo_screenwidth()
    hs = win.winfo_screenheight()
    # calculate position x, y
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    win.geometry('%dx%d+%d+%d' % (w, h, x, y))

# endregion


# region [window & widget layout]
window = Tk()
window.title("Invoice Redeemer X")
window.resizable(0, 0)
window.config(bg="black")
window.attributes("-alpha", 0.9)
CenterWindow(window, 725, 725)


yearList = ["102", "103", "104", "105", "106", "107", "108", "109"]
monthList = ["01-02", "03-04", "05-06", "07-08", "09-10", "11-12"]
# -------------------------------------------------------------------------------
code_label = Label(window, text="號碼", bg="#70b9dc")
code_label.place(x=5, y=5, width=50, height=25)
code_entry = Entry()
code_entry.place(x=60, y=5, width=100, height=25)
# -------------------------------------------------------------------------------
year_label = Label(window, text="年份", bg="#70b9dc")
year_label.place(x=5, y=35, width=50, height=25)
year_combox = ttk.Combobox(window, values=yearList)
year_combox.place(x=60, y=35, width=100, height=25)
month_label = Label(window, text="月份", bg="#70b9dc")
month_label.place(x=5, y=65, width=50, height=25)
month_combox = ttk.Combobox(window, values=monthList)
month_combox.place(x=60, y=65, width=100, height=25)
# -------------------------------------------------------------------------------
redeem_btn = Button(window, text="兌獎", bg="#9dcf24", command=RedeemInput)
redeem_btn.place(x=165, y=5, width=50, height=85)
# -------------------------------------------------------------------------------
filePath_label = Label(window, text="", anchor='w')
filePath_label.place(x=5, y=95, width=155, height=25)
loadFile_btn = Button(window, text="開檔", bg="#9dcf24", command=LoadFile)
loadFile_btn.place(x=165, y=95, width=50, height=25)
# -------------------------------------------------------------------------------
codefileRedeem_btn = Button(window, text="同期批次兌獎",
                            bg="#9dcf24", command=RedeemCodeFile)
codefileRedeem_btn.place(x=5, y=125, width=210, height=25)
datefileRedeem_btn = Button(window, text="分期批次兌獎",
                            bg="#9dcf24", command=RedeemDateFile)
datefileRedeem_btn.place(x=5, y=155, width=210, height=25)
fileResult_Text = Text(window, bg="#fff9d5", font="微軟正黑體 10")
fileResult_Text.place(x=5, y=185, width=210, height=535)
# -------------------------------------------------------------------------------
statistic_label = Label(window, text="統計各縣市中獎", bg="yellow")
statistic_label.place(x=220, y=5, width=500, height=25)

start_label = Label(window, text="開始年月", bg="#70b9dc")
start_label.place(x=220, y=35, width=100, height=25)
start_year_combobox = ttk.Combobox(window, values=yearList)
start_year_combobox.place(x=320, y=35, width=60, height=25)
start_month_combobox = ttk.Combobox(window, values=monthList)
start_month_combobox.place(x=380, y=35, width=60, height=25)

end_label = Label(window, text="結束年月", bg="#70b9dc")
end_label.place(x=445, y=35, width=100, height=25)
end_year_combobox = ttk.Combobox(window, values=yearList)
end_year_combobox.place(x=545, y=35, width=60, height=25)
end_month_combobox = ttk.Combobox(window, values=monthList)
end_month_combobox.place(x=605, y=35, width=60, height=25)

country_awardcount_label = Label(
    window, text="各\n縣\n市\n中\n獎\n數\n目", bg="#70b9dc")
country_awardcount_label.place(x=220, y=65, width=25, height=325)
country_awardprize_label = Label(
    window, text="各\n縣\n市\n中\n獎\n金\n額", bg="#70b9dc")
country_awardprize_label.place(x=220, y=395, width=25, height=325)
statistic_btn = Button(window, text="統計", bg="#9dcf24", command=DoStatistics)
statistic_btn.place(x=670, y=35, width=50, height=25)
# -------------------------------------------------------------------------------
# endregion

Code_Urls = []          # 中獎號碼網址
Award_Urls = []         # 中獎清冊網址

FileCodeList = []       # 由txt讀入的發票號碼
DateCodeDict = dict()   # 由csv讀入的發票號碼

LottoXawardLibrary = dict()  # 依期特獎縣市
LottoSawardLibrary = dict()  # 依期特別獎縣市

LottoCodeLibrary = dict()   # 存放每期中獎號碼
# -----------------------------

if(__name__ == "__main__"):
    # 解決中文亂碼問題
    # https://reurl.cc/ZQnEng
    print(matplotlib.__file__)
    startt = time.time()
    Gen_Urls()
    Get_DataSet(8)
    Get_AwardSet(8)
    endt = time.time()
    cost_time = endt - startt
    print("init cost= ", cost_time)
    window.mainloop()
