import json
import logging
import os
import random
from io import BytesIO

from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

# 全局替换所有commit历史记录里面当前分支的所有文件中的字符串
# git filter-branch --tree-filter "find . -name '*.py' -exec sed -i -e 's/originalWord/currentWord/g' {} \;"

# 设置获取的页数
max_page_index = 5
# 设置缩放比例, 无头模式下默认为1，图形化模式下需要根据屏幕缩放比例设置
zoom = 1
# 设置所在城市 拼音或英文
target_city_name = "wuhan"
# 设置搜索的地址名称
target_address_name = "所在地"

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


def switch_to_city_page(_driver, _logger):
    local_city_links = _driver.find_elements(By.CSS_SELECTOR, 'div#browser-city a[href^="//www.dianping.com/"]')
    if len(local_city_links) > 0:
        _logger.info("有遮罩层，需要切换城市")
        # 点击 "guangzhou" 链接
        local_city_links[0].click()
        # 等待遮罩层消失（这里使用遮罩层元素的消失作为判断条件）
        # 创建显示等待对象，等待城市选择元素出现并可点击（等待时间为最多 10 秒）
        WebDriverWait(_driver, 10).until(ec.invisibility_of_element_located((By.ID, "browser-city")))
    city_select = _driver.find_element(By.CLASS_NAME, "J-city")
    city_select.click()
    # 使用 ActionChains 将鼠标悬浮在城市选择元素上
    action = ActionChains(_driver)
    action.move_to_element(city_select).perform()
    # 找到武汉地区的链接并点击
    target_city_link = _driver.find_element(By.XPATH, "//a[@href='//www.dianping.com/%s']" % target_city_name)
    target_city_link.click()


def initialize_logger():
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


def is_user_logged_in(_driver, _logger):
    _logger.info("正在检查用户是否已登录")
    _driver.implicitly_wait(15)
    user_elements = _driver.find_elements(By.XPATH, "//span[@class='userinfo-container']")
    _driver.implicitly_wait(10)
    return len(user_elements) > 0


# 初始化日志记录器
def initialize_driver():
    # 创建 Chrome 选项对象
    chrome_options = webdriver.ChromeOptions()
    # 无界面模式
    chrome_options.add_argument("--headless")
    # 禁止输出 INFO 级别的日志
    chrome_options.add_argument('--log-level=3')
    # 设置用户代理字符串
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    chrome_options.add_argument(f"user-agent={user_agent}")
    # 启动 Chrome WebDriver 并传入选项
    _driver = webdriver.Chrome(options=chrome_options)
    # 启动内置的 Chrome 浏览器并最大化窗口,-headless模式下无法最大化窗口,需要设置窗口大小
    _driver.set_window_size(1920, 1080)
    # 设置隐式等待时间
    _driver.implicitly_wait(10)
    return _driver


def qr_code_login(_driver, _logger):
    # 定位并点击登录按钮
    login_button = _driver.find_element(By.LINK_TEXT, "你好，请登录/注册")
    login_button.click()
    # 尝试切换到二维码登录方式，如果找不到对应元素，则不切换
    _driver.implicitly_wait(5)
    qrcode_login_buttons = _driver.find_elements(By.CLASS_NAME, "qrcode-tab")
    _driver.implicitly_wait(10)
    if len(qrcode_login_buttons) > 0:
        _logger.info("找到二维码登录按钮，切换到二维码登录方式")
        qrcode_login_buttons[0].click()
    # 获取二维码图片
    qrcode_element = _driver.find_element(By.CLASS_NAME, "qrcode-img")
    # 获取二维码图片位置
    location = qrcode_element.location
    size = qrcode_element.size
    # 计算二维码区域的坐标
    left = location['x'] * zoom
    top = location['y'] * zoom
    right = left + size['width'] * zoom
    bottom = top + size['height'] * zoom
    # 下载并显示二维码图片
    screenshot_binary = _driver.get_screenshot_as_png()
    screenshot_image = Image.open(BytesIO(screenshot_binary))
    qr_code_image = screenshot_image.crop((left, top, right, bottom))
    qr_code_image.show()
    # 此处添加登录的逻辑，等待用户登录完成
    # 等待用户登录完成，超时表明cookie已经失效
    if is_user_logged_in(_driver, _logger):
        _logger.info("登录成功")
        # 登录成功后，获取并保存 Cookie 信息到文件
        _cookies = _driver.get_cookies()
        with open(cookie_file_path, "w") as _cookie_file:
            json.dump(_cookies, _cookie_file, indent=4)
            _logger.info("保存 Cookie 信息成功")


def remove_mask_layer(_driver):
    # 使用部分匹配的 CSS 选择器来选择包含 "guangzhou" ,也就是当前定位城市的链接
    local_city_link = _driver.find_element(By.CSS_SELECTOR, 'div#browser-city a[href^="//www.dianping.com/"]')
    # 点击 "guangzhou" 链接
    local_city_link.click()
    # 等待遮罩层消失（这里使用遮罩层元素的消失作为判断条件）
    # 创建显示等待对象，等待城市选择元素出现并可点击（等待时间为最多 10 秒）
    WebDriverWait(_driver, 10).until(ec.invisibility_of_element_located((By.ID, "browser-city")))


def go_to_shop_list_page(_driver):
    # 找到搜索框并输入关键词
    search_input = _driver.find_element(By.ID, "J-search-input")
    search_input.send_keys(target_address_name)
    # 执行搜索操作
    search_button = _driver.find_element(By.ID, "J-all-btn")
    search_button.click()
    # 切换到新打开的标签页
    _driver.switch_to.window(_driver.window_handles[-1])
    # 找到美食链接元素
    food_link = _driver.find_element(By.XPATH, "//a//span[contains(text(), '美食')]").find_element(By.XPATH, "..")
    # 获取美食链接的URL
    food_link_url = food_link.get_attribute("href")
    # 使用JavaScript打开链接在当前标签页中
    _driver.execute_script("window.location.href = arguments[0];", food_link_url)
    # 切换到新打开的标签页
    _driver.switch_to.window(_driver.window_handles[-1])


def save_random_shop_info():
    # 设置随机数生成器的种子，可以使用任何整数作为种子
    random.seed()  # 使用系统时间作为种子，以获得更随机的结果
    # 随机选取一条店铺信息
    random_shop_info = random.choice(shop_info_list)
    print("随机选取的店铺信息:")
    print(random_shop_info)
    # 提取随机选择的店铺名称并写入文件
    with open(random_shop_name_file_path, "w", encoding="utf-8") as name_file:
        name_file.write(f"店铺名称: {random_shop_info['shop_name']}\n")
        name_file.write(f"推荐菜: {random_shop_info['recommend_dishes']}\n")
        name_file.write(f"地点: {random_shop_info['location']}\n")
        name_file.write("团购信息:\n")
        name_file.write(f"{random_shop_info['group_deals']}\n")


def save_all_shops_info():
    with open(shop_info_file_path, "w", encoding="utf-8") as file:
        for shop_info in shop_info_list:
            # 写入店铺信息到文件中
            file.write(f"店铺名称: {shop_info['shop_name']}\n")
            file.write(f"推荐菜: {shop_info['recommend_dishes']}\n")
            file.write(f"地点: {shop_info['location']}\n")
            file.write("团购信息:\n")
            file.write(f"{shop_info['group_deals']}\n")
            file.write("\n")  # 添加空行分隔不同店铺信息
        file.write(f"店铺总数: {len(shop_info_list)}\n")


def get_and_save_shops_info(_driver, _logger):
    for i in range(1, max_page_index):
        # 找到商品列表的父元素
        shop_list_container = _driver.find_element(By.ID, "shop-all-list")
        # 获取包含商品信息的所有<li>元素
        shops = shop_list_container.find_elements(By.XPATH, "//li[@class='']")
        # 遍历每个<li>元素，提取商品信息并打印
        for shop in shops:
            # 检查是否存在"暂停营业"的标签
            _driver.implicitly_wait(0)
            paused_labels = shop.find_elements(By.XPATH, ".//span[contains(text(), '暂停营业')]")
            if len(paused_labels) > 0:
                _logger.info(f"找到了暂停营业标签:{paused_labels[0].text}")
                continue
            # 商铺未暂停营业，继续提取信息
            # 获取商品名称
            shop_name = shop.find_element(By.XPATH, ".//a[@data-click-name='shop_title_click']").text

            # 获取团购信息的所有子元素
            group_deals_text = get_element_info(shop, "\n",
                                                ".//div[@class='svr-info']//a[@data-click-name='shop_info_groupdeal_click']")
            # 获取推荐菜信息
            recommend_dishes_str = get_element_info(shop, ", ",
                                                    ".//div[@class='recommend']//a[@class='recommend-click']")
            # 获取地点信息
            locations_str = get_element_info(shop, ", ", ".//div[@class='tag-addr']//span[@class='addr']")

            # 打印店铺名称、推荐菜和地点信息
            print(
                f"店铺名称: {shop_name}\n 推荐菜: {recommend_dishes_str}\n 地点: {locations_str}\n 团购信息:\n {group_deals_text}\n")

            # 将店铺信息添加到列表中
            shop_info_list.append({
                "shop_name": shop_name,
                "recommend_dishes": recommend_dishes_str,
                "location": locations_str,
                "group_deals": group_deals_text
            })

        # 判断是否有下一页，如果没有则退出循环
        next_pages = _driver.find_elements(By.CLASS_NAME, "next")
        if len(next_pages) > 0:
            _logger.info("正在获取第 %d 页的数据", i + 1)
            next_pages[0].click()
        else:
            _logger.info("已经到达最后一页，退出循环")
            break


def get_element_info(shop, separator, element_condition):
    # 获取每家店铺对应条件的元素
    group_deals_elements = shop.find_elements(By.XPATH, element_condition)
    # 使用列表推导式获取每个元素的文本
    group_deals = [deal.get_attribute("textContent").strip() for deal in group_deals_elements]
    # 使用换行符 separator 连接元素列表的文本
    group_deals_text = separator.join(group_deals)
    return group_deals_text


def load_cookies_and_refresh(_driver, _logger):
    _logger.info("正在加载 Cookie 信息")
    if os.path.exists(cookie_file_path):
        _logger.info("存在保存的 Cookie 信息")
        with open(cookie_file_path, "rb") as cookie_file:
            cookies = json.load(cookie_file)
        # 添加 Cookie 信息到 WebDriver
        for cookie in cookies:
            _driver.add_cookie(cookie)
        # 刷新页面以应用 Cookie
        _driver.refresh()
        return True
    else:
        _logger.info("不存在保存的 Cookie 信息")
        return False


def run_spider():
    logger = initialize_logger()
    logger.info("开始运行爬虫程序")

    driver = initialize_driver()
    url = "https://www.dianping.com/"
    logger.info(f"正在打开网页 {url}")
    driver.get(url)

    if load_cookies_and_refresh(driver, logger) and is_user_logged_in(driver, logger):
        logger.info("Cookie 信息有效，无需登录")
    else:
        logger.error("Cookie 信息已失效，请重新登录")
        qr_code_login(driver, logger)

    switch_to_city_page(driver, logger)
    go_to_shop_list_page(driver)
    get_and_save_shops_info(driver, logger)

    driver.quit()
    logger.info("爬虫程序运行结束")


if __name__ == "__main__":
    run_spider()
