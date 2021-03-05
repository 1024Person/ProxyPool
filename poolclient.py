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
    def __init__(self):

        self.ips_df = pd.read_csv(csv_file_path)  # 读取出来的数据是dataframe形式的
        self.ips_df.columns = ["ip","scores"]
        if os.path.exists(good_ips_file_path):
            try:
                self.good_ips = pd.read_csv(good_ips_file_path)
            except pd.errors.EmptyDataError:
                self.good_ips = pd.DataFrame(data=[],columns=["ip","scores"])
        else:
            self.good_ips = pd.DataFrame(data=[],columns=["ip","scores"])  # 用来存放可用性强的ip
        self.good_ips.columns = ["ip",'scores']
        self.__sort_ip()  # 将"scores"的数据类型改变成int类型之后才可以进行排序，排序之后将可用性强的ip代理放到good_ips中去
        self.__update_ip_pool() # 先将代理池更新一下

    
    # ip生成器，返回Series对象，含有ip和socres两个字段
    def get_all_ip(self):
        for _ in range(self.ips_df.shape[0]):
            yield self.ips_df.iloc[_]

    # 随机获取一个Ip代理，如果可用
    def random_get_ip(self):
        self.__sort_ip()  # 先将ip进行排序，然后将最好用的ip放在里面
        if not self.good_ips.empty:
            ip = pd.Series(choice(self.good_ips.to_numpy()),index=["ip",'scores'])
            return ip
        else:
            return pd.Series(choice(self.ips_df.to_numpy()),index=["ip","scores"])

    
    # 参数：ip:Series对象，请求失败的ip代理
    # 请求失败的代理，将这个代理的分数减一
    def fail_ip(self,ip):
        print("请求失败\nip代理：{}".format(ip["ip"]))
        self.__sub_scores(ip)   # 代理ip分数减一
        self.__update_ip_pool() # 更新代理池
        self.__sort_ip()        # 将代理按照分数排序


    # 参数：ip:Series对象，请求成功的ip代理
    # 请求成功的代理，直接将分数设置为100
    def success_ip(self,ip):
        print("请求成功\nip代理：{}".format(ip["ip"]))
        self.__add_scores(ip)   # 代理ip分数设置为100
        self.__update_ip_pool() # 更新代理池
        self.__sort_ip()        # 将代理按照分数进行排序

      # 关闭代理池，将ips_df和good_ip都写入文件
    def shutdown(self):
        self.ips_df.to_csv(csv_file_path,mode='w',index=None,columns=None,header= False)
        print(self.good_ips)
        self.good_ips.drop_duplicates(subset=["ip",'scores'])
        print(self.good_ips)
        self.good_ips.to_csv(good_ips_file_path,mode="a",index=None,columns=None,header=False)


    # 参数：ip : 要查询分数的ip
    # 将查询到的ip和对应的分数返回出去，
    # 如果没有查询到，就直接返回None对象
    def query_scores_ip(self,ip):
        scores_ip = self.ips_df.loc[self.ips_df["ip"] == ip["ip"]]
        if scores_ip.empty:
            return None
        else:
            return scores_ip
        # self.ips_df.loc

    # 析构函数
    # def __del__(self):
    #     self.__close()

    # 更新代理池，将分数为0的都丢弃掉,并且将原来的代理池覆盖掉
    # 并且检查一下是否有重复的，直接将重复的都删除掉
    def __update_ip_pool(self):
        self.ips_df = self.ips_df.drop(index=(self.ips_df.loc[(self.ips_df["scores"] <= 0)].index))
        temp_ips = self.ips_df.to_numpy()
        dict_ips = dict(temp_ips)
        data = [{"ip":ip,"scores":scores} for ip,scores in dict_ips.items()]
        self.ips_df = pd.DataFrame(data)

        
    

    # 参数：ip ： 请求成功的代理ip
    # 将请求成功的代理设置为100分
    def __add_scores(self,ip):
        index = self.ips_df.loc[(self.ips_df["ip"] == ip["ip"])].index
        self.ips_df.loc[index,"scores"] = 100  # 成功的代理直接设置成一百

    # 将scores的数据类型从str改成int类型的
    # def __change_score_type(self):
    #     a = self.ips_df["scores"].to_numpy()
    #     b = [int(a[x]) for x in range(a.size)]
    #     # 注意这里需要设置一下index，否则的话就会发生scores的index和ips_df的index不匹配的问题
    #     scores = pd.Series(data=b,dtype=int,index=self.ips_df.index)
    #     self.ips_df["scores"] = scores

    # 参数：ip：Series对象，这里需要找到那个ip代理数据
    # 将相应的ip代理分数减1，每失败一次代理ip分数-1
    # 私有函数，不对外暴露接口
    def __sub_scores(self,ip):
        index = self.ips_df.loc[(self.ips_df["ip"] == ip["ip"])].index
        self.ips_df.loc[index,"scores"] -= 1  # 找到这个ip，将这个ip的分数建议

    # 更新ip的排列顺序，将分数最高的ip放在最上面
    def __sort_ip(self):
        # 按照降序排列
        self.ips_df.sort_values(by="scores",ascending = False, ignore_index=True,inplace=True)
        # 合并两个dataFrame
        self.good_ips.append(self.ips_df.loc[(self.ips_df["scores"]> 90)],ignore_index=True)
        print("sort",self.good_ips)



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
    # for ip in ProxyPool.get_all_ip():
    #     print("开始测试ip：\n",ip)
    # pirnt(ProxyPool.random_get_ip())
    # print(type(ProxyPool.random_get_ip()["scores"]))
    ip = ProxyPool.random_get_ip()
    ProxyPool.success_ip(ip)
    print(ProxyPool.query_scores_ip(ip))
    ProxyPool.shutdown()


#
#
# 问题：good_ips一直是空的，可能是顺序不对，还有就是good_ips在__init__的地方出错
# 
# 改进：test.py文件是用来改进爬虫部分的，改进成可以爬取很多网站的ip代理
# 
# 
# 
# 
#