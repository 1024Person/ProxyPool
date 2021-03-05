import requests
from scrapy import Selector
from setting import test_headers_2,test_url_2,headers,USER_AGENT_LIST
from random import choice
from concurrent.futures import ThreadPoolExecutor
from setting import base_url
from save import SaveIp

# 参数page：控制获取多少也代理
# 默认获取5页代理
def get_ips(pages):
    page = pages[0]
    global base_url
    ips = []

    url = base_url.format(page)
    headers.setdefault("User-Agent",choice(USER_AGENT_LIST))
    print("正在访问url:",url)
    response = requests.get(url,headers)
    headers.setdefault("User-Agent",choice(USER_AGENT_LIST))
    selector = Selector(response)
    trs = selector.xpath("/html/body/div[3]/div[2]/table/tbody//tr")
    for tr in trs:
        proxy = tr.xpath(".//td[1]/text()").extract_first()
        port = tr.xpath(".//td[2]/a/text()").extract_first()
        if proxy and port:
            ip = ":".join([proxy.strip(),port])
            # print("获取代理ip: {}".format(ip))
            ips.append(ip)
        else:
            continue
    return ips

# 参数page_count：要爬取多少页
# 默认爬取前四页
def send_ip(page_count = 4): 
    TheradPool = ThreadPoolExecutor(max_workers=3,thread_name_prefix="crawler")
    for i in range(1,page_count + 1):
        print(f"开始爬取第{i}页")
        save = SaveIp()
        futuer = TheradPool.submit(get_ips,(i,))
        futuer.add_done_callback(save.run)
        # ips+=futuer.result(timeout = 4)
        # print(futuer.result(timeout = 5))
    TheradPool.shutdown(wait = True)


if __name__ == "__main__":
    send_ip(5)
    # for ip in send_ip():
        # print("获取ip：",ip)





