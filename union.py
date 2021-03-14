# 整合模块
# 发现在扩展的时候，因为这个只调用调度模块，导致第二个调度模块的检查器会将之前检查的代理ip再次检查一遍这样非常的费事，
# 已经检查过一次了就不需要在重复检查了，所以这里有两个解决方案：
# 1、重构scheduler模块，让他可以实现多个爬取器，然后一个检查器
# 2、添加整合模块，将每一个调度器的爬取器，爬去下来的ip存放到不同的文件中，然后检查的时候也只是检查这个调度器下的文件中的ip，
# 所有的调度器都结束工作之后，利用整合模块将所有文件中的ip整合到一个文件中
from save import SaveIp             # 很明显，需要保存文件
import pandas as pd
from scheduler import Scheduler
import os
from extension import *

class Union(object):
    # 参数 file_list: 需要整合的文件路径列表
    def __init__(self,file_list):
        # self.save = SaveIp()
        self.file_list = file_list
    
    def run(self):
        save = SaveIp(mode='a')
        ips = []
        for file_path in self.file_list:
            file_ips = self.read(file_path)
            if file_ips:
                ips+=file_ips
        
        save.run(ips)
    
    def read(self,file_path):
        try:
            dt = pd.read_csv(file_path)
            ips = dt["ip"]
            return list(ips)
        except:
            return None

if __name__ == "__main__":
    current_path = os.path.dirname(os.path.abspath(__file__))
    f_name = ["\\qingting.csv",'\\kuai.csv']
    f_path_list = [current_path+_ for _ in f_name]
    kuai_scheduler = Scheduler(ip_from="web",base_url=kuai_base_url,crawler_parse_fn=kuai_parse,crawler_pages=20,save_m="a",save_path=f_path_list[1],client_path=f_path_list[1],name="快代理调度器")
    kuai_scheduler.start_scheduler()
    kuai_scheduler.shutdown()

    qingting_scheduler = Scheduler(ip_from="web",base_url=qingting_base_url,crawler_pages=4,crawler_parse_fn=qingting_parse,save_path=f_path_list[0],save_m="a",client_path=f_path_list[0],name="蜻蜓代理调度器")
    qingting_scheduler.start_scheduler()
    qingting_scheduler.shutdown()

    union = Union(f_path_list)
    union.run()