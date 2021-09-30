import csv
import os
import pandas as pd
from tqdm import tqdm


def combine_all_csv(csv_path=None, save_path=None, save_name='total_data'):
    name_list = os.listdir(csv_path)
    with open(save_path + '/' + save_name + '.csv', 'w', newline='') as f:
        w = csv.writer(f)
        for name in name_list:
            print('Day:', name)
            day = name[:8]
            data = pd.read_csv(csv_path + name)
            data = data.iloc[:, :].values
            for i, each in enumerate(tqdm(data)):
                w.writerow([day, *data[i]])
    f.close()


if __name__ == '__main__':
    wantTransCsvPath = '../StockData/'
    saveCsvPath = '../'
    save_name = 'total_data'
    combine_all_csv(csv_path=wantTransCsvPath, save_path=saveCsvPath, save_name=save_name)
