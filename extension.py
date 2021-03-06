# 扩展模块
# 用来扩展代理池，当前代理池只支持一个网站的代理抓取
import requests
from concurrent.futures import ThreadPoolExecutor
from scrapy import Selector
from setting import USER_AGENT_LIST
from random import choice
from scheduler import Scheduler
from threading import Lock

global_lock = Lock()
base_url = "https://www.kuaidaili.com/free/inha/{}/"
headers={
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0"
}
def parse(args):

    page,headers_ = args[0],args[1]
    print('第',page,'页开始执行解析函数')
    ips = []
    url = base_url.format(page)
    headers_.setdefault("User-Agent",choice(USER_AGENT_LIST))
    try:
        response = requests.get(url,headers_)
    except requests.exceptions.ConnectionError:
        print("连接失败")
        return None
    if not (response.status_code == 200):
        return None

    selector = Selector(response)
    trs = selector.xpath('/html/body/div/div[4]/div[2]/div/div[2]/table/tbody//tr')
    print("当前网页：{}  ，len(trs) = {}".format(response.url,len(trs)))
    if not len(trs):
        print("当前网页；{}未采集到的ip，len(trs) = {}".format(response.url,len(trs)))
    for tr in trs:
        ip = tr.xpath('./td[1]/text()').extract_first()
        port = tr.xpath('./td[2]/text()').extract_first()
        if ip and port:
            proxy = ":".join([ip,port])
            # print("获取代理：",proxy)
            ips.append(proxy)
        else:
            print("代理未获取到!\nip:{}\nport:{}\n".format(ip,port))
    return ips




if __name__ == "__main__":
    # crawler = CrawlerIp(save_path="./test_ips.csv",base_url=base_url,headers=headers,pages=20,save_mode='a',parse_fn=parse)
    # crawler.crawl_and_save_ip()
    scheduler = Scheduler(ip_from="web",base_url=base_url,crawler_headers=headers,crawler_parse_fn=parse,save_m='a')
    scheduler.start_scheduler()
    scheduler.shutdown()
