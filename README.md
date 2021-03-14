# 代理池使用说明

## 前言
做爬虫的，一定会和各种反爬手段做斗争，
禁封代理IP是反爬的手段之一，当然也有解决的手段就是
1. 从各大平台上买付费代理（这些代理都是一段时间可用，过了期限之后就不能用了）
2. 从网上（github）找各种的代理池，当然也可以自己搭建一个代理池
本项目就是自己搭建的一个简易代理池，没有用到数据库，没有用到web api，
个人感觉这个代理池是真的简陋，但是可扩展性却也是很高

## 代理池的抽象模型

该代理池的几大模块

1. 数据池（主体）
2. 保存器（功能）
3. 连接器（接口）
4. 调度器（引擎）
5. 检查器（功能）
6. 爬取器 （功能）

代理池几大模块之间的运行流程：



1. 开启**调度器**

2. 首先，**调度器**命令爬取器向**Internet**发起请求**requests**，然后**Internet**返回响应**response**给**爬取器**

3. **爬取器**从 **response**中提取 **Ip**交给保存器，**保存器**将 **爬取器**传递过来的 **Ip**保存到 **混沌池**中

4. **连接器**连接**数据池**，同时获得**优质池**和**混沌池**的管理权限

5. **调度器**命令**检查器**开始检查 **Ip**并且评分，

6. **检查器**通过**连接器**获得 **数据池**中的所有 **Ip**，

7. **检查器**通过对所有的 **Ip**进行检查评判，将检查结果**result**返回给 **连接器**，

8. **连接器**根据返回的结果对 **Ip**进行分类，并且将更新之后的代理 **Ip**保存到数据池中

9. **调度器**下令：关闭各个组件，待各个组件确认关闭之后， **调度器**关闭

   注意：**连接器**内置了 **IP** 分数管理机制

<img src=".\Proxy_Pool_Abstraction.png" alt="Proxy_Pool_Abstraction" style="zoom:60%;" />

## 项目结构

> -- **ProxyPool**
>
> ​		|	
>
> ​		|	-- setting.py  	------> 全局配置
>
> ​		|	-- check.py    	------> 检测ip可用性模块
>
> ​		|	-- crawler.py  	------> 爬取ip代理模块
>
> ​		|	-- poolclient.py  ------> 连接代理池模块
>
> ​		|	-- save.py 	     ------> 保存模块
>
> ​		|	-- scheduler.py  -------> 调度模块
>
> ​		|	-- ip.csv             -------> 混沌池
>
> ​		|	-- good_ips.csv  -------> 优质池

### setting全局配置

<font size=3 color=#33ff99>setting.py</font>文件中主要记录了各种默认的全局配置

- test_url,test_headers : 用来测试ip代理的网站，以及相应的headers
- csv_file_path,good_ips_file_path:保存ip的“数据池”路径，以及保存可用性高的ip“数据池”路径
- crawler_pages,crawler_base_url,crawler_headers:爬取代理网页的页数，爬取代理网页的基本格式（page参数空出来'{}'之后的网址）,以及ip网站相应的headers
- check_max_worker:检测代理可用性的线程池中线程的数量
- USER_AGENT_LIST:user_agent列表

## 优点

- 可扩展性强
- 稳定
- 配置丰富，非常灵活
- 适用性强

## 缺点

- 没有使用数据库，只是使用了本地文件操作，启动和结束程序时，耗时长，处理操作繁琐，同时这也导致了该数据库只能是轻量级的代理池（如果数据池中的数据大小达到1G的程度，那么光把文件中的ip数据读取到程序中需要的时间就是非常恐怖的！！）
- 可扩展部分还是受到参数的限制，也就是说传递的函数的参数必须按照一定的格式和数据类型

  