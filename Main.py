# 匯入套件
import os
import csv


path = 'StockData/'             # 資料路徑
NameList = os.listdir(path)     # 取資料夾內所有檔名
Record = open('Record.csv','w') # 交易紀錄
BS = None                       # 手中部位狀態
Prod = '2330'                   # 股票標的
QTY = '1'                       # 交易的張數

# 逐日回測
for name in NameList:
    # 日期
    Date = name[:8]
    print('Start:',Date)
    # 讀檔並整理資料
    data = open(path + name).readlines()
    data = [i.strip('\n').split(',') for i in data if i[13:17] == Prod]
    
    # 進出場判斷
    for i in data:
        Time = i[0]   # 時間
        Prod = i[1]   # 商品
        Price = i[2]  # 價格
        # 多單進場
        if BS == None and Time >= '09000000':
            Record.write( ','.join([Prod,'B',Date,Time,Price,QTY+'\n']) )
            BS = 'B'
        # 多單出場
        elif BS == 'B' and Time >= '13000000':
            Record.write( ','.join([Prod,'S',Date,Time,Price,QTY+'\n']) )
            BS = None
            break
    
Record.close()
