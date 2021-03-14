# 调度模块
from crawler import CrawlerIp
from check import CheckIp
from save import SaveIp
from setting import *
import datetime


class Scheduler(object):
    # 参数：ip_from ：设置ip代理的来源，来自数据池(pool)还是网页(web)
    # 参数: base_url: 爬取代理的网站,默认是从setting文件中引入的
    # 参数: crawler_headers : 如果爬取代理ip得网站也需要定制headers的话，将这个参数传入，默认是使用setting中的headers
    # 参数：crawler_parse_fn: 解析爬取代理网站的函数，默认是使用CrawlerIp类自带的__get_ips方法(该方法只适用于当前setting文件中的base_url)
    # 参数：crawler_page :  爬取几页代理ip，默认是使用setting文件中全局配置的crawler_pages
    # 参数：save_m: 爬取下来的ip使用什么方式保存到文件中,默认按照setting全局配置中的save_mode来保存文件
    # 参数：save_path: 爬取下来的ip保存的路径,默认使用setting全局配置管理器中的csv_file_path
    # 参数：check_fn: 检测模块的检测函数，默认使用CheckIp类自带的__check_ip方法(该方法使用的检测网站和定制的headers来自setting文件的test_url和test_headers)
    # 参数：check_max_worker : 用来检测池中的线程数，默认是setting文件中的check_max_worker
    # 参数：test_url : 用来检测ip的网址
    # 参数：test_headers: 请求test_url是需要定制headers时，传入此参数，默认就是setting.py中的test_headers
    # 参数：name: 用来区分不同的调度器，默认就叫调度器
    # 参数：client_path ：连接器链接混沌池路径
    # 参数：client_good_path：连接器链接优质池路径
    def __init__(self, ip_from="pool", base_url=crawler_base_url, crawler_headers=crawler_headers, crawler_parse_fn=None,crawler_pages=crawler_pages, save_m=save_mode,save_path=csv_file_path,check_fn=None, check_max_workers=check_max_worker, test_url=test_url, test_headers=test_headers,name="调度器",client_path=csv_file_path,client_good_path=good_ips_file_path):
       self.start_time = datetime.datetime.now() # 记录调度器开始时间
       self.end_time = self.start_time           # 记录调度器结束时间
       self.name = name
       self.crawler = CrawlerIp(base_url=base_url,headers=crawler_headers,parse_fn=crawler_parse_fn,pages=crawler_pages,save_mode=save_m,save_path=save_path)
       self.ip_from = ip_from
       self.check = CheckIp(max_workers=check_max_worker,check_fn=check_fn,ts_url=test_url,ts_headers=test_headers,client_good_path=client_good_path,client_path=client_path)
       self.proxy_success_rate = 0.0
       
        # 开始调度代理池
    def start_scheduler(self):
        print("===="*20)
        print(f"{self.name}开始运行")
        self.__start_crawler_ip()
        self.__start_check_ip()
    

    # 结束调度
    def shutdown(self):
        self.end_time = datetime.datetime.now()
        self.check.shutdown()
        success_rate = self.check.get_success_rate()  # 获取代理池的成功率
        consume_time = self.end_time-self.start_time
        consume_time_str = "总共耗时：{}s".format(consume_time.total_seconds())
        print("调度器运行结束!\n",consume_time_str)
        
        message = """
        本次测试代理所用网址：{},
        本次测试代理成功率： {}%,
        """.format(self.check.test_url,success_rate)
        print(message)

        input("按任意键退出！")

    # 开始从网页上爬取代理ip
    def __start_crawler_ip(self):
        if self.ip_from == "web":
            print("开始抓取代理")
            self.crawler.crawl_and_save_ip()
            return True
        else:
            return None
    
    
    # 开始检测代理ip的可用性
    def __start_check_ip(self):
        self.check.start_check()

    
if __name__ == "__main__":
    scheduler = Scheduler(check_max_workers=150,ip_from='pool',crawler_pages=10,save_m='a')
    scheduler.start_scheduler()
    scheduler.shutdown()
    input("按任意键退出")


       
       