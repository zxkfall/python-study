from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time
import requests
from bs4 import BeautifulSoup

# 初始化WebDriver，这里使用Chrome
driver = webdriver.Chrome(executable_path='path_to_chromedriver.exe')

# 打开大众点评商品页面，这是你要爬取信息的页面
url = 'https://www.dianping.com/shenzhen/ch10/g119r1572'
driver.get(url)

# 处理验证码
captcha_element = driver.find_element_by_css_selector('.captcha-image')
if captcha_element:
    # 获取滑块元素
    slider_element = driver.find_element_by_css_selector('.slider')

    # 获取验证码图片位置和滑块位置
    captcha_location = captcha_element.location
    slider_location = slider_element.location

    # 获取滑块宽度
    slider_width = slider_element.size['width']

    # 计算滑块需要滑动的距离
    slide_distance = captcha_location['x'] + slider_width / 2 - slider_location['x']

    # 模拟滑动拼图操作
    actions = ActionChains(driver)
    actions.click_and_hold(slider_element).perform()
    actions.move_by_offset(slide_distance, 0).perform()
    actions.release().perform()

    # 等待一段时间以观察结果
    time.sleep(5)

# 处理验证码后，继续爬取大众点评商品信息的代码
response = driver.page_source
soup = BeautifulSoup(response, 'html.parser')
product_items = soup.find_all('div', class_='content')

for product_item in product_items:
# 提取商品名称、价格、评分等信息
# ...
# 帮我提取商品名称
    product_name = product_item.find('h4').text
    print(product_name)
# 帮我提前商品价格
    product_price = product_item.find('span', class_='price').text
    print(product_price)

# 关闭浏览器
driver.quit()
