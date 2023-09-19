import time
from selenium import webdriver
from PIL import Image
from io import BytesIO
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 创建 Chrome 选项对象
chrome_options = webdriver.ChromeOptions()

# 设置用户代理字符串
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
chrome_options.add_argument(f"user-agent={user_agent}")

# 启动 Chrome WebDriver 并传入选项
driver = webdriver.Chrome(options=chrome_options)
# 启动内置的Chrome浏览器并最大化窗口
driver.maximize_window()
zoom = 1.5 # 设置缩放比例

# 打开大众点评网站
driver.get("https://www.dianping.com")

# 定位并点击登录按钮
login_button = driver.find_element(By.LINK_TEXT, "你好，请登录/注册")
login_button.click()

# 尝试切换到二维码登录方式，如果找不到对应元素，则不切换
try:
    qrcode_login_button = driver.find_element(By.CLASS_NAME, "qrcode-tab")
    qrcode_login_button.click()
except:
    pass

# 等待二维码出现
time.sleep(3)  # 这里可以根据页面加载速度适当调整等待时间

# 获取二维码图片
qrcode_element = driver.find_element(By.CLASS_NAME, "qrcode-img")
qrcode_url = qrcode_element.get_attribute("src")

# 获取二维码图片位置
location = qrcode_element.location
size = qrcode_element.size

# 计算二维码区域的坐标
left = location['x'] * zoom
top = location['y'] * zoom
right = left + size['width'] * zoom
bottom = top + size['height'] * zoom

# 下载并显示二维码图片
screenshot_binary = driver.get_screenshot_as_png()
screenshot_image = Image.open(BytesIO(screenshot_binary))
qr_code_image = screenshot_image.crop((left, top, right, bottom))
qr_code_image.show()


# 用户扫描二维码并登录，手动完成后继续执行以下代码

# 等待用户登录完成，可以设置一个超时时间
# 登录状态检查
try:
    user_element = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//span[@class='userinfo-container']"))
    )
    # 用户已登录，可以继续获取商品信息
    # 找到城市选择元素
    city_select = driver.find_element(By.CLASS_NAME, "J-city")

    # 点击城市选择元素以展开城市列表
    city_select.click()

    # 找到武汉地区的链接并点击
    wuhan_link = driver.find_element(By.XPATH, "//a[@href='//www.dianping.com/wuhan']")
    wuhan_link.click()

    # 关闭城市列表
    city_select.click()

    # 找到搜索框并输入关键词
    search_input = driver.find_element(By.ID, "J-search-input")
    search_input.send_keys("所在地")

    # 执行搜索操作
    search_button = driver.find_element(By.ID, "J-all-btn")
    search_button.click()

    # 找到美食链接并点击
    food_link = driver.find_element(By.XPATH, "//a[contains(text(), '美食')]")
    food_link.click()

    # 找到商品列表的父元素
    shop_list = driver.find_element(By.ID, "shop-all-list")

    # 获取包含商品信息的所有<li>元素
    items = shop_list.find_elements(By.XPATH, "//li[@class='']")

    # 遍历每个<li>元素，提取商品信息并打印
    for item in items:
        # 获取商品名称
        shop_name = item.find_element(By.XPATH, ".//a[@data-click-name='shop_title_click']").text

        # 获取团购信息
        group_deal = item.find_element(By.XPATH,
                                       ".//div[@class='svr-info']//a[@data-click-name='shop_info_groupdeal_click']").text

        # 打印商品名称和团购信息
        print("商品名称:", shop_name)
        print("团购信息:", group_deal)
        print("\n")

except:
    # 用户未登录或超时
    print("用户未登录或超时")

# 最后不要忘记关闭浏览器
driver.quit()
