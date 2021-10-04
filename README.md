# Stock_program_transaction  
- [第四屆高雄盃程式交易競賽](https://bhuntr.com/tw/competitions/eqpkavrw0olm1wupbd)  

```
└── README.md 

├── main.py                 main programe
└── KPI.py                  evaluation 
```  

## Quick Run
To test the program, run `main.py`
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


## KPI (evaluation)  
To evaluate the report, run `KPI.py` to get the result csv: `KPI.csv`
```
python KPI.py
```
Ours KPI result is showed bellow:
| 總損益 | 總交易次數 | 平均損益 | 勝率 | 獲利因子 | 賺賠比 | 最大資金回落 | 夏普比率 | 是否超額交易 |
| :---: | :--------: | :-----: | :-: | :------: | :---: | :---------: | :-----: | :---------: |
|1474694| 874       | 1687.2929|0.675|3.0082    |1.4480 |600068       |0.3519   |否            |

