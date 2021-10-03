import os
import csv
import argparse
from tqdm import tqdm
from model import MLP
import torch
import utils

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Program transaction')

    parser.add_argument('--weights', default='./checkpoints/MLP_stock_predict/models/mini_loss_model.pth', type=str)
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

    predict = MLP(n_inputs=4, hidden_layer1=128, hidden_layer2=256, hidden_layer3=128)
    predict.eval()
    utils.load_checkpoint(predict, args.weights)

    namelist = os.listdir(args.csv_folder)
    BS = 0  # 手上沒股票
    flag = 0  # 判斷是要(0:做多, 1:做空, -1:放棄)
    base_price = []
    close_price = []
    min_price, max_price = [], []
    with open('./' + args.save_name + '.csv', 'w', newline='') as f:
        w = csv.writer(f)
        for name in namelist:  # 1 day
            Date = name[:8]
            print('Start:', Date)
            data = open(args.csv_folder + name).readlines()
            data = [i.strip('\n').split(',') for i in data if i[13:17] == args.product]
            open_price, M, m = data[0][2], data[0][2], data[0][2]
##################################################################################################################
            if namelist.index(name) == 0:
                flag = -1  # 第一天沒參考資料先放棄，蒐集數據
                for i, each in enumerate(data):
                    if each[2] > M:
                        M = each[2]
                    if each[2] < m:
                        m = each[2]
            else:  # 有數據可以預測
                a = base_price[namelist.index(name)-1]
                b = max_price[namelist.index(name)-1]
                c = min_price[namelist.index(name)-1]
                d = close_price[namelist.index(name)-1]
                inputs = torch.tensor([float(a), float(b), float(c), float(d)], dtype=torch.float32)
                result = predict(inputs).item()
                print(result)
                if result > 0:
                    flag = 1
                if result < -0.05:
                    flag = 0
                if -0.05 < result < 0:
                    flag = 1

                if flag == -1:  # 放棄買賣，但要計算開、收盤價，來預測明天漲跌。
                    for i, each in enumerate(data):
                        if each[2] > M:
                            M = each[2]
                        if each[2] < m:
                            m = each[2]


                if flag == 0:  # 覺得今天會漲，做多
                    # 做多策略
                    assert BS == 0  # 檢查每一天開始是否手上都沒股票
                    for i, each in enumerate(data):
                        if each[2] > M:
                            M = each[2]
                        if each[2] < m:
                            m = each[2]
                        Time = each[0]
                        Prod = each[1]
                        Price = each[2]

                        if BS == 0:  # 手上沒股票
                            cost = 0
                            profit = 0
                        else:  # 手上有股票，計算利潤
                            # 利潤 = 價差 - 成本(手續費+交易稅)
                            profit = (float(Price)-float(open_price))*1000*args.QTY - \
                                     (round(float(Price)*1000*args.tax_rate*args.QTY) + cost)

                        # 手中沒股票，且在門檻時間以前。 若價格小於基礎價格買入。
                        if Price < open_price and BS == 0 and Time < args.finish_time:
                            open_price = Price
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
                            close = data[len(data) - 1][2]
                            w.writerow([args.product, 'S', Date, str(Time), close, args.QTY,])
                            BS = 0
                            break


                if flag == 1:  # 覺得今天會跌，做空
                    # 做空策略
                    assert BS == 0  # 檢查每一天開始是否手上都沒股票
                    for i, each in enumerate(data):
                        if each[2] > M:
                            M = each[2]
                        if each[2] < m:
                            m = each[2]
                        Time = each[0]
                        Prod = each[1]
                        Price = each[2]

                        if BS == 0:  # 手上沒股票
                            cost = 0
                            profit = 0
                        else:  # 手上有股票，計算利潤
                            # 利潤 = 價差 - 成本(手續費+交易稅)
                            profit = (float(open_price) - float(Price)) * 1000 * args.QTY - \
                                    (round(float(Price) * 1000 * args.tax_rate * args.QTY) + cost)

                        # 手中沒股票，且在門檻時間以前。 若價格大於基礎價格買入。
                        if Price > open_price and BS == 0 and Time < args.finish_time:
                            open_price = Price
                            w.writerow([args.product, 'S', Date, str(Time), Price, args.QTY, ])
                            cost = round(float(Price) * 1000 * args.tax_rate * args.QTY)  # 賣出成本
                            BS = BS + 1

                        # 手中有股票，且在門檻時間以前。 若利潤(價差) > 0 買入
                        elif profit > 0 and BS > 0 and Time < args.finish_time:
                            w.writerow([args.product, 'B', Date, str(Time), Price, args.QTY, ])
                            BS = BS - 1

                        # 超過門檻時間 (價格浮動期)，且還未平倉，找後面時間有利潤 > 0的買入。 結束今天買賣
                        elif profit > 0 and BS > 0 and Time >= args.finish_time:
                            w.writerow([args.product, 'B', Date, str(Time), Price, args.QTY, ])
                            BS = BS - 1
                            break

                        # 超過門檻時間 (價格浮動期)，且還未平倉，以收盤價買入。 結束今天買賣
                        elif BS > 0 and Time == data[len(data) - 1][0]:
                            close = data[len(data) - 1][2]
                            w.writerow([args.product, 'B', Date, str(Time), close, args.QTY, ])
                            BS = 0
                            break

            base_price.append(data[0][2])  # 開盤價
            close_price.append(data[len(data) - 1][2])  # 收盤價
            min_price.append(m)
            max_price.append(M)


    f.close()
