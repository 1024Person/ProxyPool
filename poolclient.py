# 更新ip
# 具体来说就是从文件中获取ip（获取全部ip还是获取一个ip）
# 并且，可以更改ip的分数
import pandas as pd
from random import choice
from setting import csv_file_path
from setting import good_ips_file_path
import os

# print(csv_file_path)

class PoolClient(object):
    # 参数：csv_file_path       普通ip数据池所在路径
    #       good_ips_file_path  可用性强的ip所在路径
    #       client_save_mode    更新之后的ip的保存方式
    def __init__(self,csv_file_path=csv_file_path, good_ips_file_path=good_ips_file_path,client_save_mode='w'):
        self.csv_file_path = csv_file_path          
        self.good_ips_file_path = good_ips_file_path
        self.ips_df = pd.read_csv(self.csv_file_path)    # 读取出来的数据是dataframe形式的
        self.ips_df.columns = ["ip","scores"]       # 设置一下ips的列标签
        if os.path.exists(self.good_ips_file_path):      # 从good_ips_file_path中读取可用性强的ip，提前检查一下是否有这个文件
            try:
                self.good_ips = pd.read_csv(self.good_ips_file_path)  # 如果有这个文件，但是可能这个文件中没有数据，导致pandas报错
            except pd.errors.EmptyDataError:
                self.good_ips = pd.DataFrame(data=[],columns=["ip","scores"]) # 初始化good_ips对象
        else:
            self.good_ips = pd.DataFrame(data=[],columns=["ip","scores"])  
        self.good_ips.columns = ["ip",'scores']

        self.__update_ip_pool() # 先将数据池更新一下

    
    # ip生成器，返回Series对象，含有ip和socres两个字段
    def get_all_ip(self):
        for _ in range(self.ips_df.shape[0]):
            yield self.ips_df.iloc[_]



    # 随机获取一个Ip代理
    def random_get_ip(self):
        self.__sort_ip()  # 先将ip进行排序，然后将最好用的ip放在里面
        if not self.good_ips.empty:  # 如果有可用性强的ip
            ip = pd.Series(choice(self.good_ips.to_numpy()),index=["ip",'scores'])
            return ip
        else:                       # 没有的话，随机选一个
            return pd.Series(choice(self.ips_df.to_numpy()),index=["ip","scores"])




    # 参数：ip:Series对象，请求失败的ip代理
    # 请求失败的代理，将这个代理的分数减一
    def fail_ip(self,ip):
        new_ip = self.__sub_scores(ip)   # 代理ip分数减一
        self.__update_ip_pool() # 更新一下数据池
        print("请求失败\nip代理：{}\n代理分数：{}".format(new_ip["ip"],new_ip["scores"]))  # 更新之后再将代理ip的分数显示出来

    # 参数：ip:Series对象，请求成功的ip代理
    # 请求成功的代理，直接将分数设置为100
    def success_ip(self,ip):
        new_ip = self.__add_scores(ip)   # 代理ip分数设置为100
        self.__update_ip_pool() # 更新一下数据池
        print("请求成功\nip代理：{}\n代理分数：{}".format(new_ip["ip"],new_ip["scores"]))  # 更新之后再将代理ip的分数显示出来





    # 关闭代理池，将ips_df和good_ip都写入文件
    # return 返回代理池的合格率
    def shutdown(self):
        self.__update_ip_pool()  # 关闭数据池之前将数据池更新一下
        self.__sort_ip()
        print("正在关闭数据池")
        self.ips_df.to_csv(self.csv_file_path,mode='w',index=None,columns=None,header= False)
        # print(self.good_ips)
        self.good_ips.drop_duplicates(subset=["ip",'scores'])
        # print(self.good_ips)
        self.good_ips.to_csv(self.good_ips_file_path,mode="w",index=None,columns=None,header=False)
        # 打印代理池关闭成功
        print("数据池关闭成功")
        # return self.rate


    # 参数：ip : 要查询分数的ip
    # 将查询到的ip和对应的分数返回出去，
    # 如果没有查询到，就直接返回None对象
    def query_scores_ip(self,ip):
        scores_ip = self.ips_df.loc[self.ips_df["ip"] == ip["ip"]]
        if scores_ip.empty:
            return None
        else:
            return scores_ip


    # ips_df:  删掉分数小于0的，删除重复的
    # 
    # good_ips: 删除分数小于或者等于90的，删除重复的
    #           添加分数大于90分的
    def __update_ip_pool(self):
        print("df.shape:",self.ips_df.shape)
        self.ips_df = self.ips_df.drop(index=(self.ips_df.loc[(self.ips_df["scores"] <= 0)].index))
        self.ips_df = self.ips_df.drop_duplicates(subset=["ip"])  # 将重复的ip合并
        # 合并两个dataFrame
        # 将分数大于90分的ip代理，放到good_ips中
        ip = self.ips_df.loc[(self.ips_df["scores"]> 90)]
        self.good_ips = self.good_ips.append(ip,ignore_index=True)
        self.good_ips = self.good_ips.drop_duplicates(subset=["ip"])
        # 将分数小于90或者等于90分的从good_ips中删除
        self.good_ips = self.good_ips.drop(index=(self.good_ips.loc[(self.good_ips["scores"] <= 90)].index))  # 删除good_ips中分数小于90分的
        print("df.shape",self.ips_df.shape)

        
    

    # 参数：ip ： 请求成功的代理ip
    # 将请求成功的代理设置为100分
    # 同时将这个ip放到good_ips中去
    def __add_scores(self,ip):
        index = self.ips_df.loc[(self.ips_df["ip"] == ip["ip"])].index
        self.ips_df.loc[index,"scores"] = 100  # 成功的代理直接设置成一百
        back_ip = self.ips_df.loc[index]       # 返回出去的更新之后ip
        return back_ip                         # return back_ip



    # 参数：ip：Series对象，这里需要找到那个ip代理数据
    # 将相应的ip代理分数减1，每失败一次代理ip分数-1
    # 私有函数，不对外暴露接口
    def __sub_scores(self,ip):
        index = self.ips_df.loc[(self.ips_df["ip"] == ip["ip"])].index
        self.ips_df.loc[index,"scores"] -= 1  # 找到这个ip，将这个ip的分数建议
        back_ip = self.ips_df.loc[index]
        index = self.good_ips.loc[(self.good_ips["ip"] == ip["ip"])].index
        if not index.empty:
            try:
                self.good_ips.loc[index,"scores"] -= 1 # 找到这个ip将这个ip减一分
            except:
                print(index.empty,'\t\t\t',index)
        return back_ip



    # 更新ip的排列顺序，将分数最高的ip放在最上面
    def __sort_ip(self):
        # 按照降序排列
        self.ips_df.sort_values(by="scores",ascending = False, ignore_index=True,inplace=True)


    def test(self):
        print(self.ips_df.shape)
        print(self.ips_df.iloc[-1])

#   |---------------------------------------------------------------------------    
#   |    # 注意这里的scores是字符串对象，需要先转化为int对象，                    明
#   |    # 所以这里就需要将scores列提取出来，将里面的数据处理一下，                天
#   |     # 然后再放回到ips_df里面，这个应该在__init__函数里面完成的              再
#   |     #a = self.ips_df["scores"].to_numpy()   字符串列表                    写
#   |     #b = [int(a[x]) for x in range(a.size)] 整数列表                      @
#   |     #scores = pd.Series(data=b,dtype=int)   Series对象                    @
#   |     #self.ips_df["scores"] = scores         更新一下scores列的数据         @
#   |                                                                           @
#   | ---------------------------------------------------------------------------
# self.good_ips = self.ips_df.loc[(self.ips_df["scores"])]


if __name__ == "__main__":
    ProxyPool = PoolClient()
    ip = ProxyPool.random_get_ip()
    ProxyPool.success_ip(ip)
    print(ProxyPool.query_scores_ip(ip))
    print("当前good_ips中的数据：")
    print(ProxyPool.good_ips)
    ProxyPool.shutdown()
