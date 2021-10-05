# Stock_program_transaction  
- [第四屆高雄盃程式交易競賽](https://bhuntr.com/tw/competitions/eqpkavrw0olm1wupbd)  

```
└── README.md 

├── main.py                 main programe
└── KPI.py                  evaluation 
```  

## Quick Run
To test the program, run `main.py` to get the transaction csv `Record.csv`  
```
python main.py
```
To set the parameters in main, run
```
python main.py --product product_name --stop_loss_rate stop_loss_rate --finish_time time(HHMMSSffffff) --QTY quantity
```
Here is an example to perform 2330.TW:
```
python main.py --product '2330' --stop_loss_rate 0.03 --finish_time '103000000000' --QTY 1
```

## Predict strategy  
Calculate 1, 5 and 20 days average prices to find Golden cross, Death cross  
- Golden cross (a20 < a5 < a1): Long  
- Death cross (a20 > a5 > a1): Short

## Buy, Sell strategy  
```
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
```

## KPI (evaluation)  
To evaluate the report, run `KPI.py` to get the result csv: `KPI.csv`
```
python KPI.py
```
Our KPI result `KPI.csv` is showed bellow:
| 總損益 | 總交易次數 | 平均損益 | 勝率 | 獲利因子 | 賺賠比 | 最大資金回落 | 夏普比率 | 是否超額交易 |
| :---: | :--------: | :-----: | :-: | :------: | :---: | :---------: | :-----: | :---------: |
|1474694| 874       | 1687.2929|0.675|3.0082    |1.4480 |600068       |0.3519   |否            |

## Report  
- Preliminary written report: https://drive.google.com/file/d/1wkxdQN863TYorcstUOdHMq1jP3j1MU0g/view?usp=sharing  


## Contact us  
- Chi-Mao Fan: qaz5517359@gmail.com  
- Yu-Fang Huang: lin12099@yahoo.com.tw  
- Kai-Hua Yeh: kateyehyeh@gmail.com  
- Wei-Xian Lion: zxc741852741@gmail.com  
- Li-Chi Lan: bluepro6726abc@gmail.com  


