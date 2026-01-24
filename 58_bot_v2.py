"""
58同城自动化脚本 V2 - 简化版

使用方法：
1. 修改下面的 operations 列表来定义操作流程
2. 在 images/58/58_templates/ 目录下放置对应的模板图片
3. 运行脚本

操作类型说明：
- open_url: 打开网址
- wait: 等待指定秒数
- click_text: 点击包含指定文本的元素
  - text: 要点击的文本
  - exact_match: 精确匹配（默认True），设为False则模糊匹配
  - wait_after: 点击后等待秒数
- click_xpath: 使用XPath点击元素
  - xpath: XPath表达式
  - index: 要点击第几个元素（从0开始，默认0）
  - wait_after: 点击后等待秒数
- click_xpath_all: 使用XPath点击所有匹配的元素
  - xpath: XPath表达式
  - wait_after_each: 每次点击后等待秒数（默认3）
  - wait_before_each: 每次点击前等待秒数（默认0）
- click_xpath_all_pages: 跨页点击所有元素（自动翻页）
  - xpath: 要点击的元素XPath
  - next_page_xpath: 下一页按钮的XPath（可选）
  - next_page_text: 下一页按钮的文本（默认"下一页"）
  - page_info_xpath: 页码信息容器XPath（用于获取总页数）
  - image_xpath: 要下载的图片XPath（可选，支持多个xpath用逗号分隔）
  - wait_after_each: 每次点击后等待秒数（默认3）
  - wait_after_page: 翻页后等待秒数（默认2）
  - max_pages: 最大处理页数（默认50，防止无限循环）
- click_image: 匹配并点击模板图片
- switch_tab: 切换到最新的标签页
- screenshot: 保存截图

示例：
    # 精确匹配"个人"（不会匹配"个人中心"）
    {'type': 'click_text', 'text': '个人', 'exact_match': True},

    # 使用XPath点击列表中的第1个li元素
    {'type': 'click_xpath', 'xpath': '/html/body/div[5]/div[6]/div[1]/ul/li', 'index': 0},

    # 使用XPath点击列表中的所有li元素，每个停留3秒
    {'type': 'click_xpath_all', 'xpath': '/html/body/div[5]/div[6]/div[1]/ul/li', 'wait_after_each': 3},

    # 跨页点击所有li元素，自动翻页直到最后一页
    {'type': 'click_xpath_all_pages',
     'xpath': '/html/body/div[5]/div[6]/div[1]/ul/li',
     'next_page_text': '下一页',
     'page_info_xpath': '/html/body/div[5]/div[6]/div[1]/div[1]',
     'image_xpath': '//*[@id="xtu_0"]/img',  # 下载指定xpath的图片
     'wait_after_each': 3},
"""

import time
import logging
from pathlib import Path
from typing import Dict, List, Any

# 导入核心模块
from src.core.browser import BrowserController
from src.core.recognizer import ImageRecognizer
from src.core.controller import MouseController
import pyautogui
import cv2
import numpy as np
from PIL import Image
from io import BytesIO

logger = logging.getLogger(__name__)


# ============================================================================
# 配置区域 - 在这里定义操作流程
# ============================================================================

# 基础配置
CONFIG = {
    'url': 'https://bj.58.com/',
    'template_dir': 'images/58/58_templates',
    'screenshot_dir': 'images/58/58_screenshots',
    'browser_type': 'chrome',
    'headless': False,
    'threshold': 0.7,  # 图像匹配阈值
    'max_retries': 5,  # 图像匹配最大重试次数
}

# 操作序列 - 按顺序执行的操作列表
OPERATIONS = [
    # 步骤1: 打开浏览器并访问58同城
    {
        'type': 'open_url',
        'url': CONFIG['url'],
        'description': '打开58同城首页'
    },

    # 步骤2: 等待页面加载
    {
        'type': 'wait',
        'seconds': 2,
        'description': '等待页面加载'
    },

    # 步骤3: 点击"青岛"链接
    {
        'type': 'click_text',
        'text': '青岛',
        'description': '点击青岛链接',
        'wait_after': 8,  # 点击后等待时间（秒）
    },

    # 步骤4: 等待新页面加载
    {
        'type': 'wait',
        'seconds': 3,
        'description': '等待新页面加载'
    },

    # 步骤5: 点击"租房"文本（会打开新标签页）
    {
        'type': 'click_text',
        'text': '租房',
        'description': '点击租房',
        'use_selenium': True,  # 使用Selenium直接查找文本
        'wait_after': 2,
    },

    # 步骤6: 切换到新标签页
    {
        'type': 'switch_tab',
        'description': '切换到新打开的标签页',
        'wait_after': 1,
    },
    # 步骤7: 等待页面稳定
    {
        'type': 'wait',
        'seconds': 5,
        'description': '等待页面稳定'
    },
    # 步骤8: 点击"租房"文本（会打开新标签页）
    {
        'type': 'click_text',
        'text': '写字楼',
        'description': '点击写字楼',
        #'use_selenium': True,  # 使用Selenium直接查找文本
        'wait_after': 5,
    },
    {
        'type': 'switch_tab',
        'description': '切换到新打开的标签页',
        'wait_after': 1,
    },
    {
        'type': 'click_text',
        'text': '黄岛',
        'description': '点击黄岛',
        # 'use_selenium': True,  # 使用Selenium直接查找文本
        'wait_after': 5,
    },
    # 步骤9: 切换到新标签页
    # {
    #     'type': 'switch_tab',
    #     'description': '切换到新打开的标签页',
    #     'wait_after': 1,
    # },
    {
        'type': 'click_text',
        'text': '来源不限',
        'description': '点击来源不限',
        # 'use_selenium': True,  # 使用Selenium直接查找文本
        'wait_after': 5,
    },
    {
        'type': 'click_text',
        'text': '个人',
        'description': '点击个人',
        # 'use_selenium': True,  # 使用Selenium直接查找文本
        'wait_after': 2,
    },
    {
        'type': 'click_text',
        'text': '纯写字楼',
        'description': '点击纯写字楼',
        # 'use_selenium': True,  # 使用Selenium直接查找文本
        'wait_after': 2,
    },
    # # 步骤8: 匹配并点击模板图片（例如：4.PNG）
    # {
    #     'type': 'click_image',
    #     'template': '3',  # 对应 images/58/58_templates/4.PNG
    #     'description': '点击目标按钮',
    #     'wait_after': 1,
    # },
    # 跨页点击所有li元素，自动翻页直到最后一页
    {
        'type': 'click_xpath_all_pages',
        'xpath': '/html/body/div[5]/div[6]/div[1]/ul/li',
        'next_page_text': '下一页',  # 下一页按钮的文本
        'page_info_xpath': '/html/body/div[5]/div[6]/div[1]/div[1]',  # 页码信息容器
        'image_xpath': '//*[@id="xtu_0"]/img',  # 下载指定xpath的图片
        'wait_after_each': 3,  # 每次点击后等待3秒
        'wait_after_page': 2,  # 翻页后等待2秒
        'max_pages': 50,  # 安全限制（最多处理50页）
        'description': '跨页点击所有li元素',
    },
    # 步骤9: 保存最终截图
    {
        'type': 'screenshot',
        'filename': 'final_screenshot',
        'description': '保存最终截图'
    },
]


# ============================================================================
# 执行引擎 - 无需修改
# ============================================================================

class OperationExecutor:
    """操作执行器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.browser = None
        self.recognizer = None
        self.current_step = 0

        # 创建必要的目录
        Path(config['screenshot_dir']).mkdir(parents=True, exist_ok=True)
        Path(config['template_dir']).mkdir(parents=True, exist_ok=True)

    def execute(self, operations: List[Dict[str, Any]]) -> bool:
        """执行操作序列"""
        print("=" * 70)
        print("   58同城自动化脚本 V2")
        print("=" * 70)
        print(f"\n配置信息:")
        for key, value in self.config.items():
            print(f"   {key}: {value}")

        print(f"\n操作序列 (共 {len(operations)} 步):")
        for i, op in enumerate(operations, 1):
            desc = op.get('description', '无描述')
            print(f"   {i}. {desc}")

        print("\n" + "=" * 70)
        print("开始执行...")
        print("=" * 70 + "\n")

        try:
            for i, operation in enumerate(operations, 1):
                self.current_step = i
                op_type = operation['type']
                description = operation.get('description', '')

                print(f"\n[步骤 {i}/{len(operations)}] {description}")
                print(f"类型: {op_type}")

                success = self._execute_operation(operation)

                if not success:
                    print(f"[X] 步骤 {i} 执行失败")
                    return False

                print(f"[OK] 步骤 {i} 完成")

            print("\n" + "=" * 70)
            print("   所有操作执行完成!")
            print("=" * 70)
            return True

        except Exception as e:
            logger.error(f"执行出错: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _execute_operation(self, operation: Dict[str, Any]) -> bool:
        """执行单个操作"""
        op_type = operation['type']

        if op_type == 'open_url':
            return self._open_url(operation)
        elif op_type == 'wait':
            return self._wait(operation)
        elif op_type == 'click_text':
            return self._click_text(operation)
        elif op_type == 'click_xpath':
            return self._click_xpath(operation)
        elif op_type == 'click_xpath_all':
            return self._click_xpath_all(operation)
        elif op_type == 'click_xpath_all_pages':
            return self._click_xpath_all_pages(operation)
        elif op_type == 'click_image':
            return self._click_image(operation)
        elif op_type == 'switch_tab':
            return self._switch_tab(operation)
        elif op_type == 'screenshot':
            return self._screenshot(operation)
        else:
            print(f"[X] 未知的操作类型: {op_type}")
            return False

    def _open_url(self, operation: Dict[str, Any]) -> bool:
        """打开网址"""
        if self.browser is None:
            self.browser = BrowserController(
                browser_type=self.config['browser_type'],
                headless=self.config['headless']
            )

        url = operation['url']
        print(f"正在访问: {url}")

        if not self.browser.open(url):
            print("[X] 打开网页失败")
            return False

        print("[OK] 网页已打开")
        return True

    def _wait(self, operation: Dict[str, Any]) -> bool:
        """等待"""
        seconds = operation.get('seconds', 1)
        print(f"等待 {seconds} 秒...")
        time.sleep(seconds)
        return True

    def _click_text(self, operation: Dict[str, Any]) -> bool:
        """点击包含指定文本的元素"""
        text = operation['text']
        print(f"查找并点击: '{text}'")

        if self.browser is None:
            print("[X] 浏览器未初始化")
            return False

        # 等待页面加载
        wait_before = operation.get('wait_before', 0)
        if wait_before > 0:
            print(f"等待 {wait_before} 秒...")
            time.sleep(wait_before)

        from selenium.webdriver.common.by import By
        from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        # 获取匹配模式：精确匹配或模糊匹配
        exact_match = operation.get('exact_match', True)  # 默认使用精确匹配

        try:
            # 根据匹配模式选择XPath
            if exact_match:
                # 精确匹配：文本完全相等
                print(f"[INFO] 使用精确匹配模式查找 '{text}'...")
                # 尝试多种XPath表达式
                xpaths = [
                    f"//*[normalize-space(text())='{text}']",  # 直接文本节点精确匹配
                    f"//*[text()='{text}']",  # 不考虑空格的精确匹配
                    f"//*[(normalize-space(.)='{text}' and not(*) )]",  # 叶子节点精确匹配
                ]
            else:
                # 模糊匹配：包含指定文本
                print(f"[INFO] 使用模糊匹配模式查找 '{text}'...")
                xpaths = [
                    f"//*[contains(text(), '{text}')]",  # 包含文本
                    f"//*[contains(normalize-space(text()), '{text}')]",  # 包含文本（忽略空格）
                ]

            # 尝试所有XPath表达式
            element = None
            for xpath in xpaths:
                try:
                    element = self.browser.driver.find_element(By.XPATH, xpath)
                    print(f"[OK] 找到元素: {element.text[:50]}")
                    break
                except NoSuchElementException:
                    continue

            if element is None:
                raise NoSuchElementException(f"未找到匹配 '{text}' 的元素")

            # 滚动到元素位置
            self.browser.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.5)

            # 尝试多种点击方式
            clicked = False

            # 方法1: 标准点击
            try:
                print("[INFO] 尝试标准点击...")
                element.click()
                clicked = True
                print(f"[OK] 已通过标准点击 '{text}'")
            except ElementNotInteractableException:
                print("[WARNING] 标准点击失败，元素不可交互")

            # 方法2: JavaScript点击（最可靠）
            if not clicked:
                try:
                    print("[INFO] 尝试JavaScript点击...")
                    self.browser.driver.execute_script("arguments[0].click();", element)
                    clicked = True
                    print(f"[OK] 已通过JavaScript点击 '{text}'")
                except Exception as e:
                    print(f"[WARNING] JavaScript点击失败: {e}")

            # 方法3: ActionChains点击
            if not clicked:
                try:
                    print("[INFO] 尝试ActionChains点击...")
                    from selenium.webdriver.common.action_chains import ActionChains
                    actions = ActionChains(self.browser.driver)
                    actions.move_to_element(element).click().perform()
                    clicked = True
                    print(f"[OK] 已通过ActionChains点击 '{text}'")
                except Exception as e:
                    print(f"[WARNING] ActionChains点击失败: {e}")

            if clicked:
                # 点击后等待
                wait_after = operation.get('wait_after', 0)
                if wait_after > 0:
                    time.sleep(wait_after)
                return True
            else:
                print("[X] 所有点击方式都失败")
                return False

        except NoSuchElementException:
            print(f"[X] 未找到包含 '{text}' 的元素")

            # 保存调试截图
            debug_path = Path(self.config['screenshot_dir']) / f"debug_step{self.current_step}_no_element.png"
            self._save_debug_screenshot(debug_path)
            return False

        except Exception as e:
            print(f"[X] 点击失败: {e}")

            # 保存调试截图
            debug_path = Path(self.config['screenshot_dir']) / f"debug_step{self.current_step}_error.png"
            self._save_debug_screenshot(debug_path)
            return False

    def _click_xpath(self, operation: Dict[str, Any]) -> bool:
        """使用XPath点击元素"""
        xpath = operation['xpath']
        index = operation.get('index', 0)  # 默认点击第一个元素
        print(f"使用XPath点击: {xpath}")
        print(f"元素索引: {index}")

        if self.browser is None:
            print("[X] 浏览器未初始化")
            return False

        # 等待页面加载
        wait_before = operation.get('wait_before', 0)
        if wait_before > 0:
            print(f"等待 {wait_before} 秒...")
            time.sleep(wait_before)

        from selenium.webdriver.common.by import By
        from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException

        try:
            # 使用XPath查找元素（支持多个元素）
            print(f"[INFO] 查找元素...")
            elements = self.browser.driver.find_elements(By.XPATH, xpath)

            if not elements:
                raise NoSuchElementException(f"未找到XPath: {xpath}")

            if len(elements) <= index:
                print(f"[X] 索引超出范围: 找到 {len(elements)} 个元素，但请求索引 {index}")
                return False

            element = elements[index]
            print(f"[OK] 找到第 {index + 1} 个元素: {element.text[:50] if element.text else '(无文本)'}")

            # 滚动到元素位置
            self.browser.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.5)

            # 尝试多种点击方式
            clicked = False

            # 方法1: 标准点击
            try:
                print("[INFO] 尝试标准点击...")
                element.click()
                clicked = True
                print(f"[OK] 已通过标准点击")
            except ElementNotInteractableException:
                print("[WARNING] 标准点击失败，元素不可交互")

            # 方法2: JavaScript点击（最可靠）
            if not clicked:
                try:
                    print("[INFO] 尝试JavaScript点击...")
                    self.browser.driver.execute_script("arguments[0].click();", element)
                    clicked = True
                    print(f"[OK] 已通过JavaScript点击")
                except Exception as e:
                    print(f"[WARNING] JavaScript点击失败: {e}")

            # 方法3: ActionChains点击
            if not clicked:
                try:
                    print("[INFO] 尝试ActionChains点击...")
                    from selenium.webdriver.common.action_chains import ActionChains
                    actions = ActionChains(self.browser.driver)
                    actions.move_to_element(element).click().perform()
                    clicked = True
                    print(f"[OK] 已通过ActionChains点击")
                except Exception as e:
                    print(f"[WARNING] ActionChains点击失败: {e}")

            if clicked:
                # 点击后等待
                wait_after = operation.get('wait_after', 0)
                if wait_after > 0:
                    time.sleep(wait_after)
                return True
            else:
                print("[X] 所有点击方式都失败")
                return False

        except NoSuchElementException:
            print(f"[X] 未找到XPath元素: {xpath}")

            # 保存调试截图
            debug_path = Path(self.config['screenshot_dir']) / f"debug_step{self.current_step}_no_element.png"
            self._save_debug_screenshot(debug_path)
            return False

        except Exception as e:
            print(f"[X] 点击失败: {e}")

            # 保存调试截图
            debug_path = Path(self.config['screenshot_dir']) / f"debug_step{self.current_step}_error.png"
            self._save_debug_screenshot(debug_path)
            return False

    def _click_xpath_all(self, operation: Dict[str, Any]) -> bool:
        """使用XPath点击所有匹配的元素"""
        xpath = operation['xpath']
        wait_after_each = operation.get('wait_after_each', 3)  # 默认每次点击后等待3秒
        wait_before_each = operation.get('wait_before_each', 0)  # 默认点击前不等待

        print(f"使用XPath点击所有元素: {xpath}")
        print(f"每次点击后等待: {wait_after_each} 秒")

        if self.browser is None:
            print("[X] 浏览器未初始化")
            return False

        from selenium.webdriver.common.by import By
        from selenium.common.exceptions import NoSuchElementException

        try:
            # 查找所有匹配的元素
            print(f"[INFO] 查找元素...")
            elements = self.browser.driver.find_elements(By.XPATH, xpath)

            if not elements:
                raise NoSuchElementException(f"未找到XPath: {xpath}")

            print(f"[OK] 找到 {len(elements)} 个元素")

            # 遍历并点击每个元素
            success_count = 0
            for i, element in enumerate(elements):
                print(f"\n--- 点击第 {i + 1}/{len(elements)} 个元素 ---")

                element_text = element.text[:50] if element.text else '(无文本)'
                print(f"元素内容: {element_text}")

                # 点击前等待
                if wait_before_each > 0:
                    print(f"等待 {wait_before_each} 秒...")
                    time.sleep(wait_before_each)

                # 滚动到元素位置
                try:
                    self.browser.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                    time.sleep(0.5)
                except Exception as e:
                    print(f"[WARNING] 滚动失败: {e}")

                # 尝试点击
                clicked = False

                # 方法1: 标准点击
                try:
                    print(f"  [尝试1/4] 标准点击...")
                    element.click()
                    clicked = True
                    print(f"  [OK] 已通过标准点击第 {i + 1} 个元素")
                except Exception as e:
                    print(f"  [失败] 标准点击失败: {e}")

                # 方法2: JavaScript点击
                if not clicked:
                    try:
                        print(f"  [尝试2/4] JavaScript点击...")
                        self.browser.driver.execute_script("arguments[0].click();", element)
                        clicked = True
                        print(f"  [OK] 已通过JavaScript点击第 {i + 1} 个元素")
                    except Exception as e:
                        print(f"  [失败] JavaScript点击失败: {e}")

                # 方法3: 先hover再点击
                if not clicked:
                    try:
                        print(f"  [尝试3/4] 先hover再点击...")
                        from selenium.webdriver.common.action_chains import ActionChains
                        actions = ActionChains(self.browser.driver)

                        # 先移动到元素上
                        actions.move_to_element(element).perform()
                        time.sleep(0.3)

                        # 再点击
                        actions.click().perform()
                        clicked = True
                        print(f"  [OK] 已通过hover+点击第 {i + 1} 个元素")
                    except Exception as e:
                        print(f"  [失败] hover+点击失败: {e}")

                # 方法4: 使用坐标点击（pyautogui）
                if not clicked:
                    try:
                        print(f"  [尝试4/4] 使用坐标点击...")
                        # 获取元素位置
                        location = element.location
                        size = element.size

                        # 计算元素中心点坐标（相对于页面）
                        center_x = location['x'] + size['width'] // 2
                        center_y = location['y'] + size['height'] // 2

                        # 获取浏览器窗口位置
                        window_pos = self.browser.driver.get_window_position()

                        # 转换为屏幕坐标（需要加上标题栏偏移）
                        screen_x = center_x + window_pos['x']
                        screen_y = center_y + window_pos['y'] + 60

                        print(f"  元素位置: ({location['x']}, {location['y']})")
                        print(f"  屏幕坐标: ({screen_x}, {screen_y})")

                        # 使用pyautogui点击
                        pyautogui.click(screen_x, screen_y)
                        clicked = True
                        print(f"  [OK] 已通过坐标点击第 {i + 1} 个元素")
                    except Exception as e:
                        print(f"  [失败] 坐标点击失败: {e}")

                if clicked:
                    success_count += 1

                    # 点击后等待
                    print(f"  等待 {wait_after_each} 秒...")
                    time.sleep(wait_after_each)
                else:
                    print(f"  [X] 第 {i + 1} 个元素所有点击方式都失败")

                    # 保存失败时的截图
                    debug_path = Path(self.config['screenshot_dir']) / f"debug_step{self.current_step}_element{i+1}_failed.png"
                    self._save_debug_screenshot(debug_path)

            print(f"\n[完成] 成功点击 {success_count}/{len(elements)} 个元素")
            return success_count > 0

        except NoSuchElementException:
            print(f"[X] 未找到XPath元素: {xpath}")

            # 保存调试截图
            debug_path = Path(self.config['screenshot_dir']) / f"debug_step{self.current_step}_no_element.png"
            self._save_debug_screenshot(debug_path)
            return False

        except Exception as e:
            print(f"[X] 点击失败: {e}")
            import traceback
            traceback.print_exc()

            # 保存调试截图
            debug_path = Path(self.config['screenshot_dir']) / f"debug_step{self.current_step}_error.png"
            self._save_debug_screenshot(debug_path)
            return False

    def _click_xpath_all_pages(self, operation: Dict[str, Any]) -> bool:
        """跨页点击所有匹配的元素"""
        xpath = operation['xpath']
        next_page_xpath = operation.get('next_page_xpath', '')
        next_page_text = operation.get('next_page_text', '下一页')
        wait_after_each = operation.get('wait_after_each', 3)
        wait_after_page = operation.get('wait_after_page', 2)
        max_pages_config = operation.get('max_pages', 50)  # 配置的最大页数
        page_info_xpath = operation.get('page_info_xpath', '/html/body/div[5]/div[6]/div[1]/div[1]')

        print(f"跨页点击所有元素")
        print(f"元素XPath: {xpath}")
        print(f"下一页文本: {next_page_text}")
        print(f"配置最大页数: {max_pages_config}")

        if self.browser is None:
            print("[X] 浏览器未初始化")
            return False

        from selenium.webdriver.common.by import By
        from selenium.common.exceptions import NoSuchElementException

        # 获取总页数
        max_pages = max_pages_config
        try:
            print(f"\n[INFO] 尝试获取总页数...")
            # 查找页码信息容器下的所有a元素
            container = self.browser.driver.find_element(By.XPATH, page_info_xpath)
            all_links = container.find_elements(By.TAG_NAME, 'a')

            if len(all_links) >= 2:
                # 获取倒数第二个a元素
                second_last_link = all_links[-2]
                try:
                    # 查找该a元素下的span
                    page_span = second_last_link.find_element(By.TAG_NAME, 'span')
                    total_pages_text = page_span.text.strip()

                    # 尝试转换为数字
                    try:
                        total_pages = int(total_pages_text)
                        max_pages = min(total_pages, max_pages_config)
                        print(f"[OK] 检测到总页数: {total_pages}")
                        print(f"[INFO] 将处理 {max_pages} 页")
                    except ValueError:
                        print(f"[WARNING] 无法解析页数: '{total_pages_text}'")
                        print(f"[INFO] 使用配置的最大页数: {max_pages_config}")
                except NoSuchElementException:
                    print(f"[INFO] 倒数第二个a元素下没有span，使用配置的最大页数: {max_pages_config}")
            else:
                print(f"[INFO] 找到 {len(all_links)} 个链接，不足以确定页数，使用配置值: {max_pages_config}")

        except Exception as e:
            print(f"[INFO] 获取总页数失败: {e}")
            print(f"[INFO] 使用配置的最大页数: {max_pages_config}")

        total_success = 0
        total_elements = 0
        page_number = 1

        try:
            while page_number <= max_pages:
                print(f"\n{'='*70}")
                print(f"处理第 {page_number} 页")
                print(f"{'='*70}")

                # 查找当前页的所有元素
                print(f"[INFO] 查找当前页元素...")
                elements = self.browser.driver.find_elements(By.XPATH, xpath)

                if not elements:
                    print(f"[INFO] 当前页没有找到匹配的元素")
                    # 检查是否有下一页
                    if not self._click_next_page(next_page_xpath, next_page_text, wait_after_page):
                        print(f"[INFO] 已到达最后一页")
                        break
                    page_number += 1
                    continue

                print(f"[OK] 找到 {len(elements)} 个元素")

                # 点击当前页的所有元素
                page_success = 0
                for i in range(len(elements)):
                    print(f"\n--- [第{page_number}页] 点击第 {i + 1}/{len(elements)} 个元素 ---")

                    # 每次点击前重新查找元素（因为关闭标签页后元素引用会失效）
                    try:
                        current_elements = self.browser.driver.find_elements(By.XPATH, xpath)
                        if i >= len(current_elements):
                            print(f"  [WARNING] 元素索引 {i} 超出范围，跳过")
                            continue

                        element = current_elements[i]

                        # 安全地获取元素文本
                        try:
                            element_text = element.text[:50] if element.text else '(无文本)'
                        except Exception:
                            element_text = f'元素{i+1}'

                        print(f"元素内容: {element_text}")

                    except Exception as e:
                        print(f"  [WARNING] 查找元素失败: {e}")
                        continue

                    # 滚动到元素位置
                    try:
                        self.browser.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                        time.sleep(0.3)
                    except Exception as e:
                        print(f"  [WARNING] 滚动失败: {e}")

                    # 尝试在li内查找title元素（因为点击li本身不会跳转，需要点击title）
                    title_element = None
                    try:
                        # 方法1：查找li内的<a>标签（通常是包含标题的链接）
                        links = element.find_elements(By.TAG_NAME, 'a')
                        if links:
                            # 通常第一个链接就是标题链接
                            title_element = links[0]
                            print(f"  [DEBUG] 找到title链接元素")
                        else:
                            # 方法2：查找li内包含标题文字的元素
                            # 58.com的标题通常在特定class中
                            possible_titles = element.find_elements(By.XPATH, ".//*[contains(@class, 'title') or contains(@class, 't')]")
                            if possible_titles:
                                title_element = possible_titles[0]
                                print(f"  [DEBUG] 找到title元素（通过class）")
                    except Exception as e:
                        print(f"  [DEBUG] 查找title元素失败: {e}")

                    # 如果找到title元素，点击title；否则点击整个li
                    target_element = title_element if title_element else element
                    element_type = "title" if title_element else "li"

                    # 尝试点击（使用4种方法）
                    print(f"  [INFO] 点击{element_type}元素...")
                    clicked = self._try_click_element(target_element, i + 1)

                    if clicked:
                        page_success += 1
                        total_success += 1

                        # 切换到新标签页并截图
                        print(f"  [INFO] 切换到新标签页并截图...")
                        # 获取图片xpath配置
                        image_xpath = operation.get('image_xpath', '')
                        # 传递实际点击的元素（title或li），用于重试
                        screenshot_saved = self._capture_new_tab(page_number, i + 1, element_text, image_xpath, target_element)

                        if screenshot_saved:
                            print(f"  [OK] 截图已保存")
                        else:
                            print(f"  [WARNING] 截图保存失败")

                        print(f"  等待 {wait_after_each} 秒...")
                        time.sleep(wait_after_each)
                    else:
                        print(f"  [X] 点击失败")
                        debug_path = Path(self.config['screenshot_dir']) / f"debug_p{page_number}_element{i+1}_failed.png"
                        self._save_debug_screenshot(debug_path)

                total_elements += len(elements)
                print(f"\n[第{page_number}页完成] 成功点击 {page_success}/{len(elements)} 个元素")

                # 尝试点击下一页
                print(f"\n[INFO] 尝试进入下一页...")
                if not self._click_next_page(next_page_xpath, next_page_text, wait_after_page):
                    print(f"[INFO] 已到达最后一页或无法找到下一页按钮")
                    break

                page_number += 1

            print(f"\n{'='*70}")
            print(f"全部完成!")
            print(f"处理页数: {page_number}")
            print(f"总成功点击: {total_success}")
            print(f"总元素数: {total_elements}")
            print(f"{'='*70}")

            return total_success > 0

        except Exception as e:
            print(f"[X] 跨页点击失败: {e}")
            import traceback
            traceback.print_exc()

            debug_path = Path(self.config['screenshot_dir']) / f"debug_step{self.current_step}_error.png"
            self._save_debug_screenshot(debug_path)
            return False

    def _try_click_element(self, element, element_index: int, silent: bool = False) -> bool:
        """尝试使用多种方法点击元素

        Args:
            element: Selenium元素对象
            element_index: 元素索引
            silent: 是否静默模式（不打印详细日志）
        """
        clicked = False

        # 方法1: 标准点击
        if not clicked:
            try:
                if not silent:
                    print(f"  [尝试1/4] 标准点击...")
                element.click()
                clicked = True
                if not silent:
                    print(f"  [OK] 已通过标准点击")
            except Exception as e:
                if not silent:
                    print(f"  [失败] {str(e)[:50]}")

        # 方法2: JavaScript点击
        if not clicked:
            try:
                if not silent:
                    print(f"  [尝试2/4] JavaScript点击...")
                self.browser.driver.execute_script("arguments[0].click();", element)
                clicked = True
                if not silent:
                    print(f"  [OK] 已通过JavaScript点击")
            except Exception as e:
                if not silent:
                    print(f"  [失败] {str(e)[:50]}")

        # 方法3: 先hover再点击
        if not clicked:
            try:
                if not silent:
                    print(f"  [尝试3/4] hover+点击...")
                from selenium.webdriver.common.action_chains import ActionChains
                actions = ActionChains(self.browser.driver)
                actions.move_to_element(element).perform()
                time.sleep(0.2)
                actions.click().perform()
                clicked = True
                if not silent:
                    print(f"  [OK] 已通过hover+点击")
            except Exception as e:
                if not silent:
                    print(f"  [失败] {str(e)[:50]}")

        # 方法4: 坐标点击
        if not clicked:
            try:
                if not silent:
                    print(f"  [尝试4/4] 坐标点击...")
                location = element.location
                size = element.size
                center_x = location['x'] + size['width'] // 2
                center_y = location['y'] + size['height'] // 2

                window_pos = self.browser.driver.get_window_position()
                screen_x = center_x + window_pos['x']
                screen_y = center_y + window_pos['y'] + 60

                if not silent:
                    print(f"  屏幕坐标: ({screen_x}, {screen_y})")
                pyautogui.click(screen_x, screen_y)
                clicked = True
                if not silent:
                    print(f"  [OK] 已通过坐标点击")
            except Exception as e:
                if not silent:
                    print(f"  [失败] {str(e)[:50]}")

        return clicked

    def _click_next_page(self, next_page_xpath: str, next_page_text: str, wait_after: int) -> bool:
        """点击下一页按钮"""
        from selenium.webdriver.common.by import By

        # 方法1: 使用XPath
        if next_page_xpath:
            try:
                print(f"  [尝试] 使用XPath查找下一页...")
                next_button = self.browser.driver.find_element(By.XPATH, next_page_xpath)
                self.browser.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                time.sleep(0.5)
                self.browser.driver.execute_script("arguments[0].click();", next_button)
                print(f"  [OK] 已点击下一页（XPath）")
                time.sleep(wait_after)
                return True
            except Exception as e:
                print(f"  [失败] XPath查找失败: {str(e)[:50]}")

        # 方法2: 使用文本
        if next_page_text:
            try:
                print(f"  [尝试] 使用文本'{next_page_text}'查找下一页...")
                # 查找包含文本的所有元素
                xpaths = [
                    f"//*[normalize-space(text())='{next_page_text}']",
                    f"//*[contains(text(), '{next_page_text}')]",
                    f"//a[contains(text(), '{next_page_text}')]",
                ]

                for xpath in xpaths:
                    try:
                        next_buttons = self.browser.driver.find_elements(By.XPATH, xpath)
                        # 过滤掉"下一页"但不可点击的按钮（如已禁用的）
                        for btn in next_buttons:
                            try:
                                is_enabled = btn.is_enabled()
                                is_displayed = btn.is_displayed()
                                if is_enabled and is_displayed:
                                    self.browser.driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                                    time.sleep(0.5)
                                    self.browser.driver.execute_script("arguments[0].click();", btn)
                                    print(f"  [OK] 已点击下一页（文本）")
                                    time.sleep(wait_after)
                                    return True
                            except:
                                continue
                    except:
                        continue

                print(f"  [失败] 未找到可点击的'{next_page_text}'按钮")

            except Exception as e:
                print(f"  [失败] 文本查找失败: {str(e)[:50]}")

        # 方法3: 查找常见的分页按钮
        try:
            print(f"  [尝试] 查找常见分页按钮...")
            common_selectors = [
                "//a[@class='next' or contains(@class, 'next')]",
                "//li[@class='next' or contains(@class, 'next')]/a",
                "//*[@title='下一页']",
                "//button[contains(text(), '下一页')]",
            ]

            for selector in common_selectors:
                try:
                    next_buttons = self.browser.driver.find_elements(By.XPATH, selector)
                    for btn in next_buttons:
                        if btn.is_enabled() and btn.is_displayed():
                            self.browser.driver.execute_script("arguments[0].click();", btn)
                            print(f"  [OK] 已点击下一页（通用选择器）")
                            time.sleep(wait_after)
                            return True
                except:
                    continue
        except:
            pass

        print(f"  [X] 未找到下一页按钮")
        return False

    def _click_image(self, operation: Dict[str, Any]) -> bool:
        """匹配并点击模板图片"""
        template_name = operation['template']
        print(f"匹配模板: {template_name}.PNG")

        # 初始化识别器
        if self.recognizer is None:
            self.recognizer = ImageRecognizer(
                template_dir=self.config['template_dir'],
                threshold=self.config['threshold']
            )

        # 检查模板是否存在
        if template_name not in self.recognizer.templates:
            print(f"[X] 模板不存在: {template_name}.PNG")
            print(f"请将模板图片放置在: {self.config['template_dir']}/{template_name}.PNG")
            return False

        # 等待页面加载
        wait_before = operation.get('wait_before', 0)
        if wait_before > 0:
            print(f"等待 {wait_before} 秒...")
            time.sleep(wait_before)

        # 尝试匹配
        max_retries = operation.get('max_retries', self.config['max_retries'])

        for attempt in range(max_retries):
            print(f"   尝试 {attempt + 1}/{max_retries}...", end=' ')

            # 截图
            screen = self._capture_screen()
            if screen is None:
                print("失败")
                continue

            # 保存调试截图
            debug_path = Path(self.config['screenshot_dir']) / f"debug_step{self.current_step}_attempt{attempt + 1}.png"
            cv2.imwrite(str(debug_path), screen)

            # 匹配模板
            match_result = self.recognizer.find_template(
                template_name,
                screen,
                threshold=self.config['threshold']
            )

            if match_result:
                center_x, center_y = match_result['center']
                confidence = match_result['confidence']
                print(f"成功! (置信度: {confidence:.3f}, 位置: {center_x}, {center_y})")

                # 点击
                if self._click_position(center_x, center_y, screen, template_name):
                    # 保存带标注的截图
                    self._save_click_marker(screen, center_x, center_y, template_name)

                    # 点击后等待
                    wait_after = operation.get('wait_after', 0)
                    if wait_after > 0:
                        time.sleep(wait_after)

                    return True
                else:
                    print("[X] 点击失败")
                    return False
            else:
                print("未找到")

            if attempt < max_retries - 1:
                time.sleep(1)

        print(f"[X] 匹配失败")
        return False

    def _switch_tab(self, operation: Dict[str, Any]) -> bool:
        """切换到最新的标签页"""
        print("切换标签页...")

        if self.browser is None:
            print("[X] 浏览器未初始化")
            return False

        try:
            all_windows = self.browser.driver.window_handles

            if len(all_windows) <= 1:
                print("[INFO] 只有一个标签页，无需切换")
                return True

            # 切换到最新的标签页
            self.browser.driver.switch_to.window(all_windows[-1])
            print(f"[OK] 已切换到标签页 {len(all_windows)}")

            # 切换后等待
            wait_after = operation.get('wait_after', 0)
            if wait_after > 0:
                time.sleep(wait_after)

            return True

        except Exception as e:
            print(f"[X] 切换标签页失败: {e}")
            return False

    def _screenshot(self, operation: Dict[str, Any]) -> bool:
        """保存截图"""
        filename = operation.get('filename', f'step{self.current_step}')
        print(f"保存截图...")

        if self.browser is None:
            print("[X] 浏览器未初始化")
            return False

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        screenshot_filename = f"{filename}_{timestamp}.png"
        saved_path = self.browser.screenshot(
            filename=screenshot_filename,
            folder=self.config['screenshot_dir']
        )

        if saved_path:
            print(f"[OK] 截图已保存: {saved_path}")
            return True
        else:
            print("[X] 截图保存失败")
            return False

    def _capture_screen(self) -> np.ndarray:
        """截取浏览器屏幕"""
        try:
            screenshot_binary = self.browser.driver.get_screenshot_as_png()
            screen_pil = Image.open(BytesIO(screenshot_binary))
            screen = cv2.cvtColor(np.array(screen_pil), cv2.COLOR_RGB2BGR)
            return screen
        except Exception as e:
            print(f"[X] 截图失败: {e}")
            return None

    def _click_position(self, x: int, y: int, screen: np.ndarray, template_name: str) -> bool:
        """点击指定位置"""
        try:
            # 方法1: 使用JavaScript点击（更可靠）
            js_code = f"""
            var element = document.elementFromPoint({x}, {y});
            if (element) {{
                element.click();
                return true;
            }}
            return false;
            """
            result = self.browser.driver.execute_script(js_code)

            if result:
                print(f"   [INFO] 已通过JavaScript点击 ({x}, {y})")
                return True

            # 方法2: 使用pyautogui点击（需要坐标转换）
            print(f"   [INFO] JavaScript点击失败，尝试使用pyautogui...")

            window_pos = self.browser.driver.get_window_position()
            screen_x = x + window_pos['x']
            screen_y = y + window_pos['y'] + 60  # 标题栏偏移

            pyautogui.click(screen_x, screen_y)
            print(f"   [INFO] 已通过pyautogui点击 ({screen_x}, {screen_y})")
            return True

        except Exception as e:
            print(f"   [X] 点击失败: {e}")
            return False

    def _save_click_marker(self, screen: np.ndarray, x: int, y: int, template_name: str):
        """保存带点击标记的截图"""
        try:
            marker_path = Path(self.config['screenshot_dir']) / f"click_{template_name}_marked.png"
            screen_marked = screen.copy()

            # 画红色圆圈和十字
            cv2.circle(screen_marked, (x, y), 15, (0, 0, 255), 3)
            cv2.line(screen_marked, (x - 20, y), (x + 20, y), (0, 0, 255), 2)
            cv2.line(screen_marked, (x, y - 20), (x, y + 20), (0, 0, 255), 2)

            # 添加文本
            text = f"CLICK: ({x}, {y})"
            cv2.putText(screen_marked, text, (x + 20, y - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            cv2.imwrite(str(marker_path), screen_marked)
            print(f"   [DEBUG] 点击标记已保存: {marker_path}")

        except Exception as e:
            print(f"   [WARNING] 保存点击标记失败: {e}")

    def _save_debug_screenshot(self, path: Path):
        """保存调试截图"""
        try:
            if self.browser:
                screen = self._capture_screen()
                if screen is not None:
                    cv2.imwrite(str(path), screen)
                    print(f"   [DEBUG] 调试截图已保存: {path}")
        except Exception as e:
            print(f"   [WARNING] 保存调试截图失败: {e}")

    def _capture_new_tab(self, page_number: int, element_number: int, element_text: str, image_xpath: str = '', element=None) -> bool:
        """切换到新标签页并截图，并下载指定图片"""
        from selenium.webdriver.common.by import By
        import urllib.request

        original_window = None
        original_url = None

        try:
            # 重试3次
            for retry in range(3):
                # 记录当前标签页和URL（点击前）
                original_window = self.browser.driver.current_window_handle
                original_url = self.browser.driver.current_url

                if retry == 0:
                    print(f"    [DEBUG] 列表页URL: {original_url[:70]}...")

                # 等待新标签页打开并加载
                if retry == 0:
                    print(f"    [DEBUG] 等待新标签页打开...")
                time.sleep(2)

                # 切换到最新的标签页
                all_windows = self.browser.driver.window_handles
                latest_window = all_windows[-1]

                if retry == 0:
                    print(f"    [DEBUG] 切换到最新标签页 (共{len(all_windows)}个标签页)")
                self.browser.driver.switch_to.window(latest_window)

                # 等待页面加载
                time.sleep(1)

                # 获取新标签页的URL
                new_tab_url = self.browser.driver.current_url
                if retry == 0:
                    print(f"    [DEBUG] 新标签页URL: {new_tab_url[:70]}...")

                # 对比URL
                if new_tab_url == original_url:
                    if retry < 2 and element:
                        print(f"    [WARNING] URL相同，点击未生效，准备重试 ({retry + 1}/3)...")
                        # 切换回原标签页
                        self.browser.driver.switch_to.window(original_window)
                        # 重新点击元素
                        try:
                            self._try_click_element(element, element_number, silent=True)
                            continue
                        except Exception as e:
                            print(f"    [ERROR] 重试点击失败: {e}")
                            return False
                    else:
                        print(f"    [INFO] URL相同，重试3次后仍失败，跳过截图")
                        # 切换回原标签页
                        self.browser.driver.switch_to.window(original_window)
                        return False

                # URL不同，成功
                print(f"    [INFO] URL不同，新标签页有新内容")
                break

            # 创建58_data1目录（用于保存截图和图片）
            data_dir1 = Path('58_data1')
            data_dir1.mkdir(parents=True, exist_ok=True)

            # 生成文件名
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            safe_text = "".join(c for c in element_text[:30] if c.isalnum() or c in (' ', '-', '_')).strip()
            if safe_text:
                base_filename = f"P{page_number}_E{element_number}_{safe_text}_{timestamp}"
            else:
                base_filename = f"P{page_number}_E{element_number}_{timestamp}"

            # 创建子目录用于保存本次的截图和图片
            image_subdir = data_dir1 / base_filename
            image_subdir.mkdir(parents=True, exist_ok=True)

            # 截图并保存到同一目录
            screenshot_path = image_subdir / f"{base_filename}.png"

            # 等待页面完全渲染
            time.sleep(1)

            screenshot_binary = self.browser.driver.get_screenshot_as_png()
            img = Image.open(BytesIO(screenshot_binary))
            img.save(str(screenshot_path))

            print(f"    [OK] 截图已保存: {base_filename}.png")

            # 下载前4张图片（xtu_0, xtu_1, xtu_2, xtu_3）
            if image_xpath:
                print(f"    [INFO] 开始下载图片...")

                try:

                    downloaded_count = 0
                    # 只下载前4张图片，ID从xtu_0到xtu_3
                    for i in range(4):
                        img_xpath = f'//*[@id="xtu_{i}"]/img'
                        try:
                            # 查找匹配的图片元素
                            img_elements = self.browser.driver.find_elements(By.XPATH, img_xpath)

                            if not img_elements:
                                print(f"    [DEBUG] XPath '{img_xpath}' 未找到图片")
                                continue

                            print(f"    [DEBUG] XPath '{img_xpath}' 找到 {len(img_elements)} 张图片")

                            # 只下载第一张图片
                            img_element = img_elements[0]
                            try:
                                # 获取图片URL
                                img_url = img_element.get_attribute('src')

                                if not img_url:
                                    print(f"    [DEBUG] 图片 {i+1} 没有src属性")
                                    continue

                                # 处理相对URL
                                if not img_url.startswith('http'):
                                    if img_url.startswith('//'):
                                        img_url = 'https:' + img_url
                                    elif img_url.startswith('/'):
                                        img_url = new_tab_url.rstrip('/') + '/' + img_url.lstrip('/')

                                # 生成图片文件名
                                img_extension = '.jpg'
                                if '.png' in img_url.lower():
                                    img_extension = '.png'
                                elif '.jpeg' in img_url.lower():
                                    img_extension = '.jpeg'

                                img_filename = f"image_{i+1}{img_extension}"
                                img_save_path = image_subdir / img_filename

                                # 下载图片
                                print(f"    [DEBUG] 下载图片 {i+1}: {img_url[:60]}...")
                                urllib.request.urlretrieve(img_url, str(img_save_path))
                                downloaded_count += 1
                                print(f"    [OK] 已保存: {img_filename}")

                            except Exception as e:
                                print(f"    [WARNING] 下载图片 {i+1} 失败: {e}")

                        except Exception as e:
                            print(f"    [WARNING] XPath '{img_xpath}' 处理失败: {e}")

                    if downloaded_count > 0:
                        print(f"    [OK] 共下载 {downloaded_count} 张图片到 {image_subdir}")
                    else:
                        print(f"    [WARNING] 未下载到任何图片")

                except Exception as e:
                    print(f"    [ERROR] 下载图片失败: {e}")
                    import traceback
                    traceback.print_exc()

            # 关闭当前标签页（新标签页）
            print(f"    [DEBUG] 关闭新标签页...")
            try:
                self.browser.driver.close()
                print(f"    [DEBUG] 已关闭新标签页")
            except Exception as e:
                print(f"    [WARNING] 关闭标签页失败: {e}")

            # 切换回原标签页
            try:
                self.browser.driver.switch_to.window(original_window)
                print(f"    [DEBUG] 已返回列表页")
            except Exception as e:
                print(f"    [WARNING] 返回列表页失败: {e}")
                try:
                    all_windows = self.browser.driver.window_handles
                    if len(all_windows) > 0:
                        self.browser.driver.switch_to.window(all_windows[0])
                except:
                    pass

            # 等待页面恢复
            time.sleep(0.5)

            return True

        except Exception as e:
            print(f"    [ERROR] 截图失败: {e}")
            import traceback
            traceback.print_exc()

            # 尝试恢复
            try:
                if original_window:
                    self.browser.driver.switch_to.window(original_window)
            except:
                pass

            return False


# ============================================================================
# 主程序
# ============================================================================

def main():
    """主函数"""
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 创建执行器
    executor = OperationExecutor(CONFIG)

    # 执行操作序列
    success = executor.execute(OPERATIONS)

    if success:
        print("\n[OK] 脚本执行成功!")
    else:
        print("\n[X] 脚本执行失败")

    return success


if __name__ == "__main__":
    print("58同城自动化脚本 V2")
    print("=" * 70)
    print("\n提示:")
    print("1. 修改脚本中的 OPERATIONS 列表来定义操作流程")
    print("2. 在 images/58/58_templates/ 目录下放置模板图片")
    print("3. 运行脚本\n")

    success = main()

    input("\n按回车键退出...")
