import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from PIL import Image
from io import BytesIO

# 启动内置的Chrome浏览器并最大化窗口
driver = webdriver.Chrome()
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
time.sleep(2)  # 这里可以根据页面加载速度适当调整等待时间

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
# 你可以添加代码来轮询检查用户是否已登录，或者根据网站上的元素状态来确定登录状态

# 登录完成后，继续执行获取商品信息的操作
# 你可以根据页面结构定位商品信息的元素并进行抓取

# 最后不要忘记关闭浏览器
driver.quit()
