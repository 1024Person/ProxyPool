# 扩展模块
# 用来扩展代理池，当前代理池只支持一个网站的代理抓取
import requests
from concurrent.futures import ThreadPoolExecutor
from scrapy import Selector
from setting import USER_AGENT_LIST
from random import choice,randint
from scheduler import Scheduler
from threading import Lock
from pyquery import PyQuery as PQ
import time
import re
import os

headers={
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0"
}
kuai_base_url = "https://www.kuaidaili.com/free/inha/{}/"   # 快代理
qingting_base_url = "https://ip.jiangxianli.com/?page={}"   # 蜻蜓代理
_89_base_url = "https://www.89ip.cn/index_{}.html"          # 89代理
tomato_base_url = "https://www.fanqieip.com/free/China/{}"  # 番茄代理


# 第一个参数：page
# 第二个参数：headers，这个headers使用的crawler对象中的self.headers
def qingting_parse(args):
    print("正在爬取蜻蜓代理")
    page,headers_,url = args[0],args[1],args[2]
    print("第{}页开始执行解析函数".format(page))
    ips = []
    # url = qingting_base_url.format(page)
    headers_.setdefault('User-Agent',choice(USER_AGENT_LIST))
    try:
        response = requests.get(url,headers_)
        if response.status_code != 200:
            print("状态码不对")
            return None
    except requests.exceptions.ConnectionError:
        print("链接失败")
        return None
    
    doc = PQ(response.text)
    trs = doc('tbody > tr').items()
    for tr in trs:
        ip = tr('td:nth-child(1)').text()
        port = tr('td:nth-child(2)').text()
        if ip and port :
            proxy = ':'.join((ip,port))
            ips.append(proxy)
        else:
            print("代理未获取到")
    return ips


# 经过多次测试，快代理竟然禁封IP，这可了不得，所以这里需要进行延迟访问一下，
# 代理池还没构造出来，就被封了ip，这个就很尴尬，所以这里延迟访问一下
def kuai_parse(args):
    print("正在爬取快代理")
    page,headers_,url = args[0],args[1],args[2]
    print('第',page,'页开始执行解析函数')
    ips = []
    # url = kuai_base_url.format(page)
    ua = choice(USER_AGENT_LIST)
    # 这里也不知道为什么，程序又犯病，直接在setdefault里面随机选择一个user-agent的话，就会设置不上
    headers_['User-Agent'] = ua
    # print(headers_)
    try:
        response = requests.get(url,headers_,timeout=3)
    except requests.exceptions.ConnectionError as e:
        print(e.args)
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
    
    sleep = randint(6,12)  # 随机延迟访问6-11秒
    print(f"延迟{sleep}s后继续爬取，请稍等...")
    time.sleep(sleep)
    
    return ips

def _89_parse(args):
    print("正在爬取89代理")
    page,headers_,url = args[0],args[1],args[2]
    print('第',page,'页开始执行解析函数')
    ips = []
    # url = kuai_base_url.format(page)
    ua = choice(USER_AGENT_LIST)
    # 这里也不知道为什么，程序又犯病，直接在setdefault里面随机选择一个user-agent的话，就会设置不上
    headers_['User-Agent'] = ua
    # print(headers_)
    try:
        response = requests.get(url,headers_,timeout=3)
        if response.status_code != 200:
            print("状态码不对")
            return None
    except requests.exceptions.ConnectionError as e:
        print(e.args)
        print("连接失败")
        return None
    
    doc = PQ(response.text)
    trs = doc("tbody tr").items()
    for tr in trs:
        ip = tr('td:nth-child(1)').text()
        ip = re.sub('\s','',ip)
        port = tr('td:nth-child(2)').text()
        port = re.sub('\s','',port)
        if ip and port:
            proxy = ':'.join([ip,port])
            ips.append(proxy)
    
    sleep = randint(4,8)
    print("延迟{}s后再次进行请求，请稍等...".format(sleep))
    time.sleep(sleep)
    return ips





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

    scheduler = Scheduler(ip_from='web',base_url=_89_base_url,crawler_pages=100,crawler_parse_fn=_89_parse,save_m='a',save_path=f_path,client_path=f_path,name="89代理调度器")
    scheduler.start_scheduler()
    scheduler.shutdown()