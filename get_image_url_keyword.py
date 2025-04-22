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
import os

def get_pinterest_images(keyword, least_num=3, chromedriver_path=r'C:\Program Files (x86)\chromedriver-win64\chromedriver.exe', save_to_file=False):
    """
    根据关键词搜索Pinterest上的图片，返回至少指定数量的图片链接
    
    参数:
        keyword (str): 搜索关键词
        least_num (int): 需要返回的最少图片数量，默认为5
        chromedriver_path (str): ChromeDriver的路径
        save_to_file (bool): 是否将链接保存到文件，默认为False
        
    返回:
        list: 包含图片链接的列表，长度至少为least_num
    """
    cr_options = ChromeOptions()
    cr_options.add_argument("--start-maximized")  # 将浏览器最大化
    # 添加反爬虫措施
    cr_options.add_argument("--disable-blink-features=AutomationControlled")
    cr_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    cr_options.add_experimental_option("useAutomationExtension", False)
    cr_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36")
    
    # 无头模式，可选
    # cr_options.add_argument("--headless")
    
    service = Service(chromedriver_path)
    driver = Chrome(service=service, options=cr_options)
    
    # 执行JS去除webdriver特征
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    original_urls = set()  # 将图片的原始链接存储在集合内，自动去重
    lasts = []  # 用于检测是否到达页面底部
    
    try:
        # 构建搜索URL
        base_url = f'https://www.pinterest.com/search/pins/?q={keyword}'
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
        
        # 滚动页面直到找到足够的图片或达到最大尝试次数
        max_scroll_attempts = 30
        for i in range(max_scroll_attempts):
            # 如果已经找到足够的图片，退出循环
            if len(original_urls) >= least_num:
                print(f"已找到{len(original_urls)}张图片，满足要求的{least_num}张")
                break
                
            print(f'滚动次数: {i+1}, 当前已找到: {len(original_urls)}张图片')
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
                
            for element in all_elements:
                # 如果已经找到足够的图片，退出元素处理循环
                if len(original_urls) >= least_num:
                    break
                    
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
                        original_url = img_url.replace('236x', 'originals')
                        original_urls.add(original_url)
                        last = img_url
                except Exception as e:
                    print(f"处理图片时出错: {e}")
                    continue
                    
            if last:
                lasts.append(last)
            else:
                print("本页未找到任何有效图片")
                
            # 滚动页面
            driver.execute_script(f'window.scrollTo({i * 2000},{(i + 1) * 2000})')
            
            # 如果已经滑到底部且未找到足够的图片，退出循环
            if len(lasts) >= 3 and lasts[-1] == lasts[-2] and lasts[-1] == lasts[-3]:
                print("检测到连续3页相同内容，可能已到达底部")
                break
        
        # 将集合转换为列表
        result_urls = list(original_urls)
        
        # 确保返回至少least_num个链接，如果不足则填充None或重复链接
        if len(result_urls) < least_num:
            print(f"警告：只找到了{len(result_urls)}张图片，少于请求的{least_num}张")
            # 如果找到的图片数量不足，填充已有图片以达到least_num
            while len(result_urls) < least_num and len(result_urls) > 0:
                result_urls.append(result_urls[0])  # 重复使用第一张图片
        
        # 截取需要的长度
        result_urls = result_urls[:least_num]
        
        # 如果需要，保存到文件
        if save_to_file:
            filename = f"{keyword.replace(' ', '_')}_images.txt"
            with open(filename, 'w') as f:
                for url in result_urls:
                    f.write(url + "\n")
            print(f"图片链接已保存到文件: {filename}")
        
        return result_urls
    
    finally:
        # 确保浏览器关闭
        driver.quit()

# 示例使用
if __name__ == "__main__":
    
    keyword = 'Image, aerial view of Alcatraz Island'
    num_images = 5
    
    image_urls = get_pinterest_images(keyword=keyword, least_num=num_images, save_to_file=True)
    
    print(f"\n找到的图片链接:")
    for i, url in enumerate(image_urls, 1):
        print(f"{i}. {url}")
