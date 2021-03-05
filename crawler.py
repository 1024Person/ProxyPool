import requests
from scrapy import Selector
from setting import USER_AGENT_LIST,crawler_headers
from random import choice
from concurrent.futures import ThreadPoolExecutor
from setting import crawler_base_url
from save import SaveIp

# 参数page：控制获取多少也代理
# 默认获取5页代理
class CrawlerIp(object):
    # 参数：base_url 要爬取得代理网址 默认是setting文件中的base_url
    # 参数：headers 定制headers 默认是setting文件中的crawler_headers
    # 参数：page  要爬多少页 默认是5页
    # 参数：save_mode 爬取下来的代理ip保存到文件中的格式 默认是'w'
    # 参数：prase_fn 解析ip网页的解析方法，默认是使用该类自带的__get_ip
    #----------这两个参数---------# 参数：save_obj 用来保存代理ip的函数（可能会存储到数据库中，所以这里需要再次添加一个接口）
    #-----------有点难------------# 参数：save_obj_kwagrs  初始化save_obj对象需要用的参数
    def __init__(self,base_url=crawler_base_url,headers=crawler_headers,pages=5,save_mode="w",parse_fn=None):
        self.base_url = base_url
        self.pages = pages
        self.PoolSpider = ThreadPoolExecutor(max_workers=8,thread_name_prefix="Crawler Pool")
        self.headers = headers
        if not parse_fn:
            self.parse_fn = self.__get_ips
        else:
            self.parse_fn = parse_fn
    
   


    # 参数：parse_fn 和爬取网址对应的解析方法，从网页上获取代理ip
    # 注意：parse_fn函数的参数必须只有一个，page
    # page：要爬取得页数
    # 如果parse_fn没有传进来，那么就默认为self.__get_ips
    # 要爬取得网站需要在刚开始创建Crawler对象的时候，将爬取网站的分页网址基本格式（将页码那个参数空出来）传入进来
    def crawl_and_save_ip(self):
        for page in range(1,self.pages + 1):
            
            print("开始爬取第{}页".format(page))
            save = SaveIp(mode="a")
            future = self.PoolSpider.submit(self.parse_fn,(page,))
            future.add_done_callback(save.run)
        print("爬取完成")
        self.PoolSpider.shutdown(wait=True)

    # 从网页上爬取ip代理
    # 参数：pages 当前要爬取那一页  tuple类型
    def __get_ips(self,pages):
        ips = []
        page = pages[0]
        url = self.base_url.format(page)
        self.headers.setdefault('User-Agent',choice(USER_AGENT_LIST))
        print("正在访问url:",url)
        response = requests.get(url=url,headers=self.headers)
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
        

    
        



# def get_ips(pages):
#     page = pages[0]
#     global base_url
#     ips = []

#     url = base_url.format(page)
#     headers.setdefault("User-Agent",choice(USER_AGENT_LIST))
#     print("正在访问url:",url)
#     response = requests.get(url,headers)
#     headers.setdefault("User-Agent",choice(USER_AGENT_LIST))
#     selector = Selector(response)
#     trs = selector.xpath("/html/body/div[3]/div[2]/table/tbody//tr")
#     for tr in trs:
#         proxy = tr.xpath(".//td[1]/text()").extract_first()
#         port = tr.xpath(".//td[2]/a/text()").extract_first()
#         if proxy and port:
#             ip = ":".join([proxy.strip(),port])
#             # print("获取代理ip: {}".format(ip))
#             ips.append(ip)
#         else:
#             continue
#     return ips

# # 参数page_count：要爬取多少页
# # 默认爬取前四页
# def send_ip(page_count = 4): 
#     TheradPool = ThreadPoolExecutor(max_workers=3,thread_name_prefix="crawler")
#     for i in range(1,page_count + 1):
#         print(f"开始爬取第{i}页")
#         save = SaveIp()
#         futuer = TheradPool.submit(get_ips,(i,))
#         futuer.add_done_callback(save.run)
#         # ips+=futuer.result(timeout = 4)
#         # print(futuer.result(timeout = 5))
#     TheradPool.shutdown(wait = True)


# if __name__ == "__main__":
#     send_ip(5)
#     # for ip in send_ip():
#         # print("获取ip：",ip)




if __name__ == "__main__":
    crawler = CrawlerIp()
    crawler.crawl_and_save_ip()

