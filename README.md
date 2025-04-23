# 利用爬虫(based on selenium)获取图片
*所有程序都是本地运行* 

配好环境后，先用 `get_image_url.py` 测试一下是否正确
`get_image_url_keyword.py` 是根据一个关键词搜索对应的前least_num(e.g. 5)张图片，返回一个列表，长度为 least_num，其中包含了不为None的爬到与关键词相关的图片链接
`step_crawling.py` 主要爬的程序

如果出现卡在22%报错，修改get_image_url_keyword为headless模式，   
`cr_options.add_argument("--headless")  # 启用无头模式`
`# cr_options.add_argument("--start-maximized")  # 取消将浏览器最大化`

chromedriver_file的格式类似于`chromedriver_path=r'C:\Program Files (x86)\chromedriver-win64\chromedriver.exe'`，在https://developer.chrome.google.cn/docs/chromedriver/downloads?hl=zh-cn根据自己的chrome版本下载。


最终 output json 格式为
```
meta_data: # other information, so that we can get where the keyword from.
keyword: # the input keyword
image_links:[] # store it as a list
```


## 配置信息
*查看selenium* 的配置方法
Chrome Driver 最新版本下载
https://googlechromelabs.github.io/chrome-for-testing/

Check 一下网上的 Chrome Driver 配置信息和 Chrome 的版本对应关系

Mac \ Windows 的教程可能不一样


Reference
[1] https://blog.csdn.net/crayonjingjing/article/details/124921047
