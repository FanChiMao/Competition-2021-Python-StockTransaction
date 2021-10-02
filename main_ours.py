import os
import csv
import argparse
from tqdm import tqdm



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
    parser.add_argument('--QTY', default=1, type=int, help='quantity')

    args = parser.parse_args()


    namelist = os.listdir(args.csv_folder)
    BS = 0
    with open('./' + args.save_name + '.csv', 'w', newline='') as f:
        w = csv.writer(f)
        for name in namelist:  # 1 day
            Date = name[:8]
            print('Start:', Date)
            data = open(args.csv_folder + name).readlines()
            data = [i.strip('\n').split(',') for i in data if i[13:17] == args.product]

            base_price = data[0][2]

            assert BS == 0  # 檢查每一天開始是否手上都沒股票
            for i, each in enumerate(tqdm(data, ncols=50), 0):
                Time = each[0]
                Prod = each[1]
                Price = each[2]
                if BS == 0:  # 手上沒股票
                    cost = 0
                    profit = 0
                else:  # 手上有股票，計算利潤
                    # 利潤 = 價差 - 成本(手續費+交易稅)
                    profit = (float(Price)-float(base_price))*1000*args.QTY - \
                             (round(float(Price)*1000*args.tax_rate*args.QTY) + cost)

                # 手中沒股票，且在門檻時間以前。 若價格小於基礎價格買入。
                if Price < base_price and BS == 0 and Time < args.finish_time:
                    base_price = Price
                    w.writerow([args.product, 'B', Date, str(Time), Price, args.QTY,])
                    cost = round(float(Price) * 1000 * args.tax_rate * args.QTY)  # 買入成本
                    BS = BS + 1

                # 手中有股票，且在門檻時間以前。 若利潤(價差) > 0 賣出
                elif profit > 0 and BS > 0 and Time < args.finish_time:
                    w.writerow([args.product, 'S', Date, str(Time), Price, args.QTY,])
                    BS = BS - 1

                # 超過門檻時間 (價格浮動期)，且還未平倉，找後面時間有利潤 > 0的賣出。 結束今天買賣
                elif profit > 0 and BS > 0 and Time >= args.finish_time:
                    w.writerow([args.product, 'S', Date, str(Time), Price, args.QTY,])
                    BS = BS - 1
                    break

                # 超過門檻時間 (價格浮動期)，且還未平倉，以收盤價賣出。 結束今天買賣
                elif BS > 0 and Time == data[len(data) - 1][0]:
                    close_price = data[len(data) - 1][2]
                    w.writerow([args.product, 'S', Date, str(Time), close_price, args.QTY,])
                    BS = 0
                    break

    f.close()
