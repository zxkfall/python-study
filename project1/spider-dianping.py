import json
import logging
import os
import random
from io import BytesIO

from PIL import Image
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

# 获取当前文件所在的目录
current_directory = os.path.dirname(os.path.abspath(__file__))
# 构建保存cookies文件的相对路径
cookie_file_path = os.path.join(current_directory, "cookies.json")
# 构建保存文件的相对路径
shop_info_file_path = os.path.join(current_directory, "shop_info.txt")
# 构建保存随机选取的店铺名称的相对路径
random_shop_name_file_path = os.path.join(current_directory, "random_shop_name.txt")
# 店铺信息列表，包括店铺名称、推荐菜、地点和团购信息
shop_info_list = []
max_page_count = 5


def switch_city_page(_driver):
    city_select = _driver.find_element(By.CLASS_NAME, "J-city")
    city_select.click()
    # 使用 ActionChains 将鼠标悬浮在城市选择元素上
    action = ActionChains(_driver)
    action.move_to_element(city_select).perform()
    # 找到武汉地区的链接并点击
    wuhan_link = _driver.find_element(By.XPATH, "//a[@href='//www.dianping.com/wuhan']")
    wuhan_link.click()


def init_logger():
    # 获取当前 Python 脚本的文件名（包括扩展名 .py）
    script_file = __file__
    # 获取文件名和扩展名的元组
    file_name, file_extension = os.path.splitext(script_file)
    # 配置日志
    log_file_path = os.path.join(current_directory, f"{file_name}.log")
    # 创建一个自定义的文件处理器，并指定编码为UTF-8
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    file_handler.setFormatter(formatter)
    # 创建日志记录器并将处理器添加到记录器中
    logger_ = logging.getLogger(__name__)
    logger_.addHandler(file_handler)
    logger_.setLevel(logging.INFO)
    return logger_


# 初始化日志记录器
def init_driver():
    # 创建 Chrome 选项对象
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")  # 无界面模式
    # 禁止输出 INFO 级别的日志
    chrome_options.add_argument('--log-level=3')
    # 设置用户代理字符串
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    chrome_options.add_argument(f"user-agent={user_agent}")
    # 启动 Chrome WebDriver 并传入选项
    _driver = webdriver.Chrome(options=chrome_options)
    # 启动内置的 Chrome 浏览器并最大化窗口
    _driver.maximize_window()
    # 设置隐式等待时间
    _driver.implicitly_wait(10)
    return _driver


# 设置缩放比例
zoom = 1.5

logger = init_logger()
logger.info("开始运行爬虫程序")

driver = init_driver()
# 打开大众点评网站
driver.get("https://www.dianping.com")
# 检查是否存在保存的 Cookie 信息


try:
    with open(cookie_file_path, "rb") as cookie_file:
        cookies = json.load(cookie_file)
    # 添加 Cookie 信息到 WebDriver
    for cookie in cookies:
        driver.add_cookie(cookie)
    # 刷新页面以应用 Cookie
    driver.refresh()
    user_element = WebDriverWait(driver, 15).until(
        ec.presence_of_element_located((By.XPATH, "//span[@class='userinfo-container']"))
    )

except Exception as e:
    if isinstance(e, FileNotFoundError):
        logger.info("未找到保存的 Cookie 信息文件")
    else:
        logger.error("读取 Cookie 信息文件失败", exc_info=True)
    # 如果找不到 Cookie 信息文件，使用二维码登录的代码部分可以放在这里

    # 定位并点击登录按钮
    login_button = driver.find_element(By.LINK_TEXT, "你好，请登录/注册")
    login_button.click()

    # 尝试切换到二维码登录方式，如果找不到对应元素，则不切换
    try:
        qrcode_login_button = WebDriverWait(driver, 5).until(
            ec.visibility_of_element_located((By.CLASS_NAME, "qrcode-tab")))
        qrcode_login_button.click()
    except Exception as e:
        logger.info("切换到二维码登录方式失败\n%s", str(e.args[0]))
        pass
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
    with open(cookie_file_path, "w") as cookie_file:
        json.dump(cookies, cookie_file, indent=4)


# 用户登录后的操作，可以在这里添加
# 登录状态检查
try:
    user_element = WebDriverWait(driver, 15).until(
        ec.presence_of_element_located((By.XPATH, "//span[@class='userinfo-container']"))
    )
    # 用户已登录，可以继续获取商品信息
    # 找到城市选择元素
    try:
        switch_city_page(_driver=driver)
    except Exception as e:
        logger.info("有遮罩层 \n%s", str(e.args[0]))
        # 使用部分匹配的 CSS 选择器来选择包含 "guangzhou" ,也就是当前定位城市的链接
        local_city_link = driver.find_element(By.CSS_SELECTOR, 'div#browser-city a[href^="//www.dianping.com/"]')

        # 点击 "guangzhou" 链接
        local_city_link.click()

        # 等待遮罩层消失（这里使用遮罩层元素的消失作为判断条件）
        # 创建显示等待对象，等待城市选择元素出现并可点击（等待时间为最多 10 秒）
        WebDriverWait(driver, 10).until(ec.invisibility_of_element_located((By.ID, "browser-city")))
        switch_city_page(_driver=driver)
        pass
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
            # 检查是否存在"暂停营业"的标签
            driver.implicitly_wait(0)
            try:
                paused_label = item.find_element(By.XPATH, ".//span[contains(text(), '暂停营业')]")

                # 如果元素找到了，可以在这里执行后续操作
                print("找到了暂停营业标签:", paused_label.text)
                continue
            except NoSuchElementException:
                # 在找不到元素时捕获TimeoutException异常，然后继续执行后续操作
                print("未找到暂停营业标签，继续往下运行")
            driver.implicitly_wait(10)

            # 商铺未暂停营业，继续提取信息
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
            print("团购信息:")
            print(group_deals_text.strip())
            print("\n")

            # 将店铺信息添加到列表中
            shop_info_list.append({
                "店铺名称": shop_name,
                "推荐菜": recommend_dishes_str,
                "地点": locations_str,
                "团购信息": group_deals_text.strip()
            })

        # 判断是否有下一页，如果没有则退出循环
        try:
            next_page = driver.find_element(By.CLASS_NAME, "next")
            if "disabled" in next_page.get_attribute("class"):
                break
        except Exception as e:
            logger.error("未找到下一页链接\n%s", str(e))
            break

        if len(shop_info_list) > max_page_count:
            break
        # 点击下一页链接
        next_page.click()

        # 等待页面加载完成
        WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.ID, "shop-all-list"))
        )
except Exception as e:
    # 用户未登录或超时
    logger.error("用户未登录或超时\n%s", str(e.args[0]))
finally:
    # 打开文件以保存店铺信息
    with open(shop_info_file_path, "w", encoding="utf-8") as file:
        for shop_info in shop_info_list:
            # 写入店铺信息到文件中
            file.write(f"店铺名称: {shop_info['店铺名称']}\n")
            file.write(f"推荐菜: {shop_info['推荐菜']}\n")
            file.write(f"地点: {shop_info['地点']}\n")
            file.write("团购信息:\n")
            file.write(f"{shop_info['团购信息']}\n")
            file.write("\n")  # 添加空行分隔不同店铺信息

# 设置随机数生成器的种子，可以使用任何整数作为种子
random.seed()  # 使用系统时间作为种子，以获得更随机的结果
# 随机选取一条店铺信息
random_shop_info = random.choice(shop_info_list)
print("随机选取的店铺信息:")
print(random_shop_info)

# 提取随机选择的店铺名称并写入文件
with open(random_shop_name_file_path, "w", encoding="utf-8") as name_file:
    name_file.write(f"店铺名称: {random_shop_info['店铺名称']}\n")
    name_file.write(f"推荐菜: {random_shop_info['推荐菜']}\n")
    name_file.write(f"地点: {random_shop_info['地点']}\n")
    name_file.write("团购信息:\n")
    name_file.write(f"{random_shop_info['团购信息']}\n")

# 最后不要忘记关闭浏览器
driver.quit()
