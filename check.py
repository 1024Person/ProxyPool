# 检测模块
from poolclient import PoolClient 
from setting import test_url,test_headers,USER_AGENT_LIST
from random import choice
from concurrent.futures import ThreadPoolExecutor
import requests

class CheckIp():
    def __init__(self):
        self.poolclient = PoolClient()
        self.test_url = test_url
        self.test_header = test_headers
        self.CheckPool = ThreadPoolExecutor(max_workers=4,thread_name_prefix="CheckIp")

    # 开启检查池
    def start_check(self):
        print("{}开始运行".format(self.CheckPool._thread_name_prefix))
        for ip in self.poolclient.get_all_ip():
            print("正在检测ip代理：",ip)
            future = self.CheckPool.submit(self.__check,(ip,))
            future.add_done_callback(self.__update_pool)
        
        self.CheckPool.shutdown(wait=True)
    
    # 关闭检查池
    def shutdown(self):
        self.poolclient.shutdown()  # 关闭数据池

    
    # 线程池的回调函数，用来更新代理池的分数
    def __update_pool(self,future):
        result = future.result()
        success_or_fail, ip= result
        if success_or_fail:
            self.poolclient.success_ip(ip)
        else:
            self.poolclient.fail_ip(ip)



    # 参数：ip:Series对象，当前要检测的ip代理
    # return:
    #   bool 返回当前ip是否可用
    #   ip   设置分数的时候需要
    def __check(self,ip):
        proxy = {
            "http":"http://"+ip["ip"],
            "https":"https://"+ip["ip"]
        }
        try:
            response = requests.get(url=self.test_url,headers=self.test_header,proxies=proxy,timeout=15)
            if response.status_code == 200:
                return (True,ip)
            else:
                print("请求状态码不对")
                print("status_code:",response.status_code)
                return (False,ip)
        except requests.exceptions.ProxyError:
            print("代理出错")
            return (False,ip)
        except requests.exceptions.ConnectTimeout:
            print("请求太慢，直接pass掉了")
            return (False,ip)
        except requests.exceptions.TooManyRedirects:
            print("我也不知道怎么就出错了")
            return (False,ip)
        except:
            return (False,ip)
        

if __name__ == "__main__":
    check = CheckIp()
    check.start_check()
    check.shutdown()

