# 保存模块
import csv
from setting import csv_file_path
import pandas as pd

class SaveIp(object):

    # def __init__(self):
        # self.__file =open(file=file_path,mode="w",encoding='utf8')
        # self.wirter = csv.writer(self.__file)
        # 
    
    # 将ip保存到文件中吧，
    def run(self,future):
        ips = future.result()
        # ips_series = pd.Series(data=ips)
        scores = [10 for _ in range(len(ips))]
        # scores_series = pd.Series(data=scores)
        df = pd.DataFrame({"ip":ips,"scores":scores})
        df.to_csv(csv_file_path,index=None,mode='a',columns=None,header=False)
        print("保存文件成功")



    
    # def __del__(self):
        # self.__file.close()
        
