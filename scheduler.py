# 调度模块
from crawler import CrawlerIp
from check import CheckIp
from save import SaveIp
from setting import *

class Scheduler(object):
    # 参数：ip_from ：设置ip代理的来源，来自数据池(pool)还是网页(web)
    # 参数: base_url: 爬取代理的网站,默认是从setting文件中引入的
    # 参数: crawler_headers : 如果爬取代理ip得网站也需要定制headers的话，将这个参数传入，默认是使用setting中的headers
    # 参数：crawler_parse_fn: 解析爬取代理网站的函数，默认是使用CrawlerIp类自带的__get_ips方法(该方法只适用于当前setting文件中的base_url)
    # 参数：crawler_page :  爬取几页代理ip，默认是使用setting文件中全局配置的crawler_pages
    # 参数：check_fn: 检测模块的检测函数，默认使用CheckIp类自带的__check_ip方法(该方法使用的检测网站和定制的headers来自setting文件的test_url和test_headers)
    # 参数：check_max_worker : 用来检测池中的线程数，默认是setting文件中的check_max_worker
    # 参数：test_url : 用来检测ip的网址
    # 参数：test_headers: 请求test_url是需要定制headers时，传入此参数，默认就是setting.py中的test_headers
    def __init__(self, ip_from="pool", base_url=crawler_base_url, crawler_headers=crawler_headers, crawler_parse_fn=None,crawler_pages=crawler_pages, check_fn=None, check_max_workers=check_max_worker, test_url=test_url, test_headers=test_headers):
       self.crawler = CrawlerIp(base_url=base_url,headers=crawler_headers,parse_fn=crawler_parse_fn,pages=crawler_pages)
       self.ip_from = ip_from
       self.check = CheckIp(max_workers=check_max_worker,check_fn=check_fn,ts_url=test_url,ts_headers=test_headers)
       self.proxy_success_rate = 0.0
       
        # 开始调度代理池
    def start_scheduler(self):
        print("开始调度代理池")
        self.__start_crawler_ip()
        self.__start_check_ip()
    

    # 结束调度
    def shutdown(self):
        print("结束调度代理")
        self.check.shutdown()
        success_rate = self.check.get_success_rate()  # 获取代理池的成功率
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
    scheduler = Scheduler(check_max_workers=150)
    scheduler.start_scheduler()
    scheduler.shutdown()


       
       