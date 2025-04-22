from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import random

cr_options = ChromeOptions()
cr_options.add_argument("--start-maximized")  # 将浏览器最大化
# 添加反爬虫措施
cr_options.add_argument("--disable-blink-features=AutomationControlled")
cr_options.add_experimental_option("excludeSwitches", ["enable-automation"])
cr_options.add_experimental_option("useAutomationExtension", False)
cr_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36")

#  Input keywords
queries = [           # 想要搜索分类的关键词
    # '頭貼 卡通',
    '海盗船 头像',
    # '可愛頭貼',
    # '文字 头像',
    # '人物 头像',
    # 'ins风 头像',
    # '油画 头像',
    # '摄影 风景',
]

service = Service('/usr/local/bin/chromedriver')
driver = Chrome(service=service, options=cr_options)

# 执行JS去除webdriver特征
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

print('Size: ' + str(driver.get_window_size()))   
# 这里输出浏览器尺寸是为了后面调试每次滑动的最佳高度
original_urls = set()   # 将图片的原始链接存储在集合内，自动去重
lasts = []

for query in queries:
    base_url = f'https://www.pinterest.com/search/pins/?q={query}'
    driver.get(base_url)
    
    # 等待页面加载
    time.sleep(5)
    
    # 尝试多种选择器
    selectors = [
        # 旧选择器
        '//div[@data-test-id="pin-visual-wrapper"]/div[1]/div[1]/img',
        # 新的更通用选择器
        '//div[contains(@class, "Pin")]//img',
        '//img[@loading="auto"]',
        '//img[contains(@srcset, "i.pinimg.com")]',
        '//img[contains(@src, "i.pinimg.com")]',
        # 最通用的选择器
        '//img'
    ]
    
    for i in range(30):     # 这里为了保证滑到底部，所以循环次数写到了30，但其实可能不需要30次
        print('i----------',i)  # 输出i来记录滑动了几次（翻了几页）
        last = None  # 初始化last变量
        
        # 随机等待时间，模拟人类行为
        time.sleep(2 + random.random() * 2)
        
        # 尝试不同的选择器直到找到图片
        all_elements = []
        for selector in selectors:
            all_elements = driver.find_elements(By.XPATH, selector)
            if len(all_elements) > 0:
                print(f"使用选择器: {selector}")
                print(f"找到元素数量: {len(all_elements)}")
                break
        
        if len(all_elements) == 0:
            print("没有找到任何图片元素")
            continue
            
        print('-------------------------------------------------------------------')
        for element in all_elements:
            try:
                img_url = element.get_attribute('src')
                if not img_url:
                    # 尝试从srcset获取
                    srcset = element.get_attribute('srcset')
                    if srcset:
                        # 解析srcset获取最大尺寸图片
                        src_list = srcset.split(',')
                        if src_list:
                            img_url = src_list[-1].strip().split(' ')[0]
                
                if img_url and 'i.pinimg.com' in img_url:
                    print(f"找到图片: {img_url}")
                    original_url = img_url.replace('236x', 'originals')
                    original_urls.add(original_url)
                    last = img_url
            except Exception as e:
                print(f"处理图片时出错: {e}")
                continue
                
        if last:
            print(f"最后一张图片: {last}")
            lasts.append(last)
        else:
            print("本页未找到任何有效图片")
            
        # 滚动页面
        driver.execute_script(f'window.scrollTo({i * 2000},{(i + 1) * 2000})')
        
        # 如果已经滑到底部，则退出循环
        if len(lasts) >= 3 and lasts[-1] == lasts[-2] and lasts[-1] == lasts[-3]:
            print("检测到连续3页相同内容，可能已到达底部")
            break

print('lasts: ',lasts)
print('*****************************************')
print(f"总共找到 {len(original_urls)} 张图片")

for item in original_urls:
    with open('ddd.txt','a+') as f:  # 最后将爬取的链接写入ddd.txt，注意要是a+追加方式，因为该代码可能要跑几遍（毕竟科学上网不稳定，可能有图片第一遍没有获取成功）
        f.writelines(item + "\n")

driver.quit()
print("完成！图片链接已保存到ddd.txt")
