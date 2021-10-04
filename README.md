# Stock_program_transaction  
- [第四屆高雄盃程式交易競賽](https://bhuntr.com/tw/competitions/eqpkavrw0olm1wupbd)  

```
└── README.md 

├── main.py                 main programe
└── KPI.py                  evaluation 


```  

## Quick Run
To test the program, run
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

## Strategy  
Calculate 1, 5 and 20 days average prices to find Golden cross, Death cross  
- Golden cross (a20 < a5 < a1): Long  
- Death cross (a20 > a5 > a1): Short



