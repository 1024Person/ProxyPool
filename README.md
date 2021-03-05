# 代理池使用说明

## 项目目录

> -- **ProxyPool**
>
> ​	|	
>
> ​	|	-- setting.py  	------> 全局配置
>
> ​	|	-- check.py    	------> 检测ip可用性模块
>
> ​	|	-- crawler.py  	------> 爬取ip代理模块
>
> ​	|	-- poolclient.py  ------> 连接代理池模块
>
> ​	|	-- save.py 	     ------> 保存模块
>
> ​	|	-- scheduler.py  -------> 调度模块



## setting文件配置说明

在setting文件中有默认的test_url和相应的test_headers,以及base_url