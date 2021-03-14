# 整合模块
# 发现在扩展的时候，因为这个只调用调度模块，导致第二个调度模块的检查器会将之前检查的代理ip再次检查一遍这样非常的费事，
# 已经检查过一次了就不需要在重复检查了，所以这里有两个解决方案：
# 1、重构scheduler模块，让他可以实现多个爬取器，然后一个检查器
# 2、添加整合模块，将每一个调度器的爬取器，爬去下来的ip存放到不同的文件中，然后检查的时候也只是检查这个调度器下的文件中的ip，
# 所有的调度器都结束工作之后，利用整合模块将所有文件中的ip整合到一个文件中
import sys
import os
import pandas as pd
sys.path.append(os.path.abspath('..'))
from scheduler import Scheduler
import extension
from setting import csv_file_path

class Union(object):
    # 参数 file_list: 需要整合的文件路径列表
    # 参数 is_del_file : 是否需要删除中间文件，默认为不删除
    def __init__(self,file_list,is_del_file = False):
        # self.save = SaveIp()
        self.file_list = file_list
        self.perpare_work()
        self.is_del_file = is_del_file
    
    # 检查工作：检查传入的file_list中的文件是否都存在，
    # 将不存在的文件路径移除删除
    def perpare_work(self):
        self.file_list = list(set(self.file_list))
        for path in self.file_list:
            if not os.path.exists(path):
                self.file_list.remove(path)

    
    def run(self):
        # save = SaveIp(mode='a')
        df = pd.DataFrame(data=[],columns=["ip","scores"])
        for file_path in self.file_list:
            file_ips = self.read(file_path)
            if file_ips is not None:
                df = df.append(file_ips)

        # scores = [10 for _ in range(len(ips))]
        # df = pd.DataFrame({"ip":ips,"scores":scores})
        df.to_csv(csv_file_path,index=None,mode='a',columns=None,header=False)  # 都保存到混沌代理池中
        print("文件整合成功")
        if self.is_del_file:
            print("正在删除临时文件。。。")
            self.delete_file()
            print("临时文件删除成功")

    def delete_file(self):
        for file_path in self.file_list:
            print(f"正在删除{file_path}")
            os.remove(file_path)


    
    def read(self,file_path):
        try:
            dt = pd.read_csv(file_path)
            dt.columns=["ip","scores"]
            return dt
        except:
            return None

if __name__ == "__main__":
    current_path = os.path.dirname(os.path.abspath(__file__))
    f_path = current_path+"\\89_ip.csv"
    # f_name = ["\\qingting.csv",'\\kuai.csv']
    f_path_list = [f_path]
    # kuai_scheduler = Scheduler(ip_from="web",base_url=kuai_base_url,crawler_parse_fn=kuai_parse,crawler_pages=200,save_m="a",save_path=f_path_list[1],client_path=f_path_list[1],name="快代理调度器")
    # kuai_scheduler.start_scheduler()
    # kuai_scheduler.shutdown()

    # qingting_scheduler = Scheduler(ip_from="web",base_url=qingting_base_url,crawler_pages=4,crawler_parse_fn=qingting_parse,save_path=f_path_list[0],save_m="a",client_path=f_path_list[0],name="蜻蜓代理调度器")
    # qingting_scheduler.start_scheduler()
    # qingting_scheduler.shutdown()

    # scheduler = Scheduler(ip_from='web',base_url=extension._89_base_url,crawler_pages=100,crawler_parse_fn=extension._89_parse,save_m='a',save_path=f_path,client_path=f_path,name="89代理调度器")
    # scheduler.start_scheduler()
    # scheduler.shutdown()
    union = Union(f_path_list)
    union.run()