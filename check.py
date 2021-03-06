# 检测模块
from poolclient import PoolClient 
from setting import test_url,test_headers,USER_AGENT_LIST,check_max_worker
from random import choice
from concurrent.futures import ThreadPoolExecutor
import requests

class CheckIp():
    # 参数：check_max_worker: 线程池中的线程数，默认是从settings中引入的100个，可以修改setting文件中的全局配置，也可以在创建的时候自己再传入一个数字，推荐后一种方法
    # 参数：check_fn : 检查ip可用性的方法，默认是CheckIp自带的__check方法，如果传入定制的check_fn这个函数的参数必须是一个pd.Series对象，这个对象的index是["ip","scores"]
    # 参数：test_url : 用来检测ip的网址，默认使用setting文件中的test_url
    # 参数：test_headers : 定制headers,默认使用setting文件中的test_headers
    def __init__(self,max_workers=check_max_worker,check_fn=None,ts_url=test_url,ts_headers=test_headers):
        self.__total_ip_count = 0   # 代理池中代理的数量
        self.__success_ip_count = 0  # 代理池中成功可用代理的数量
        self.poolclient = PoolClient()
        self.test_url = ts_url
        self.test_header = ts_headers
        self.CheckPool = ThreadPoolExecutor(max_workers=check_max_worker,thread_name_prefix="CheckIp")
        if not check_fn :
            self.check_fn = self.__check
        else:
            self.check_fn = check_fn

    # 开启检查池
    # 参数：check_fn 检测函数，默认为self.__check 
    # 注意：check_fn 函数只能有一个参数：ip(Series对象)
    # 要检测代理ip的网站，需要从setting.py里设置test_url,想定制headers也需要从setting.py文件中设置test_headers
    def start_check(self):
        print("{}开始运行".format(self.CheckPool._thread_name_prefix))
        for ip in self.poolclient.get_all_ip():
            future = self.CheckPool.submit(self.check_fn,(ip,))
            future.add_done_callback(self.__update_pool)
        
        
    
    # 关闭检查池
    def shutdown(self):
        print("关闭检查池")
        self.CheckPool.shutdown(wait=True)
        print("检查池关闭成功")
        self.poolclient.shutdown()  # 关闭数据池
        
    # 获取代理池成功率
    def get_success_rate(self):
        return self.__success_ip_count / self.__total_ip_count
    
    # 线程池的回调函数，用来更新代理池的分数
    def __update_pool(self,future):
        self.__total_ip_count += 1
        result = future.result()
        success_or_fail, ip= result
        if success_or_fail:
            self.__success_ip_count += 1
            self.poolclient.success_ip(ip)
        else:
            self.poolclient.fail_ip(ip)
        print("===" * 20)  # 将每次测试结果隔开，


    # 参数：ip:Series对象，当前要检测的ip代理
    # return:
    #   bool 返回当前ip是否可用
    #   ip   设置分数的时候需要
    def __check(self,ip):
        ip = ip[0]  # 先将ip的Series对象获取出来
        proxy = {
            "http":"http://"+ip["ip"],
            "https":"https://"+ip["ip"]
        }
        try:
            response = requests.get(url=self.test_url,headers=self.test_header,proxies=proxy,timeout=30)
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
        except requests.exceptions.ReadTimeout:
            print("ReadTimeout")
            return (False,ip)
        except:
            return (False,ip)

        

if __name__ == "__main__":
    check = CheckIp()
    check.start_check()
    check.shutdown()
    message = """
    本次测试网址：  {},
    本次测试成功率：{}%,
    """.format(check.test_url,check.get_success_rate())
    print(message)

