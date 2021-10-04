import os
import csv
import argparse
import statistics
from collections import deque

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Program transaction')

    parser.add_argument('--csv_folder', default='./StockData/', type=str, help='total csv data folder path')
    parser.add_argument('--product', default='2330', type=str, help='product number')
    parser.add_argument('--save_name', default='Record', type=str, help='transaction record csv name')
    parser.add_argument('--initial_money', default=5000000, type=int)
    parser.add_argument('--tax_rate', default=0.003, type=float, help='tax_rate')
    parser.add_argument('--handling_fee', default=0.001425, type=float, help='handling fee')
    parser.add_argument('--stop_loss_rate', default=0.1, type=float)
    parser.add_argument('--stop_profit_rate', default=0.2, type=float)
    parser.add_argument('--finish_time', default='103000000000', type=str, help='HHMMSSffffff')
    parser.add_argument('--QTY', default=1, type=int, help='quantity')

    args = parser.parse_args()

    namelist = os.listdir(args.csv_folder)
    BS = 0  # 手上沒股票
    flag = -1
    a1 = 0  # 日均
    a5 = 0
    average_5 = deque()  # 周均線
    a20 = 0
    average_20 = deque()  # 月均線
    with open('./' + args.save_name + '.csv', 'w', newline='') as f:
        w = csv.writer(f)
        for name in namelist:  # 一天開始
            Date = name[:8]
            print('Start:', Date)
            data = open(args.csv_folder + name).readlines()
            data = [i.strip('\n').split(',') for i in data if i[13:17] == args.product]
            open_price = data[0][2]  # 開盤價

            average_1 = []  # 日均

            # Golden cross 黃金交叉，多單買入
            if a20 < a5 < a1 and len(average_5) == 5 and len(average_20) == 20:
                print(' - 黃金交叉: 月均: %4f  周均: %4f  日均: %4f' % (a20, a5, a1))
                flag = 1  # 做多
            # Death cross 死亡交叉，空單賣出
            elif a1 < a5 < a20 and len(average_5) == 5 and len(average_20) == 20:
                print(' - 死亡交叉: 月均: %4f  周均: %4f  日均: %4f' % (a20, a5, a1))
                flag = 0  # 做空
            else:
                print(' - 無訊號  : 月均: %4f  周均: %4f  日均: %4f' % (a20, a5, a1))

            assert BS == 0  # 檢查每一天開始是否手上都沒股票
            ##################################################################################################################
            for i, each in enumerate(data):  # 一天開始: 9:00 ~ 13:00

                average_1.append(float(each[2]))

                # Golden cross 黃金交叉，多單買入
                if flag == 1:
                    Time = each[0]
                    Prod = each[1]
                    Price = each[2]

                    if BS == 0:  # 手上沒股票
                        cost = 0
                        profit = 0
                    else:  # 手上有股票，計算利潤
                        # 利潤 = 價差 - 成本(手續費+交易稅)
                        profit = (float(Price) - float(open_price)) * 1000 * args.QTY - \
                                 (round(float(Price) * 1000 * (args.tax_rate + args.handling_fee) * args.QTY) + cost)

                    # 手中沒股票，且在門檻時間以前。 若價格小於基礎價格買入。
                    if Price == open_price and BS == 0 and Time < args.finish_time:
                        open_price = Price
                        w.writerow([args.product, 'B', Date, str(Time), Price, args.QTY, ])
                        cost = round(float(Price) * 1000 * args.handling_fee * args.QTY)  # 買入成本
                        BS = BS + 1

                    # 手中有股票，且在門檻時間以前。 若利潤(價差) > 0 賣出
                    elif profit > 0 and BS > 0 and Time < args.finish_time:
                        w.writerow([args.product, 'S', Date, str(Time), Price, args.QTY, ])
                        BS = BS - 1

                    # 超過門檻時間 (價格浮動期)，且還未平倉，找後面時間有利潤 > 0的賣出。 結束今天買賣
                    elif profit > 0 and BS > 0 and Time >= args.finish_time:
                        w.writerow([args.product, 'S', Date, str(Time), Price, args.QTY, ])
                        BS = BS - 1
                        # break

                    # 超過門檻時間 (價格浮動期)，且還未平倉，並到達停損點，趕快賣出。 結束今天買賣
                    elif 0 > profit and float(Price) < float(open_price) * args.stop_loss_rate and BS > 0 \
                            and Time >= args.finish_time:
                        w.writerow([args.product, 'S', Date, str(Time), Price, args.QTY, ])
                        BS = BS - 1

                    # 超過門檻時間 (價格浮動期)，且還未平倉，以收盤價賣出。 結束今天買賣
                    elif BS > 0 and Time == data[len(data) - 1][0]:
                        close = data[len(data) - 1][2]
                        w.writerow([args.product, 'S', Date, str(Time), close, args.QTY, ])
                        BS = 0
                        # break

                # Death cross 死亡交叉，空單賣出
                if flag == 0:
                    Time = each[0]
                    Prod = each[1]
                    Price = each[2]

                    if BS == 0:  # 手上沒股票
                        cost = 0
                        profit = 0
                    else:  # 手上有股票，計算利潤
                        # 利潤 = 價差 - 成本(手續費+交易稅)
                        profit = (float(open_price) - float(Price)) * 1000 * args.QTY - \
                                 (round(float(Price) * 1000 * (args.tax_rate + args.handling_fee) * args.QTY) + cost)

                    # 手中沒股票，且在門檻時間以前。 若價格大於基礎價格買入。
                    if Price == open_price and BS == 0 and Time < args.finish_time:
                        open_price = Price
                        w.writerow([args.product, 'S', Date, str(Time), Price, args.QTY, ])
                        cost = round(float(Price) * 1000 * args.handling_fee * args.QTY)  # 賣出成本
                        BS = BS + 1

                    # 手中有股票，且在門檻時間以前。 若利潤(價差) > 0 買入
                    elif profit > 0 and BS > 0 and Time < args.finish_time:
                        w.writerow([args.product, 'B', Date, str(Time), Price, args.QTY, ])
                        BS = BS - 1

                    # 超過門檻時間 (價格浮動期)，且還未平倉，找後面時間有利潤 > 0的買入。 結束今天買賣
                    elif profit > 0 and BS > 0 and Time >= args.finish_time:
                        w.writerow([args.product, 'B', Date, str(Time), Price, args.QTY, ])
                        BS = BS - 1

                    # 超過門檻時間 (價格浮動期)，且還未平倉，並到達停損點，趕快買入。 結束今天買賣
                    elif 0 > profit and float(Price) > float(open_price) * args.stop_loss_rate and BS > 0 \
                            and Time >= args.finish_time:
                        w.writerow([args.product, 'S', Date, str(Time), Price, args.QTY, ])
                        BS = BS - 1

                    # 超過門檻時間 (價格浮動期)，且還未平倉，以收盤價買入。 結束今天買賣
                    elif BS > 0 and Time == data[len(data) - 1][0]:
                        close = data[len(data) - 1][2]
                        w.writerow([args.product, 'B', Date, str(Time), close, args.QTY, ])
                        BS = 0

            a1 = statistics.mean(average_1)
            average_5.append(a1)
            average_20.append(a1)
            if len(average_5) > 5:
                average_5.popleft()

            if len(average_20) > 20:
                average_20.popleft()

            a5 = statistics.mean((list(average_5)))
            a20 = statistics.mean(list(average_20))

    f.close()
