import requests
from scrapy import Selector
from setting import USER_AGENT_LIST,crawler_headers,save_mode
from random import choice
from concurrent.futures import ThreadPoolExecutor
from setting import crawler_base_url,csv_file_path
from save import SaveIp

# 参数page：控制获取多少也代理
# 默认获取5页代理
class CrawlerIp(object):
    # 参数：base_url : 要爬取得代理网址 默认是setting文件中的base_url
    # 参数：headers  : 定制headers 默认是setting文件中的crawler_headers
    # 参数：page     : 要爬多少页 默认是5页
    # 参数：save_mode: 爬取下来的代理ip保存到文件中的格式 默认是'w'
    # 参数：prase_fn : 解析ip网页的解析方法，默认是使用该类自带的__get_ip
    # 参数：save_fn  : 保存ip的函数，默认是SaveIp的run方法
    # 参数：save_path: 保存文件的路径
    #----------这两个参数---------# 参数：save_obj 用来保存代理ip的函数（可能会存储到数据库中，所以这里需要再次添加一个接口）
    #-----------有点难------------# 参数：save_obj_kwagrs  初始化save_obj对象需要用的参数
    def __init__(self,base_url=crawler_base_url,headers=crawler_headers,pages=5,save_mode=save_mode,parse_fn=None,save_path=csv_file_path):
        self.save_mode = save_mode
        self.base_url = base_url
        self.pages = pages
        self.PoolSpider = ThreadPoolExecutor(max_workers=8,thread_name_prefix="Crawler Pool")
        self.headers = headers
        self.save_path = save_path
        if not parse_fn:
            self.parse_fn = self.__get_ips
        else:
            self.parse_fn = parse_fn
    
   
    # 要爬取得网站需要在刚开始创建Crawler对象的时候，
    # 将爬取网站的分页网址基本格式（将页码那个参数空出来）传入进来
    def crawl_and_save_ip(self):
        for page in range(1,self.pages + 1):
            print("开始爬取第{}页".format(page))
            save = SaveIp(mode=self.save_mode,csv_file_path=self.save_path)
            future = self.PoolSpider.submit(self.parse_fn,(page,self.headers))
            ips = future.result()
            save.run(ips)
            # future.add_done_callback(save.run)
        print("爬取完成")
        self.PoolSpider.shutdown(wait=True)

    # 从网页上爬取ip代理
    # 参数：pages 当前要爬取那一页  tuple类型
    def __get_ips(self,args):
        ips = []
        page = args[0]
        url = self.base_url.format(page)
        self.headers.setdefault('User-Agent',choice(USER_AGENT_LIST))
        # print("正在访问url:",url)
        try:
            response = requests.get(url=url,headers=self.headers,timeout=15)
        except requests.exceptions.ConnectionError:
            return None
        except requests.exceptions.ConnectTimeout:
            return None
        except requests.exceptions.ReadTimeout:
            return None
        except: 
            return None
        self.headers.setdefault("User-Agent",choice(USER_AGENT_LIST))
        selector = Selector(response)
        trs = selector.xpath("/html/body/div[3]/div[2]/table/tbody//tr")
        for tr in trs:
            proxy = tr.xpath(".//td[1]/text()").extract_first()
            port = tr.xpath(".//td[2]/a/text()").extract_first()
            if proxy and port:
                ip = ":".join([proxy.strip(),port])
                print("获取代理ip: {}".format(ip))
                ips.append(ip)
            else:
                continue
        return ips


if __name__ == "__main__":
    crawler = CrawlerIp(pages=10)
    crawler.crawl_and_save_ip()

