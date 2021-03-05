# 保存模块
import csv
from setting import csv_file_path
import pandas as pd

class SaveIp(object):

    # 参数：csv_file_path 本地数据池的路径
    # 参数：mode          保存ip代理的方式
    def __init__(self,csv_file_path=csv_file_path,mode='w'):
        self.mode=mode
        self.csv_file_path = csv_file_path
        
    
    # 将ip保存到文件中吧，
    def run(self,future):
        ips = future.result()
        # ips_series = pd.Series(data=ips)
        scores = [10 for _ in range(len(ips))]
        # scores_series = pd.Series(data=scores)
        df = pd.DataFrame({"ip":ips,"scores":scores})
        df.to_csv(self.csv_file_path,index=None,mode=self.mode,columns=None,header=False)
        print("保存文件成功")
