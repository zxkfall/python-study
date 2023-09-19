import pickle
import time
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# 创建 Chrome 选项对象
chrome_options = webdriver.ChromeOptions()

# 设置用户代理字符串
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
chrome_options.add_argument(f"user-agent={user_agent}")

# 启动 Chrome WebDriver 并传入选项
driver = webdriver.Chrome(options=chrome_options)
# 启动内置的 Chrome 浏览器并最大化窗口
driver.maximize_window()
zoom = 1.5  # 设置缩放比例
# 打开大众点评网站
driver.get("https://www.dianping.com")
# 检查是否存在保存的 Cookie 信息
try:
    with open("cookies.pkl", "rb") as cookie_file:
        cookies = pickle.load(cookie_file)

    # 添加 Cookie 信息到 WebDriver
    for cookie in cookies:
        driver.add_cookie(cookie)

    # 刷新页面以应用 Cookie
    driver.refresh()

except FileNotFoundError:
    print("未找到保存的 Cookie 信息文件")

    # 如果找不到 Cookie 信息文件，使用二维码登录的代码部分可以放在这里

    # 定位并点击登录按钮
    login_button = driver.find_element(By.LINK_TEXT, "你好，请登录/注册")
    login_button.click()

    # 尝试切换到二维码登录方式，如果找不到对应元素，则不切换
    try:
        qrcode_login_button = driver.find_element(By.CLASS_NAME, "qrcode-tab")
        qrcode_login_button.click()
    except:
        pass
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

    # 此处添加登录的逻辑，等待用户登录完成

    # 登录成功后，获取并保存 Cookie 信息到文件
    cookies = driver.get_cookies()
    with open("cookies.pkl", "wb") as cookie_file:
        pickle.dump(cookies, cookie_file)
    # # 打开大众点评网站
    # time.sleep(10)
    # driver.get("https://www.dianping.com")

# 用户登录后的操作，可以在这里添加
# 登录状态检查
try:
    user_element = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//span[@class='userinfo-container']"))
    )
    # 用户已登录，可以继续获取商品信息
    # 找到城市选择元素
    city_select = driver.find_element(By.CLASS_NAME, "J-city")
    city_select.click()
    # 使用 ActionChains 将鼠标悬浮在城市选择元素上
    action = ActionChains(driver)
    action.move_to_element(city_select).perform()

    # 找到武汉地区的链接并点击
    wuhan_link = driver.find_element(By.XPATH, "//a[@href='//www.dianping.com/wuhan']")
    wuhan_link.click()

    # 找到搜索框并输入关键词
    search_input = driver.find_element(By.ID, "J-search-input")
    search_input.send_keys("所在地")

    # 执行搜索操作
    search_button = driver.find_element(By.ID, "J-all-btn")
    search_button.click()
    # 切换到新打开的标签页
    driver.switch_to.window(driver.window_handles[-1])

    # 找到美食链接元素
    food_link = driver.find_element(By.XPATH, "//a//span[contains(text(), '美食')]").find_element(By.XPATH, "..")

    # 获取美食链接的URL
    food_link_url = food_link.get_attribute("href")

    # 使用JavaScript打开链接在当前标签页中
    driver.execute_script("window.location.href = arguments[0];", food_link_url)

    # 切换到新打开的标签页
    driver.switch_to.window(driver.window_handles[-1])

    while True:

        # 找到商品列表的父元素
        shop_list = driver.find_element(By.ID, "shop-all-list")

        # 获取包含商品信息的所有<li>元素
        items = shop_list.find_elements(By.XPATH, "//li[@class='']")

        # 遍历每个<li>元素，提取商品信息并打印
        for item in items:
            # 获取商品名称
            shop_name = item.find_element(By.XPATH, ".//a[@data-click-name='shop_title_click']").text

            # 获取团购信息的所有子元素
            group_deals_elements = item.find_elements(By.XPATH,
                                                      ".//div[@class='svr-info']//a[@data-click-name='shop_info_groupdeal_click']")

            # 使用列表推导式获取每个团购信息的文本
            group_deals = [deal.get_attribute("textContent").strip() for deal in group_deals_elements]

            # 使用换行符 '\n' 连接团购信息列表的文本
            group_deals_text = '\n'.join(group_deals)

            # 获取推荐菜信息
            recommend_dishes_elements = item.find_elements(By.XPATH,
                                                           ".//div[@class='recommend']//a[@class='recommend-click']")
            recommend_dishes = [dish.text for dish in recommend_dishes_elements]
            recommend_dishes_str = ", ".join(recommend_dishes)

            # 获取地点信息
            tag_elements = item.find_elements(By.XPATH, ".//div[@class='tag-addr']//span[@class='tag']")
            locations = [tag.text for tag in tag_elements]
            locations_str = ", ".join(locations)

            # 打印店铺名称、推荐菜和地点信息
            print("店铺名称:", shop_name)
            print("推荐菜:", recommend_dishes_str)
            print("地点:", locations_str)
            # 打印商品名称和拼接的团购信息
            print("团购信息:\n", group_deals_text)
            print("\n")
        # 判断是否有下一页，如果没有则退出循环
        try:
            next_page = driver.find_element(By.CLASS_NAME, "next")
            if "disabled" in next_page.get_attribute("class"):
                break
        except:
            break

        # 点击下一页链接
        next_page.click()

        # 等待页面加载完成
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "shop-all-list"))
        )
except:
    # 用户未登录或超时
    print("用户未登录或超时")
# 最后不要忘记关闭浏览器
driver.quit()
