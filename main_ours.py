import os
import csv
import argparse
from tqdm import tqdm
import utils
from strategy import BuySell

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Program transaction')

    parser.add_argument('--csv_folder', default='./StockData/', type=str, help='total csv data folder path')
    parser.add_argument('--product', default='2330', type=str, help='product number')
    parser.add_argument('--save_name', default='Record', type=str, help='transaction record csv name')
    parser.add_argument('--initial_money', default=5000000, type=int)
    parser.add_argument('--tax_rate', default=0.004425, type=float, help='tax_rate + handling fee')
    parser.add_argument('--stop_loss_rate', default=0.1, type=float)
    parser.add_argument('--stop_profit_rate', default=0.2, type=float)
    parser.add_argument('--finish_time', default='103000000000', type=str, help='HHMMSSffffff')
    parser.add_argument('--QTY', default=5, type=int, help='quantity')

    args = parser.parse_args()


    namelist = os.listdir(args.csv_folder)
    with open('./' + args.save_name + '.csv', 'w', newline='') as f:
        w = csv.writer(f)
        for name in namelist:# 1 day
            Date = name[:8]
            BS = None
            print('Start:', Date)

            data = open(args.csv_folder + name).readlines()
            data = [i.strip('\n').split(',') for i in data if i[13:17] == args.product]


            base_price = float(data[0][2])
            close_price = float(data[len(data)-1][2])

            for i, each in enumerate(tqdm(data), 0):
                Time = each[0]
                Price = float(each[2])
                if BS == None:  # 手上沒股票
                    cost = 0
                    profit = 0
                else:  # 手上有股票，計算利潤
                    # 利潤 = 價差 - 成本(手續費+交易稅)
                    profit = (Price-base_price)*1000*args.QTY - ((Price*1000*args.tax_rate*args.QTY) + cost)

                # 手中沒股票，且在門檻時間以前。 若價格小於基礎價格買入。
                if Price < base_price and BS == None and Time < args.finish_time:
                    base_price = Price
                    w.writerow([args.product, 'B', Date, Time, str(Price), args.QTY])
                    cost = Price * 1000 * args.tax_rate * args.QTY  # 買入成本
                    BS = 'B'

                # 手中有股票，且在門檻時間以前。 若利潤(價差) > 0 賣出
                elif profit > 0 and BS == 'B' and Time < args.finish_time:
                    w.writerow([args.product, 'S', Date, Time, str(Price), args.QTY])
                    BS = None

                # 超過門檻時間 (價格浮動期)，且還未平倉，找後面時間有利潤 > 0的賣出。 結束今天買賣
                elif profit > 0 and BS == 'B' and Time >= args.finish_time:
                    w.writerow([args.product, 'S', Date, Time, str(Price), args.QTY])
                    BS = None
                    break

                # 超過門檻時間 (價格浮動期)，且還未平倉，以收盤價賣出。 結束今天買賣
                # BS == 'B' and Time == 133000000000
                elif BS == 'B' and Time == 133000000000:
                    w.writerow([args.product, 'S', Date, '133000000000', str(close_price), args.QTY])
                    BS = None
                    break
    f.close()
