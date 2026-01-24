"""
浏览器自动化控制模块

基于 Selenium 实现浏览器控制功能
"""

import time
import logging
from pathlib import Path
from typing import Optional, List, Tuple, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions

logger = logging.getLogger(__name__)


class BrowserController:
    """浏览器控制器"""

    def __init__(self,
                 browser_type: str = 'chrome',
                 headless: bool = False,
                 user_agent: Optional[str] = None,
                 window_size: Tuple[int, int] = (1920, 1080)):
        """
        初始化浏览器控制器

        Args:
            browser_type: 浏览器类型 'chrome' | 'firefox' | 'edge'
            headless: 是否无头模式（不显示浏览器窗口）
            user_agent: 自定义 User-Agent
            window_size: 窗口大小 (width, height)
        """
        self.browser_type = browser_type.lower()
        self.headless = headless
        self.user_agent = user_agent
        self.window_size = window_size
        self.driver = None

        logger.info(f"初始化浏览器控制器: {browser_type}")
        self._init_driver()

    def _init_driver(self):
        """初始化 WebDriver"""
        try:
            if self.browser_type == 'chrome':
                self._init_chrome()
            elif self.browser_type == 'firefox':
                self._init_firefox()
            elif self.browser_type == 'edge':
                self._init_edge()
            else:
                raise ValueError(f"不支持的浏览器类型: {self.browser_type}")

            # 设置窗口大小
            if not self.headless:
                self.driver.set_window_size(*self.window_size)

            logger.info(f"浏览器初始化成功: {self.browser_type}")

        except Exception as e:
            logger.error(f"浏览器初始化失败: {e}")
            raise

    def _init_chrome(self):
        """初始化 Chrome 浏览器"""
        options = ChromeOptions()

        if self.headless:
            options.add_argument('--headless')

        # 常用配置
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument(f'--window-size={self.window_size[0]},{self.window_size[1]}')

        if self.user_agent:
            options.add_argument(f'user-agent={self.user_agent}')

        # 禁用自动化标识
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        self.driver = webdriver.Chrome(options=options)

    def _init_firefox(self):
        """初始化 Firefox 浏览器"""
        options = FirefoxOptions()

        if self.headless:
            options.add_argument('--headless')

        if self.user_agent:
            options.set_preference("general.useragent.override", self.user_agent)

        self.driver = webdriver.Firefox(options=options)

    def _init_edge(self):
        """初始化 Edge 浏览器"""
        options = ChromeOptions()

        if self.headless:
            options.add_argument('--headless')

        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'--window-size={self.window_size[0]},{self.window_size[1]}')

        if self.user_agent:
            options.add_argument(f'user-agent={self.user_agent}')

        self.driver = webdriver.Edge(options=options)

    def open(self, url: str) -> bool:
        """
        打开网址

        Args:
            url: 目标网址

        Returns:
            bool: 是否成功
        """
        try:
            self.driver.get(url)
            logger.info(f"已打开: {url}")
            return True
        except Exception as e:
            logger.error(f"打开网址失败: {e}")
            return False

    def find_element(self,
                     locator: Tuple[str, str],
                     timeout: int = 10) -> Optional[Any]:
        """
        查找单个元素

        Args:
            locator: 定位器 (By.ID, 'element_id') 或 (By.XPATH, '//xpath')
            timeout: 超时时间（秒）

        Returns:
            WebElement 或 None
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return element
        except TimeoutException:
            logger.warning(f"元素查找超时: {locator}")
            return None
        except Exception as e:
            logger.error(f"查找元素失败: {e}")
            return None

    def find_elements(self,
                      locator: Tuple[str, str],
                      timeout: int = 10) -> List[Any]:
        """
        查找多个元素

        Args:
            locator: 定位器
            timeout: 超时时间（秒）

        Returns:
            元素列表
        """
        try:
            elements = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located(locator)
            )
            return elements
        except TimeoutException:
            logger.warning(f"未找到元素: {locator}")
            return []
        except Exception as e:
            logger.error(f"查找元素失败: {e}")
            return []

    def click(self,
              locator: Tuple[str, str],
              timeout: int = 10) -> bool:
        """
        点击元素

        Args:
            locator: 元素定位器
            timeout: 超时时间

        Returns:
            bool: 是否成功
        """
        try:
            element = self.find_element(locator, timeout)
            if element:
                element.click()
                logger.debug(f"已点击元素: {locator}")
                return True
            return False
        except Exception as e:
            logger.error(f"点击失败: {e}")
            return False

    def input_text(self,
                   locator: Tuple[str, str],
                   text: str,
                   clear_first: bool = True,
                   timeout: int = 10) -> bool:
        """
        输入文本

        Args:
            locator: 元素定位器
            text: 输入的文本
            clear_first: 是否先清空
            timeout: 超时时间

        Returns:
            bool: 是否成功
        """
        try:
            element = self.find_element(locator, timeout)
            if element:
                if clear_first:
                    element.clear()
                element.send_keys(text)
                logger.debug(f"已输入文本到: {locator}")
                return True
            return False
        except Exception as e:
            logger.error(f"输入文本失败: {e}")
            return False

    def get_text(self,
                 locator: Tuple[str, str],
                 timeout: int = 10) -> Optional[str]:
        """
        获取元素文本

        Args:
            locator: 元素定位器
            timeout: 超时时间

        Returns:
            文本内容或 None
        """
        try:
            element = self.find_element(locator, timeout)
            if element:
                return element.text
            return None
        except Exception as e:
            logger.error(f"获取文本失败: {e}")
            return None

    def get_attribute(self,
                      locator: Tuple[str, str],
                      attribute: str,
                      timeout: int = 10) -> Optional[str]:
        """
        获取元素属性

        Args:
            locator: 元素定位器
            attribute: 属性名
            timeout: 超时时间

        Returns:
            属性值或 None
        """
        try:
            element = self.find_element(locator, timeout)
            if element:
                return element.get_attribute(attribute)
            return None
        except Exception as e:
            logger.error(f"获取属性失败: {e}")
            return None

    def wait_for_element(self,
                         locator: Tuple[str, str],
                         timeout: int = 10) -> bool:
        """
        等待元素出现

        Args:
            locator: 元素定位器
            timeout: 超时时间

        Returns:
            bool: 是否找到
        """
        element = self.find_element(locator, timeout)
        return element is not None

    def execute_script(self, script: str, *args) -> Any:
        """
        执行 JavaScript

        Args:
            script: JavaScript 代码
            *args: 传递给 JavaScript 的参数

        Returns:
            执行结果
        """
        try:
            result = self.driver.execute_script(script, *args)
            logger.debug(f"已执行 JavaScript")
            return result
        except Exception as e:
            logger.error(f"执行 JavaScript 失败: {e}")
            return None

    def scroll_to_element(self, locator: Tuple[str, str], timeout: int = 10) -> bool:
        """
        滚动到元素位置

        Args:
            locator: 元素定位器
            timeout: 超时时间

        Returns:
            bool: 是否成功
        """
        try:
            element = self.find_element(locator, timeout)
            if element:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(0.5)  # 等待滚动完成
                logger.debug(f"已滚动到元素: {locator}")
                return True
            return False
        except Exception as e:
            logger.error(f"滚动到元素失败: {e}")
            return False

    def scroll_page(self, amount: int = 500):
        """
        滚动页面

        Args:
            amount: 滚动像素量（正数向下，负数向上）
        """
        self.driver.execute_script(f"window.scrollBy(0, {amount});")
        logger.debug(f"页面滚动: {amount}px")

    def screenshot(self, filename: Optional[str] = None,
                  folder: str = "images/screenshots") -> Optional[str]:
        """
        截取当前页面可见区域

        Args:
            filename: 文件名，None自动生成
            folder: 保存文件夹

        Returns:
            保存的文件路径或 None
        """
        try:
            # 创建文件夹
            save_folder = Path(folder)
            save_folder.mkdir(parents=True, exist_ok=True)

            # 生成文件名
            if filename is None:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"

            filepath = save_folder / filename

            # 截图
            self.driver.save_screenshot(str(filepath))

            logger.info(f"截图已保存: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"截图失败: {e}")
            return None

    def screenshot_full_page(self, filename: Optional[str] = None,
                            folder: str = "images/screenshots") -> Optional[str]:
        """
        截取整个网页（包括需要滚动的部分）

        Args:
            filename: 文件名
            folder: 保存文件夹

        Returns:
            保存的文件路径或 None
        """
        try:
            # 创建文件夹
            save_folder = Path(folder)
            save_folder.mkdir(parents=True, exist_ok=True)

            # 生成文件名
            if filename is None:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"full_page_{timestamp}.png"

            filepath = save_folder / filename

            # 获取页面总高度
            total_height = self.driver.execute_script(
                "return document.body.scrollHeight"
            )

            # 获取窗口高度
            window_height = self.driver.execute_script(
                "return window.innerHeight"
            )

            # 使用 PIL 拼接完整截图
            from PIL import Image
            import io

            screenshots = []
            current_position = 0

            while current_position < total_height:
                # 截取当前可见区域
                screenshot_binary = self.driver.get_screenshot_as_png()
                screenshot = Image.open(io.BytesIO(screenshot_binary))
                screenshots.append(screenshot)

                # 滚动到下一部分
                current_position += window_height - 50  # 重叠50px避免缺失
                self.driver.execute_script(f"window.scrollTo(0, {current_position});")
                time.sleep(0.3)  # 等待滚动完成

            # 拼接图片
            if screenshots:
                total_width = screenshots[0].width
                total_image_height = sum(img.height for img in screenshots)

                final_image = Image.new('RGB', (total_width, total_image_height))

                y_offset = 0
                for screenshot in screenshots:
                    final_image.paste(screenshot, (0, y_offset))
                    y_offset += screenshot.height

                final_image.save(str(filepath))
                logger.info(f"全页截图已保存: {filepath}")
                return str(filepath)

            return None

        except Exception as e:
            logger.error(f"全页截图失败: {e}")
            return None

    def get_url(self) -> str:
        """获取当前 URL"""
        return self.driver.current_url

    def get_title(self) -> str:
        """获取页面标题"""
        return self.driver.title

    def back(self):
        """后退"""
        self.driver.back()
        logger.debug("页面后退")

    def forward(self):
        """前进"""
        self.driver.forward()
        logger.debug("页面前进")

    def refresh(self):
        """刷新页面"""
        self.driver.refresh()
        logger.debug("页面刷新")

    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("浏览器已关闭")

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.close()

    def __del__(self):
        """析构函数，确保关闭浏览器"""
        # 注释掉自动关闭，让浏览器保持打开
        # self.close()
        pass


# 便捷的定位器常量
class Locator:
    """元素定位器常量"""
    ID = By.ID
    NAME = By.NAME
    CLASS_NAME = By.CLASS_NAME
    TAG_NAME = By.TAG_NAME
    LINK_TEXT = By.LINK_TEXT
    PARTIAL_LINK_TEXT = By.PARTIAL_LINK_TEXT
    CSS_SELECTOR = By.CSS_SELECTOR
    XPATH = By.XPATH


# 测试函数
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("浏览器控制器测试")
    print("=" * 60)

    # 使用上下文管理器自动关闭浏览器
    with BrowserController(browser_type='chrome', headless=False) as browser:
        # 打开网页
        print("\n1. 打开百度...")
        browser.open('https://www.baidu.com')

        # 查找搜索框
        print("2. 查找搜索框...")
        search_box = browser.find_element((Locator.ID, 'kw'))
        if search_box:
            print("   [OK] 找到搜索框")

            # 输入文本
            print("3. 输入搜索内容...")
            browser.input_text((Locator.ID, 'kw'), 'Python Selenium')

            # 点击搜索按钮
            print("4. 点击搜索...")
            browser.click((Locator.ID, 'su'))

            # 等待结果加载
            time.sleep(2)

            # 截图
            print("5. 截图...")
            browser.screenshot('baidu_search_result.png')

            print("\n[OK] 测试完成")
        else:
            print("   [X] 未找到搜索框")
