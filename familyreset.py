"""
FamilyReset - ブラウザ自動化ツールクラス

テキストで要素を認識して操作を実行、XPathの手動検索が不要

基本例:
    fr = FamilyReset()
    fr.open('https://example.com') \\
      .click_text('登录')           \\  # 点击包含"登录"文字的元素
      .input_text('用户名', 'admin') \\  # 在"用户名"关联的输入框输入
      .input_text('密码', '123456')  \\  # 在"密码"关联的输入框输入
      .click_text('提交')            \\  # 点击提交按钮
      .wait(3)                       \\  # 等待3秒
      .screenshot()                      # 截图

高级功能:
    # 元素操作
    fr.double_click_text('文件')       # 双击
    fr.hover_text('菜单')               # 鼠标悬停
    fr.right_click_text('对象')         # 右键点击

    # 输入操作
    fr.input_and_enter('搜索', '关键词')  # 输入后回车
    fr.clear_input('用户名')              # 清空输入框
    fr.check_element('同意条款')          # 勾选复选框

    # 滚动操作
    fr.scroll(500)                       # 向下滚动500像素
    fr.scroll_to_text('底部')            # 滚动到指定文字
    fr.scroll_to_top()                   # 滚动到顶部
    fr.scroll_to_bottom()                # 滚动到底部

    # 页面操作
    fr.back()                            # 后退
    fr.forward()                         # 前进
    fr.refresh()                         # 刷新
    url = fr.get_url()                   # 获取当前URL
    title = fr.get_title()               # 获取页面标题

    # 元素信息
    text = fr.get_text('标题')           # 获取元素文本
    href = fr.get_attr('链接', 'href')   # 获取元素属性
    exists = fr.exists('按钮')           # 检查元素是否存在

    # 等待操作
    fr.wait_for_text('加载完成', timeout=30)  # 等待文字出现
    fr.wait(5)                               # 等待5秒

    # JavaScript
    fr.execute_js('alert("Hello")')     # 执行JavaScript代码
"""

import time
import logging
from typing import Optional, List, Tuple, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

from src.core.browser import BrowserController

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FamilyReset:
    """
    FamilyReset 浏览器自动化工具类

    通过文字自动识别元素并执行操作
    """

    def __init__(self, browser_type: str = 'chrome', headless: bool = False):
        """
        初始化

        Args:
            browser_type: 浏览器类型 ('chrome', 'firefox', 'edge')
            headless: 是否无头模式
        """
        self.browser = BrowserController(
            browser_type=browser_type,
            headless=headless
        )
        self.driver = self.browser.driver
        logger.info(f"FamilyReset 初始化完成 (浏览器: {browser_type})")

    # ========================================================================
    # 基础操作
    # ========================================================================

    def open(self, url: str) -> 'FamilyReset':
        """
        打开网址

        Args:
            url: 目标网址

        Returns:
            self，支持链式调用
        """
        logger.info(f"打开网址: {url}")
        self.browser.open(url)
        return self

    def wait(self, seconds: float) -> 'FamilyReset':
        """
        等待指定时间

        Args:
            seconds: 等待秒数

        Returns:
            self，支持链式调用
        """
        logger.info(f"等待 {seconds} 秒")
        time.sleep(seconds)
        return self

    def screenshot(self, filename: str = None) -> 'FamilyReset':
        """
        截图

        Args:
            filename: 文件名

        Returns:
            self，支持链式调用
        """
        path = self.browser.screenshot(filename)
        logger.info(f"截图已保存: {path}")
        return self

    # ========================================================================
    # 通过文字操作元素
    # ========================================================================

    def find_element_by_text(self, text: str, exact_match: bool = True,
                             timeout: int = 10) -> Optional[Any]:
        """
        通过文字查找元素

        Args:
            text: 要查找的文字
            exact_match: 是否精确匹配（True=完全相等，False=包含即可）
            timeout: 超时时间（秒）

        Returns:
            找到的元素，未找到返回 None
        """
        logger.info(f"查找文字: '{text}' (精确匹配: {exact_match})")

        # 构建多个 XPath 表达式尝试
        if exact_match:
            xpaths = [
                f"//*[normalize-space(text())='{text}']",  # 精确匹配（忽略空格）
                f"//*[text()='{text}']",  # 完全精确匹配
                f"//input[@value='{text}']",  # 按钮的 value 属性
                f"//button[normalize-space(text())='{text}']",  # 按钮精确匹配
            ]
        else:
            xpaths = [
                f"//*[contains(text(), '{text}')]",  # 包含文字
                f"//*[contains(normalize-space(text()), '{text}')]",  # 包含文字（忽略空格）
                f"//input[contains(@value, '{text}')]",  # 按钮的 value
                f"//button[contains(text(), '{text}')]",  # 按钮包含
            ]

        # 尝试每个 XPath
        for xpath in xpaths:
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                logger.info(f"✓ 找到元素: {element.tag_name}")
                return element
            except TimeoutException:
                continue

        logger.warning(f"✗ 未找到包含 '{text}' 的元素")
        return None

    def click_text(self, text: str, exact_match: bool = True,
                   wait_after: float = 0, timeout: int = 10) -> 'FamilyReset':
        """
        查找并点击包含指定文字的元素

        Args:
            text: 要点击的文字
            exact_match: 是否精确匹配
            wait_after: 点击后等待秒数
            timeout: 查找超时时间

        Returns:
            self，支持链式调用
        """
        element = self.find_element_by_text(text, exact_match, timeout)

        if element is None:
            logger.error(f"无法点击: 未找到 '{text}'")
            return self

        # 滚动到元素
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", element
        )
        time.sleep(0.3)

        # 尝试多种点击方式
        clicked = False

        # 方法1: 标准点击
        try:
            element.click()
            clicked = True
            logger.info(f"✓ 已点击: '{text}' (标准点击)")
        except Exception as e:
            logger.debug(f"标准点击失败: {e}")

        # 方法2: JavaScript 点击
        if not clicked:
            try:
                self.driver.execute_script("arguments[0].click();", element)
                clicked = True
                logger.info(f"✓ 已点击: '{text}' (JavaScript)")
            except Exception as e:
                logger.debug(f"JavaScript 点击失败: {e}")

        # 方法3: ActionChains
        if not clicked:
            try:
                actions = ActionChains(self.driver)
                actions.move_to_element(element).click().perform()
                clicked = True
                logger.info(f"✓ 已点击: '{text}' (ActionChains)")
            except Exception as e:
                logger.debug(f"ActionChains 点击失败: {e}")

        if wait_after > 0:
            time.sleep(wait_after)

        return self

    def click_text_and_save_url(self, text: str, url_file: str = 'clicked_urls.txt',
                                exact_match: bool = True, wait_after: float = 0) -> str:
        """
        点击文本并记录点击后的 URL

        Args:
            text: 要点击的文字
            url_file: URL 保存的文件路径
            exact_match: 是否精确匹配
            wait_after: 点击后等待秒数

        Returns:
            点击后的 URL
        """
        # 先点击
        self.click_text(text, exact_match=exact_match, wait_after=wait_after)

        # 等待页面加载
        self.wait(1)

        # 获取当前 URL
        current_url = self.get_url()

        # 保存到文件
        try:
            with open(url_file, 'a', encoding='utf-8') as f:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] 点击 '{text}' -> {current_url}\n")
            logger.info(f"✓ URL 已保存: {current_url}")
        except Exception as e:
            logger.error(f"保存 URL 失败: {e}")

        return current_url

    def load_urls(self, url_file: str = 'clicked_urls.txt') -> list:
        """
        从文件加载所有保存的 URL 记录

        Args:
            url_file: URL 文件路径

        Returns:
            URL 记录列表，每项格式: {'timestamp': str, 'text': str, 'url': str}
        """
        urls = []
        try:
            with open(url_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        # 解析格式: [2026-01-28 10:30:15] 点击 '10d' -> https://example.com
                        import re
                        match = re.match(r'\[([^\]]+)\] 点击 \'([^\']+)\' -> (.+)', line)
                        if match:
                            urls.append({
                                'timestamp': match.group(1),
                                'text': match.group(2),
                                'url': match.group(3)
                            })
            logger.info(f"✓ 加载了 {len(urls)} 条 URL 记录")
        except FileNotFoundError:
            logger.warning(f"URL 文件不存在: {url_file}")
        except Exception as e:
            logger.error(f"加载 URL 失败: {e}")
        return urls

    def get_latest_url(self, text: str = None, url_file: str = 'clicked_urls.txt') -> str:
        """
        获取指定文本对应的最新 URL

        Args:
            text: 点击的文字（None 表示获取最后一条记录）
            url_file: URL 文件路径

        Returns:
            URL 字符串，未找到返回 None
        """
        urls = self.load_urls(url_file)
        if not urls:
            return None

        if text:
            # 查找指定文字的最新 URL
            for record in reversed(urls):
                if text in record['text'] or record['text'] == text:
                    logger.info(f"找到 '{text}' 的最新 URL: {record['url']}")
                    return record['url']
            logger.warning(f"未找到 '{text}' 的 URL 记录")
            return None
        else:
            # 返回最后一条记录
            latest = urls[-1]
            logger.info(f"最新 URL: {latest['url']} (点击文字: '{latest['text']}')")
            return latest['url']

    def get_all_urls(self, url_file: str = 'clicked_urls.txt') -> list:
        """
        获取所有保存的 URL 记录

        Args:
            url_file: URL 文件路径

        Returns:
            URL 记录列表
        """
        return self.load_urls(url_file)

    def filter_urls_by_text(self, text: str, url_file: str = 'clicked_urls.txt') -> list:
        """
        根据文字过滤 URL 记录

        Args:
            text: 要匹配的文字（支持模糊匹配）
            url_file: URL 文件路径

        Returns:
            匹配的 URL 记录列表
        """
        urls = self.load_urls(url_file)
        filtered = []
        for record in urls:
            if text in record['text'] or record['text'] == text:
                filtered.append(record)
        logger.info(f"找到 {len(filtered)} 条包含 '{text}' 的 URL 记录")
        return filtered

    def open_saved_url(self, text: str = None, url_file: str = 'clicked_urls.txt') -> 'FamilyReset':
        """
        打开已保存的 URL

        Args:
            text: 点击的文字（None 表示打开最后一条记录的 URL）
            url_file: URL 文件路径

        Returns:
            self，支持链式调用
        """
        url = self.get_latest_url(text, url_file)
        if url:
            logger.info(f"打开已保存的 URL: {url}")
            self.open(url)
        else:
            logger.error(f"未找到要打开的 URL")
        return self

    def input_text(self, label_text: str, value: str,
                   exact_match: bool = True, find_input: bool = True,
                   timeout: int = 10) -> 'FamilyReset':
        """
        根据标签文字查找关联的输入框并输入文本

        Args:
            label_text: 标签文字（如"用户名"、"密码"等）
            value: 要输入的值
            exact_match: 是否精确匹配标签
            find_input: 是否查找关联的输入框（False则直接在找到的元素上输入）
            timeout: 超时时间

        Returns:
            self，支持链式调用
        """
        logger.info(f"输入文本: 标签='{label_text}', 值='{value}'")

        # 查找标签元素
        label = self.find_element_by_text(label_text, exact_match, timeout)

        if label is None:
            logger.error(f"无法输入: 未找到标签 '{label_text}'")
            return self

        # 查找关联的输入框
        input_element = None

        if find_input:
            # 方法1: 通过 label 的 for 属性
            try:
                label_for = label.get_attribute('for')
                if label_for:
                    input_element = self.driver.find_element(By.ID, label_for)
                    logger.info(f"  通过 for 属性找到输入框")
            except:
                pass

            # 方法2: 查找同级或父级的输入框
            if input_element is None:
                try:
                    # 查找父元素
                    parent = label.find_element(By.XPATH, '..')

                    # 在父元素中查找输入框
                    inputs = parent.find_elements(By.TAG_NAME, 'input')

                    # 优先查找 type=text 或 type=password 的
                    for inp in inputs:
                        inp_type = inp.get_attribute('type') or 'text'
                        if inp_type in ['text', 'password', 'email', 'search']:
                            input_element = inp
                            logger.info(f"  在同级元素中找到输入框 (type={inp_type})")
                            break

                    # 如果没找到，取第一个输入框
                    if input_element is None and inputs:
                        input_element = inputs[0]
                        logger.info(f"  在同级元素中找到输入框")
                except:
                    pass

            # 方法3: 查找相邻的输入框
            if input_element is None:
                try:
                    following = label.find_elements(By.XPATH, './following::input[1]')
                    if following:
                        input_element = following[0]
                        logger.info(f"  在后续元素中找到输入框")
                except:
                    pass

        # 如果找到的标签本身就是输入框（如 button value="登录"）
        if input_element is None and label.tag_name == 'input':
            input_element = label
            logger.info(f"  标签本身就是输入框")

        if input_element is None:
            logger.error(f"无法输入: 未找到 '{label_text}' 关联的输入框")
            return self

        # 输入文本
        try:
            input_element.clear()
            input_element.send_keys(value)
            logger.info(f"✓ 已输入: '{value}'")
        except Exception as e:
            logger.error(f"输入失败: {e}")

        return self

    def select_option(self, select_text: str, option_text: str,
                      exact_match: bool = True, timeout: int = 10) -> 'FamilyReset':
        """
        根据下拉框标签选择选项

        Args:
            select_text: 下拉框标签文字
            option_text: 要选择的选项文字
            exact_match: 是否精确匹配标签
            timeout: 超时时间

        Returns:
            self，支持链式调用
        """
        logger.info(f"选择下拉框: 标签='{select_text}', 选项='{option_text}'")

        # 查找 select 元素（使用 input_text 的逻辑）
        label = self.find_element_by_text(select_text, exact_match, timeout)

        if label is None:
            logger.error(f"未找到标签 '{select_text}'")
            return self

        # 查找关联的 select 元素
        select_element = None

        try:
            # 通过 for 属性
            label_for = label.get_attribute('for')
            if label_for:
                select_element = self.driver.find_element(By.ID, label_for)
        except:
            pass

        if select_element is None:
            try:
                # 查找同级
                parent = label.find_element(By.XPATH, '..')
                selects = parent.find_elements(By.TAG_NAME, 'select')
                if selects:
                    select_element = selects[0]
            except:
                pass

        if select_element is None:
            logger.error(f"未找到 '{select_text}' 关联的下拉框")
            return self

        # 选择选项
        try:
            from selenium.webdriver.support.ui import Select
            select = Select(select_element)
            select.select_by_visible_text(option_text)
            logger.info(f"✓ 已选择: '{option_text}'")
        except Exception as e:
            logger.error(f"选择失败: {e}")

        return self

    # ========================================================================
    # 列表操作
    # ========================================================================

    def find_all_by_text(self, text: str, exact_match: bool = True,
                         timeout: int = 10) -> List[Any]:
        """
        查找所有包含指定文字的元素

        Args:
            text: 要查找的文字
            exact_match: 是否精确匹配
            timeout: 超时时间

        Returns:
            元素列表
        """
        logger.info(f"查找所有包含 '{text}' 的元素")

        # 构建多个 XPath 表达式尝试
        if exact_match:
            xpaths = [
                f"//*[normalize-space(text())='{text}']",
                f"//*[text()='{text}']",
                f"//input[@value='{text}']",
                f"//button[normalize-space(text())='{text}']",
                f"//a[normalize-space(text())='{text}']",
                f"//li[normalize-space(text())='{text}']",
            ]
        else:
            xpaths = [
                f"//*[contains(text(), '{text}')]",
                f"//*[contains(normalize-space(text()), '{text}')]",
                f"//input[contains(@value, '{text}')]",
                f"//button[contains(text(), '{text}')]",
                f"//a[contains(text(), '{text}')]",
                f"//li[contains(text(), '{text}')]",
            ]

        # 尝试每个 XPath
        for xpath in xpaths:
            try:
                elements = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_all_elements_located((By.XPATH, xpath))
                )
                if elements:
                    logger.info(f"✓ 找到 {len(elements)} 个元素")
                    return elements
            except TimeoutException:
                continue

        logger.warning(f"✗ 未找到包含 '{text}' 的元素")
        return []

    def get_list_items(self, list_selector: str = None,
                       timeout: int = 10) -> List[dict]:
        """
        获取列表项（自动识别常见的列表结构）

        Args:
            list_selector: 可选的列表容器选择器（XPath）
            timeout: 超时时间

        Returns:
            列表项字典列表: [{'index': 0, 'text': '内容', 'element': element}, ...]
        """
        logger.info("获取列表项")

        items = []

        try:
            # 尝试多种列表结构
            list_types = []

            # 如果提供了选择器
            if list_selector:
                list_types.append(('custom', (By.XPATH, list_selector)))

            # 常见的列表结构
            list_types.extend([
                ('ul', (By.TAG_NAME, 'ul')),
                ('ol', (By.TAG_NAME, 'ol')),
                ('table', (By.TAG_NAME, 'table')),
                ('div[class*="list"]', (By.XPATH, '//div[contains(@class, "list")]')),
                ('div[class*="item"]', (By.XPATH, '//div[contains(@class, "item")]')),
            ])

            for list_type, locator in list_types:
                try:
                    if list_type == 'table':
                        # 表格特殊处理
                        tables = self.driver.find_elements(*locator)
                        for table in tables:
                            rows = table.find_elements(By.TAG_NAME, 'tr')
                            for idx, row in enumerate(rows):
                                cells = row.find_elements(By.TAG_NAME, 'td')
                                if cells:
                                    text = ' | '.join([cell.text.strip() for cell in cells if cell.text.strip()])
                                    if text:
                                        items.append({
                                            'index': len(items),
                                            'text': text,
                                            'element': row
                                        })
                    elif list_type == 'custom':
                        # 自定义选择器
                        elements = self.driver.find_elements(*locator)
                        for idx, elem in enumerate(elements):
                            text = elem.text.strip()
                            if text:
                                items.append({
                                    'index': idx,
                                    'text': text,
                                    'element': elem
                                })
                        break  # 自定义选择器优先
                    else:
                        # ul, ol, div等
                        elements = self.driver.find_elements(*locator)
                        for list_elem in elements:
                            children = list_elem.find_elements(By.TAG_NAME, 'li')
                            if not children:
                                children = list_elem.find_elements(By.XPATH, './*')

                            for child in children:
                                text = child.text.strip()
                                if text and text not in [item['text'] for item in items]:
                                    items.append({
                                        'index': len(items),
                                        'text': text,
                                        'element': child
                                    })

                    if items:
                        logger.info(f"✓ 通过 {list_type} 找到 {len(items)} 个列表项")
                        break

                except Exception as e:
                    logger.debug(f"尝试 {list_type} 失败: {e}")
                    continue

            if not items:
                logger.warning("未找到列表项")

        except Exception as e:
            logger.error(f"获取列表项失败: {e}")

        return items

    def get_text_list(self, xpath: str = None) -> List[str]:
        """
        获取页面上所有文本内容或指定元素的文本

        Args:
            xpath: 可选的XPath表达式，None则获取整个页面的文本

        Returns:
            文本列表
        """
        logger.info("获取文本列表")

        try:
            if xpath:
                elements = self.driver.find_elements(By.XPATH, xpath)
                texts = [elem.text.strip() for elem in elements if elem.text.strip()]
            else:
                # 获取页面所有可见文本
                texts = self.driver.find_elements(By.XPATH, '//*[text()]')
                texts = [t.strip() for t in [elem.text for elem in texts] if t.strip()]

            logger.info(f"✓ 获取到 {len(texts)} 个文本")
            return texts

        except Exception as e:
            logger.error(f"获取文本列表失败: {e}")
            return []

    def click_list_item(self, index: int, list_selector: str = None,
                        wait_after: float = 0) -> 'FamilyReset':
        """
        点击列表中的第N项

        Args:
            index: 列表索引（从0开始）
            list_selector: 可选的列表选择器
            wait_after: 点击后等待秒数

        Returns:
            self，支持链式调用
        """
        logger.info(f"点击列表第 {index} 项")

        items = self.get_list_items(list_selector)

        if index < 0 or index >= len(items):
            logger.error(f"索引超出范围: 0-{len(items)-1}")
            return self

        try:
            element = items[index]['element']
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", element
            )
            time.sleep(0.3)
            element.click()
            logger.info(f"✓ 已点击: {items[index]['text']}")

            if wait_after > 0:
                time.sleep(wait_after)

        except Exception as e:
            logger.error(f"点击列表项失败: {e}")

        return self

    def select_and_click_list(self, list_selector: str = None,
                              prompt: str = "请选择要操作的项") -> 'FamilyReset':
        """
        显示列表让用户选择，然后点击选中的项

        Args:
            list_selector: 可选的列表选择器
            prompt: 提示文字

        Returns:
            self，支持链式调用
        """
        items = self.get_list_items(list_selector)

        if not items:
            logger.error("没有可选择的列表项")
            return self

        print("\n" + "="*70)
        print(prompt)
        print("="*70)

        for item in items:
            print(f"  [{item['index']}] {item['text']}")

        print("="*70)

        try:
            choice = input(f"\n请输入选项 (0-{len(items)-1}): ").strip()

            if not choice.isdigit():
                logger.error("无效输入")
                return self

            index = int(choice)

            if index < 0 or index >= len(items):
                logger.error(f"索引超出范围: 0-{len(items)-1}")
                return self

            # 点击选中的项
            try:
                element = items[index]['element']
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", element
                )
                time.sleep(0.3)
                element.click()
                logger.info(f"✓ 已点击: {items[index]['text']}")
            except Exception as e:
                logger.error(f"点击失败: {e}")

        except KeyboardInterrupt:
            logger.info("用户取消选择")

        return self

    def click_text_match(self, pattern: str, exact_match: bool = False,
                         timeout: int = 10, wait_after: float = 0) -> 'FamilyReset':
        """
        查找并点击包含匹配模式的文本元素

        Args:
            pattern: 匹配模式（支持部分匹配）
            exact_match: 是否精确匹配
            timeout: 超时时间
            wait_after: 点击后等待秒数

        Returns:
            self，支持链式调用
        """
        logger.info(f"查找并点击匹配 '{pattern}' 的元素")

        elements = self.find_all_by_text(pattern, exact_match, timeout)

        if not elements:
            logger.error(f"未找到匹配 '{pattern}' 的元素")
            return self

        # 点击第一个匹配的元素
        element = elements[0]
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", element
        )
        time.sleep(0.3)
        element.click()
        logger.info(f"✓ 已点击: {element.text[:50]}")

        if wait_after > 0:
            time.sleep(wait_after)

        return self

    # ========================================================================
    # 获取元素信息
    # ========================================================================

    def get_text(self, text: str, exact_match: bool = True,
                 timeout: int = 10) -> Optional[str]:
        """
        获取包含指定文字的元素的文本内容

        Args:
            text: 要查找的文字
            exact_match: 是否精确匹配
            timeout: 超时时间

        Returns:
            元素的文本内容，未找到返回 None
        """
        element = self.find_element_by_text(text, exact_match, timeout)
        if element:
            text_content = element.text
            logger.info(f"获取文本: '{text_content}'")
            return text_content
        return None

    def get_attr(self, text: str, attr_name: str,
                 exact_match: bool = True, timeout: int = 10) -> Optional[str]:
        """
        获取包含指定文字的元素的属性值

        Args:
            text: 要查找的文字
            attr_name: 属性名（如 'href', 'id', 'class' 等）
            exact_match: 是否精确匹配
            timeout: 超时时间

        Returns:
            属性值，未找到返回 None
        """
        element = self.find_element_by_text(text, exact_match, timeout)
        if element:
            attr_value = element.get_attribute(attr_name)
            logger.info(f"获取属性 {attr_name}: '{attr_value}'")
            return attr_value
        return None

    def exists(self, text: str, exact_match: bool = True,
               timeout: int = 5) -> bool:
        """
        检查包含指定文字的元素是否存在

        Args:
            text: 要查找的文字
            exact_match: 是否精确匹配
            timeout: 超时时间

        Returns:
            True 表示存在，False 表示不存在
        """
        element = self.find_element_by_text(text, exact_match, timeout)
        exists = element is not None
        logger.info(f"元素 '{text}' {'存在' if exists else '不存在'}")
        return exists

    def exists_xpath(self, xpath: str, timeout: int = 2) -> bool:
        """
        检查 XPath 元素是否存在

        Args:
            xpath: XPath 表达式
            timeout: 超时时间（秒）

        Returns:
            True 表示存在，False 表示不存在
        """
        try:
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.common.by import By

            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            return True
        except:
            return False

    def wait_for_text(self, text: str, exact_match: bool = True,
                      timeout: int = 30) -> bool:
        """
        等待包含指定文字的元素出现

        Args:
            text: 要等待的文字
            exact_match: 是否精确匹配
            timeout: 最长等待时间

        Returns:
            True 表示元素出现，False 表示超时
        """
        logger.info(f"等待文字出现: '{text}' (最长 {timeout} 秒)")
        element = self.find_element_by_text(text, exact_match, timeout)
        return element is not None

    # ========================================================================
    # 点击操作（扩展）
    # ========================================================================

    def click_xpath(self, xpath: str, index: int = 0,
                    wait_after: float = 0) -> 'FamilyReset':
        """
        通过 XPath 点击元素

        Args:
            xpath: XPath 表达式
            index: 元素索引（当有多个匹配时）
            wait_after: 点击后等待秒数

        Returns:
            self，支持链式调用
        """
        logger.info(f"通过 XPath 点击: {xpath} (索引: {index})")

        try:
            elements = self.driver.find_elements(By.XPATH, xpath)

            if not elements:
                logger.error(f"未找到 XPath 元素: {xpath}")
                return self

            if len(elements) <= index:
                logger.error(f"索引超出范围: 找到 {len(elements)} 个元素，请求索引 {index}")
                return self

            element = elements[index]
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", element
            )
            time.sleep(0.3)
            element.click()
            logger.info(f"✓ 已点击第 {index + 1} 个元素")

            if wait_after > 0:
                time.sleep(wait_after)

        except Exception as e:
            logger.error(f"XPath 点击失败: {e}")

        return self

    def double_click_text(self, text: str, exact_match: bool = True,
                          wait_after: float = 0) -> 'FamilyReset':
        """
        双击包含指定文字的元素

        Args:
            text: 要双击的文字
            exact_match: 是否精确匹配
            wait_after: 双击后等待秒数

        Returns:
            self，支持链式调用
        """
        logger.info(f"双击文字: '{text}'")

        element = self.find_element_by_text(text, exact_match)

        if element:
            try:
                actions = ActionChains(self.driver)
                actions.double_click(element).perform()
                logger.info(f"✓ 已双击: '{text}'")

                if wait_after > 0:
                    time.sleep(wait_after)
            except Exception as e:
                logger.error(f"双击失败: {e}")

        return self

    def hover_text(self, text: str, exact_match: bool = True,
                   wait_after: float = 0) -> 'FamilyReset':
        """
        鼠标悬停在包含指定文字的元素上

        Args:
            text: 目标文字
            exact_match: 是否精确匹配
            wait_after: 悬停后等待秒数

        Returns:
            self，支持链式调用
        """
        logger.info(f"鼠标悬停: '{text}'")

        element = self.find_element_by_text(text, exact_match)

        if element:
            try:
                actions = ActionChains(self.driver)
                actions.move_to_element(element).perform()
                logger.info(f"✓ 已悬停: '{text}'")

                if wait_after > 0:
                    time.sleep(wait_after)
            except Exception as e:
                logger.error(f"悬停失败: {e}")

        return self

    # ========================================================================
    # 输入操作（扩展）
    # ========================================================================

    def input_and_enter(self, label_text: str, value: str,
                        exact_match: bool = True) -> 'FamilyReset':
        """
        在输入框输入文本后按回车键

        Args:
            label_text: 标签文字
            value: 要输入的值
            exact_match: 是否精确匹配标签

        Returns:
            self，支持链式调用
        """
        logger.info(f"输入并回车: 标签='{label_text}', 值='{value}'")

        # 查找标签元素
        label = self.find_element_by_text(label_text, exact_match)

        if label is None:
            logger.error(f"未找到标签 '{label_text}'")
            return self

        # 查找关联的输入框
        input_element = None

        try:
            parent = label.find_element(By.XPATH, '..')
            inputs = parent.find_elements(By.TAG_NAME, 'input')

            for inp in inputs:
                inp_type = inp.get_attribute('type') or 'text'
                if inp_type in ['text', 'password', 'email', 'search']:
                    input_element = inp
                    break

            if input_element is None and inputs:
                input_element = inputs[0]
        except:
            pass

        if input_element is None:
            logger.error(f"未找到 '{label_text}' 关联的输入框")
            return self

        # 输入并按回车
        try:
            from selenium.webdriver.common.keys import Keys
            input_element.clear()
            input_element.send_keys(value)
            input_element.send_keys(Keys.RETURN)
            logger.info(f"✓ 已输入并回车: '{value}'")
            time.sleep(1)  # 等待提交
        except Exception as e:
            logger.error(f"输入并回车失败: {e}")

        return self

    def clear_input(self, label_text: str,
                    exact_match: bool = True) -> 'FamilyReset':
        """
        清空输入框

        Args:
            label_text: 标签文字
            exact_match: 是否精确匹配

        Returns:
            self，支持链式调用
        """
        logger.info(f"清空输入框: '{label_text}'")

        label = self.find_element_by_text(label_text, exact_match)

        if label:
            try:
                parent = label.find_element(By.XPATH, '..')
                inputs = parent.find_elements(By.TAG_NAME, 'input')

                if inputs:
                    inputs[0].clear()
                    logger.info(f"✓ 已清空: '{label_text}'")
            except Exception as e:
                logger.error(f"清空失败: {e}")

        return self

    # ========================================================================
    # 复选框/单选框操作
    # ========================================================================

    def check_element(self, label_text: str, check: bool = True,
                      exact_match: bool = True) -> 'FamilyReset':
        """
        勾选或取消勾选复选框/单选框

        Args:
            label_text: 标签文字
            check: True 表示勾选，False 表示取消勾选
            exact_match: 是否精确匹配

        Returns:
            self，支持链式调用
        """
        action = "勾选" if check else "取消勾选"
        logger.info(f"{action}: '{label_text}'")

        label = self.find_element_by_text(label_text, exact_match)

        if not label:
            logger.error(f"未找到标签: '{label_text}'")
            return self

        input_element = None

        # 方法1: 检查 label 本身是否是 input
        if label.tag_name == 'input':
            inp_type = label.get_attribute('type')
            if inp_type in ['checkbox', 'radio']:
                input_element = label
                logger.debug("  标签本身就是 input")

        # 方法2: 通过 label 的 for 属性查找
        if input_element is None:
            try:
                label_for = label.get_attribute('for')
                if label_for:
                    input_element = self.driver.find_element(By.ID, label_for)
                    logger.debug(f"  通过 for 属性找到: #{label_for}")
            except:
                pass

        # 方法3: 在父元素中查找
        if input_element is None:
            try:
                parent = label.find_element(By.XPATH, '..')
                inputs = parent.find_elements(By.TAG_NAME, 'input')
                for inp in inputs:
                    inp_type = inp.get_attribute('type')
                    if inp_type in ['checkbox', 'radio']:
                        input_element = inp
                        logger.debug("  在父元素中找到 input")
                        break
            except:
                pass

        # 方法4: 在相邻元素中查找（前面的 input）
        if input_element is None:
            try:
                preceding = label.find_elements(By.XPATH, './preceding::input[1]')
                for inp in preceding:
                    inp_type = inp.get_attribute('type')
                    if inp_type in ['checkbox', 'radio']:
                        input_element = inp
                        logger.debug("  在前面的元素中找到 input")
                        break
            except:
                pass

        # 方法5: 在相邻元素中查找（后面的 input）
        if input_element is None:
            try:
                following = label.find_elements(By.XPATH, './following::input[1]')
                for inp in following:
                    inp_type = inp.get_attribute('type')
                    if inp_type in ['checkbox', 'radio']:
                        input_element = inp
                        logger.debug("  在后面的元素中找到 input")
                        break
            except:
                pass

        # 执行勾选/取消勾选
        if input_element:
            try:
                is_selected = input_element.is_selected()

                # 滚动到元素
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", input_element
                )
                time.sleep(0.3)

                # 判断是否需要点击
                if check and not is_selected:
                    input_element.click()
                    logger.info(f"✓ 已勾选: '{label_text}'")
                elif not check and is_selected:
                    input_element.click()
                    logger.info(f"✓ 已取消勾选: '{label_text}'")
                else:
                    logger.info(f"  状态已正确，无需操作: '{label_text}'")

            except Exception as e:
                logger.error(f"{action}失败: {e}")
                # 尝试使用 JavaScript 点击
                try:
                    self.driver.execute_script("arguments[0].click();", input_element)
                    logger.info(f"✓ 使用JavaScript {action}成功: '{label_text}'")
                except:
                    logger.error(f"JavaScript点击也失败")
        else:
            logger.error(f"未找到 '{label_text}' 关联的复选框/单选框")

        return self

    # ========================================================================
    # 滚动操作
    # ========================================================================

    def scroll(self, amount: int = 500) -> 'FamilyReset':
        """
        滚动页面

        Args:
            amount: 滚动像素（正数向下，负数向上）

        Returns:
            self，支持链式调用
        """
        self.driver.execute_script(f"window.scrollBy(0, {amount});")
        logger.info(f"页面滚动: {amount}px")
        return self

    def scroll_to_text(self, text: str, exact_match: bool = True,
                       timeout: int = 10) -> 'FamilyReset':
        """
        滚动到包含指定文字的元素

        Args:
            text: 目标文字
            exact_match: 是否精确匹配
            timeout: 超时时间

        Returns:
            self，支持链式调用
        """
        logger.info(f"滚动到文字: '{text}'")

        element = self.find_element_by_text(text, exact_match, timeout)

        if element:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", element
            )
            time.sleep(0.5)
            logger.info(f"✓ 已滚动到: '{text}'")

        return self

    def scroll_to_top(self) -> 'FamilyReset':
        """滚动到页面顶部"""
        self.driver.execute_script("window.scrollTo(0, 0);")
        logger.info("已滚动到页面顶部")
        return self

    def scroll_to_bottom(self) -> 'FamilyReset':
        """滚动到页面底部"""
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        logger.info("已滚动到页面底部")
        return self

    # ========================================================================
    # 页面操作
    # ========================================================================

    def back(self) -> 'FamilyReset':
        """后退"""
        self.driver.back()
        logger.info("页面后退")
        return self

    def forward(self) -> 'FamilyReset':
        """前进"""
        self.driver.forward()
        logger.info("页面前进")
        return self

    def refresh(self) -> 'FamilyReset':
        """刷新页面"""
        self.driver.refresh()
        logger.info("页面刷新")
        return self

    def get_url(self) -> str:
        """获取当前 URL"""
        url = self.driver.current_url
        logger.info(f"当前 URL: {url}")
        return url

    def get_title(self) -> str:
        """获取页面标题"""
        title = self.driver.title
        logger.info(f"页面标题: {title}")
        return title

    def get_page_source(self) -> str:
        """获取页面 HTML 源码"""
        return self.driver.page_source

    def execute_js(self, script: str, *args) -> Any:
        """
        执行 JavaScript 代码

        Args:
            script: JavaScript 代码
            *args: 传递给 JavaScript 的参数

        Returns:
            执行结果
        """
        result = self.driver.execute_script(script, *args)
        logger.info(f"已执行 JavaScript")
        return result

    # ========================================================================
    # 标签页操作
    # ========================================================================

    def switch_tab(self, index: int = -1) -> 'FamilyReset':
        """
        切换标签页

        Args:
            index: 标签页索引，-1 表示最新的

        Returns:
            self，支持链式调用
        """
        all_windows = self.driver.window_handles

        if not all_windows:
            logger.warning("没有打开的标签页")
            return self

        if index == -1:
            index = len(all_windows) - 1

        self.driver.switch_to.window(all_windows[index])
        logger.info(f"已切换到标签页 {index + 1}/{len(all_windows)}")

        return self

    # ========================================================================
    # 高级操作
    # ========================================================================

    def delete_all_settings(self, target_xpath: str = '//*[@id="__nuxt"]/section/div/a[1]',
                            delete_button_text: str = '設定を削除する',
                            confirm_button_text: str = '削除',
                            max_iterations: int = 100) -> int:
        """
        批量删除设置项

        循环执行以下操作，直到目标元素消失：
        1. 点击目标 XPath 元素（默认第一个）
        2. 点击删除按钮
        3. 确认删除（对话框中的确认按钮）

        Args:
            target_xpath: 目标元素的 XPath（默认 a[1]，每次删除后列表更新）
            delete_button_text: 删除按钮的文字
            confirm_button_text: 确认按钮的文字
            max_iterations: 最大循环次数（防止无限循环）

        Returns:
            删除的项目数量
        """
        logger.info("开始批量删除设置")
        count = 0

        while self.exists_xpath(target_xpath) and count < max_iterations:
            count += 1
            logger.info(f"--- 第 {count} 次删除 ---")

            # 1. 点击目标元素
            logger.info("1. 点击设置项...")
            self.click_xpath(target_xpath)
            self.wait(1)

            # 2. 点击删除按钮
            logger.info(f"2. 点击 '{delete_button_text}'...")
            self.click_text(delete_button_text, exact_match=False)
            self.wait(2.5)  # 增加等待时间，让对话框完全显示

            # 3. 点击确认按钮（对话框中）
            logger.info(f"3. 点击对话框中的 '{confirm_button_text}'...")

            # 尝试多种方式点击确认按钮
            clicked = False

            # 方式1: 通过文字查找并点击（优先精确匹配）
            try:
                # 先尝试精确匹配
                element = self.find_element_by_text(confirm_button_text, exact_match=True, timeout=3)
                if element:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                    time.sleep(0.3)
                    element.click()
                    clicked = True
                    logger.info(f"  ✓ 标准点击成功（精确匹配）")
            except Exception as e:
                logger.debug(f"  精确匹配失败: {e}")

            # 方式2: 使用 JavaScript 点击（优先精确匹配）
            if not clicked:
                try:
                    xpaths = [
                        # 优先精确匹配
                        f"//button[normalize-space(text())='{confirm_button_text}']",
                        f"//a[normalize-space(text())='{confirm_button_text}']",
                        f"//div[normalize-space(text())='{confirm_button_text}']",
                        f"//span[normalize-space(text())='{confirm_button_text}']",
                        f"//*[normalize-space(text())='{confirm_button_text}']",
                        # 如果精确匹配找不到，再用模糊匹配
                        f"//button[contains(text(), '{confirm_button_text}')]",
                        f"//a[contains(text(), '{confirm_button_text}')]",
                        f"//div[contains(text(), '{confirm_button_text}')]",
                        f"//span[contains(text(), '{confirm_button_text}')]",
                        f"//*[contains(text(), '{confirm_button_text}')]",
                    ]
                    for xpath in xpaths:
                        elements = self.driver.find_elements(By.XPATH, xpath)
                        logger.debug(f"  XPath '{xpath}' 找到 {len(elements)} 个元素")
                        for elem in elements:
                            try:
                                if elem.is_displayed() and elem.is_enabled():
                                    self.driver.execute_script("arguments[0].click();", elem)
                                    clicked = True
                                    logger.info(f"  ✓ JavaScript点击成功 (XPath: {xpath})")
                                    time.sleep(0.5)  # 短暂等待确认点击生效
                                    break
                            except Exception as inner_e:
                                logger.debug(f"    点击元素失败: {inner_e}")
                        if clicked:
                            break
                except Exception as e:
                    logger.debug(f"  JavaScript点击失败: {e}")

            # 方式3: 使用 ActionChains
            if not clicked:
                try:
                    elements = self.find_all_by_text(confirm_button_text, exact_match=False, timeout=2)
                    for elem in elements:
                        if elem.is_displayed() and elem.is_enabled():
                            actions = ActionChains(self.driver)
                            actions.move_to_element(elem).click().perform()
                            clicked = True
                            logger.info(f"  ✓ ActionChains点击成功")
                            break
                except Exception as e:
                    logger.debug(f"  ActionChains点击失败: {e}")

            if not clicked:
                logger.warning(f"  ✗ 无法点击确认按钮 '{confirm_button_text}'")
                # 尝试截图以便调试
                self.screenshot(f'failed_click_confirm_{count}')

            self.wait(2)  # 等待删除操作完成

            # 如果点击失败，尝试获取所有包含"削除"的元素信息
            if not clicked:
                logger.warning("尝试查找所有包含'削除'的元素...")
                try:
                    all_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '削除')]")
                    logger.info(f"找到 {len(all_elements)} 个包含'削除'的元素")
                    for i, elem in enumerate(all_elements):
                        try:
                            tag = elem.tag_name
                            text = elem.text[:50] if elem.text else ""
                            visible = elem.is_displayed()
                            enabled = elem.is_enabled()
                            logger.info(f"  [{i+1}] <{tag}> text='{text}' visible={visible} enabled={enabled}")
                        except:
                            pass
                except Exception as e:
                    logger.debug(f"查找元素失败: {e}")

            logger.info(f"✓ 第 {count} 次删除完成")

        # 检查结束原因
        if not self.exists_xpath(target_xpath):
            logger.info(f"[OK] 所有设置已删除，共删除 {count} 项")
        else:
            logger.warning(f"达到最大循环次数 {max_iterations}，可能还有剩余项")

        return count

    def delete_items_in_container(self, container_xpath: str,
                                  delete_button_text: str = '削除',
                                  confirm_button_text: str = None,
                                  confirm_button_xpath: str = None,
                                  max_iterations: int = 100) -> int:
        """
        在指定容器内循环删除项目

        循环执行以下操作，直到容器元素消失：
        1. 检查容器是否存在
        2. 点击容器内的删除按钮
        3. 如果提供了 confirm_button_xpath 或 confirm_button_text，点击确认按钮

        Args:
            container_xpath: 容器元素的 XPath
            delete_button_text: 删除按钮的文字
            confirm_button_text: 确认按钮的文字（可选）
            confirm_button_xpath: 确认按钮的 XPath（可选，如果提供则优先使用，比文字匹配更精准）
            max_iterations: 最大循环次数

        Returns:
            删除的项目数量
        """
        logger.info(f"开始在容器内删除项目: {container_xpath}")
        count = 0

        while self.exists_xpath(container_xpath) and count < max_iterations:
            count += 1
            logger.info(f"--- 第 {count} 次删除 ---")

            try:
                # 1. 获取容器元素
                try:
                    container = self.driver.find_element(By.XPATH, container_xpath)
                    logger.debug(f"找到容器元素")
                except Exception as e:
                    logger.error(f"无法找到容器元素: {e}")
                    logger.info("容器已消失，删除任务结束")
                    break

                # 2. 在容器内查找删除按钮
                clicked = False

                # 方式1: 精确匹配按钮文字（优先尝试）
                try:
                    xpaths = [
                        f"{container_xpath}//button[normalize-space(text())='{delete_button_text}']",
                        f"{container_xpath}//a[normalize-space(text())='{delete_button_text}']",
                        f"{container_xpath}//div[normalize-space(text())='{delete_button_text}']",
                        f"{container_xpath}//span[normalize-space(text())='{delete_button_text}']",
                        f"{container_xpath}//*[normalize-space(text())='{delete_button_text}']",
                        # 模糊匹配
                        f"{container_xpath}//button[contains(text(), '{delete_button_text}')]",
                        f"{container_xpath}//a[contains(text(), '{delete_button_text}')]",
                        f"{container_xpath}//div[contains(text(), '{delete_button_text}')]",
                        f"{container_xpath}//span[contains(text(), '{delete_button_text}')]",
                        f"{container_xpath}//*[contains(text(), '{delete_button_text}')]",
                    ]

                    for xpath in xpaths:
                        elements = self.driver.find_elements(By.XPATH, xpath)
                        logger.info(f"  XPath '{xpath}' 找到 {len(elements)} 个元素")

                        for elem in elements:
                            try:
                                if elem.is_displayed() and elem.is_enabled():
                                    self.driver.execute_script(
                                        "arguments[0].scrollIntoView({block: 'center'});", elem
                                    )
                                    time.sleep(0.3)
                                    elem.click()
                                    clicked = True
                                    logger.info(f"  ✓ 点击成功: {delete_button_text}")
                                    time.sleep(0.5)
                                    break
                            except Exception as inner_e:
                                logger.debug(f"    点击元素失败: {inner_e}")
                        if clicked:
                            break

                except Exception as e:
                    logger.debug(f"查找删除按钮失败（方式1）: {e}")

                # 方式2: 直接在容器内查找所有元素
                if not clicked:
                    try:
                        # 查找容器内所有包含该文字的元素
                        all_elements = container.find_elements(By.XPATH, f".//*[contains(text(), '{delete_button_text}')]")
                        logger.info(f"  容器内查找：找到 {len(all_elements)} 个包含 '{delete_button_text}' 的元素")

                        # 优先选择精确匹配的元素
                        exact_matches = []
                        partial_matches = []

                        for elem in all_elements:
                            try:
                                elem_text = elem.text.strip()
                                if elem_text == delete_button_text:
                                    exact_matches.append(elem)
                                elif delete_button_text in elem_text:
                                    partial_matches.append(elem)
                            except:
                                pass

                        # 优先使用精确匹配
                        candidates = exact_matches if exact_matches else partial_matches

                        for elem in candidates:
                            try:
                                if elem.is_displayed() and elem.is_enabled():
                                    self.driver.execute_script(
                                        "arguments[0].scrollIntoView({block: 'center'});", elem
                                    )
                                    time.sleep(0.3)
                                    elem.click()
                                    clicked = True
                                    match_type = "精确匹配" if exact_matches else "模糊匹配"
                                    logger.info(f"  ✓ 通过文字点击成功 ({match_type}): {delete_button_text}")
                                    time.sleep(0.5)
                                    break
                            except Exception as inner_e:
                                logger.debug(f"    点击元素失败: {inner_e}")

                    except Exception as e:
                        logger.debug(f"在容器内查找失败: {e}")

                if not clicked:
                    logger.warning(f"  ✗ 无法点击删除按钮 '{delete_button_text}'")
                    logger.warning("  容器内元素信息：")
                    try:
                        # 输出容器内的所有元素用于调试
                        all_elems = container.find_elements(By.XPATH, ".//*")
                        logger.info(f"  容器内共有 {len(all_elems)} 个元素")
                        for i, elem in enumerate(all_elems[:10]):  # 只显示前10个
                            try:
                                tag = elem.tag_name
                                text = elem.text.strip()[:30] if elem.text else ""
                                logger.debug(f"    [{i+1}] <{tag}> text='{text}'")
                            except:
                                pass
                    except:
                        pass
                    self.screenshot(f'failed_delete_in_container_{count}')
                    continue

                # 点击确认按钮（在整个页面查找，不在容器内）
                # 确认按钮通常在弹出的对话框中，对话框可能在容器外部
                if confirm_button_xpath or confirm_button_text:
                    if confirm_button_xpath:
                        logger.info(f"  通过 XPath 点击确认按钮: {confirm_button_xpath}")
                    else:
                        logger.info(f"  点击确认按钮 '{confirm_button_text}'...")

                    self.wait(2.5)  # 增加等待时间，让确认对话框完全显示

                    # 尝试多种方式点击确认按钮
                    confirm_clicked = False

                    # 方式0: 直接使用 XPath（最优先，最精准）
                    if confirm_button_xpath and not confirm_clicked:
                        try:
                            element = self.driver.find_element(By.XPATH, confirm_button_xpath)
                            if element:
                                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                                time.sleep(0.3)
                                element.click()
                                confirm_clicked = True
                                logger.info(f"  ✓ 确认按钮点击成功（直接XPath）")
                        except Exception as e:
                            logger.debug(f"  直接XPath点击失败: {e}")

                    # 方式1: 精确文字匹配（如果没有提供 XPath 或 XPath 失败）
                    if not confirm_clicked and confirm_button_text:
                        try:
                            element = self.find_element_by_text(confirm_button_text, exact_match=True, timeout=5)
                            if element:
                                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                                time.sleep(0.3)
                                element.click()
                                confirm_clicked = True
                                logger.info(f"  ✓ 确认按钮点击成功（精确匹配）")
                        except Exception as e:
                            logger.debug(f"  精确匹配失败: {e}")

                    # 方式2: JavaScript 点击（只在使用文字匹配时）
                    if not confirm_clicked and confirm_button_text:
                        try:
                            xpaths = [
                                f"//button[normalize-space(text())='{confirm_button_text}']",
                                f"//a[normalize-space(text())='{confirm_button_text}']",
                                f"//div[normalize-space(text())='{confirm_button_text}']",
                                f"//span[normalize-space(text())='{confirm_button_text}']",
                                f"//*[normalize-space(text())='{confirm_button_text}']",
                                f"//button[contains(text(), '{confirm_button_text}')]",
                                f"//a[contains(text(), '{confirm_button_text}')]",
                                f"//div[contains(text(), '{confirm_button_text}')]",
                                f"//span[contains(text(), '{confirm_button_text}')]",
                                f"//*[contains(text(), '{confirm_button_text}')]",
                            ]
                            for xpath in xpaths:
                                elements = self.driver.find_elements(By.XPATH, xpath)
                                logger.debug(f"  XPath '{xpath}' 找到 {len(elements)} 个元素")
                                for elem in elements:
                                    try:
                                        if elem.is_displayed() and elem.is_enabled():
                                            self.driver.execute_script("arguments[0].click();", elem)
                                            confirm_clicked = True
                                            logger.info(f"  ✓ 确认按钮点击成功 (XPath: {xpath})")
                                            time.sleep(0.5)
                                            break
                                    except Exception as inner_e:
                                        logger.debug(f"    点击确认按钮失败: {inner_e}")
                                if confirm_clicked:
                                    break
                        except Exception as e:
                            logger.debug(f"  JavaScript点击确认按钮失败: {e}")

                    # 方式3: 使用 ActionChains
                    if not confirm_clicked:
                        try:
                            elements = self.find_all_by_text(confirm_button_text, exact_match=False, timeout=2)
                            logger.debug(f"  通过文字查找找到 {len(elements)} 个元素")
                            for elem in elements:
                                try:
                                    if elem.is_displayed() and elem.is_enabled():
                                        actions = ActionChains(self.driver)
                                        actions.move_to_element(elem).click().perform()
                                        confirm_clicked = True
                                        logger.info(f"  ✓ ActionChains点击成功")
                                        time.sleep(0.5)
                                        break
                                except Exception as inner_e:
                                    logger.debug(f"    ActionChains点击失败: {inner_e}")
                        except Exception as e:
                            logger.debug(f"  ActionChains点击失败: {e}")

                    # 如果还是失败，输出所有包含该文字的元素信息
                    if not confirm_clicked:
                        logger.warning(f"  ✗ 无法点击确认按钮 '{confirm_button_text}'")
                        logger.warning("  尝试查找所有包含该文字的元素...")
                        try:
                            all_elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{confirm_button_text}')]")
                            logger.info(f"  找到 {len(all_elements)} 个包含 '{confirm_button_text}' 的元素")
                            for i, elem in enumerate(all_elements):
                                try:
                                    tag = elem.tag_name
                                    text = elem.text[:50] if elem.text else ""
                                    visible = elem.is_displayed()
                                    enabled = elem.is_enabled()
                                    logger.info(f"    [{i+1}] <{tag}> text='{text}' visible={visible} enabled={enabled}")
                                except:
                                    pass
                        except Exception as e:
                            logger.debug(f"  查找元素失败: {e}")

                        self.screenshot(f'failed_click_confirm_{count}')

                # 等待删除操作完成
                self.wait(1.5)

                logger.info(f"✓ 第 {count} 次删除完成")

            except Exception as e:
                logger.error(f"删除过程出错: {e}")
                break

        # 检查结束原因
        if not self.exists_xpath(container_xpath):
            logger.info(f"[OK] 容器内所有项目已删除，共删除 {count} 项")
        else:
            logger.warning(f"达到最大循环次数 {max_iterations}，可能还有剩余项")

        return count

    # ========================================================================
    # 其他操作
    # ========================================================================

    def close(self):
        """关闭浏览器"""
        self.browser.close()
        logger.info("浏览器已关闭")

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.close()


# FamilyReset 工具类 - 用于在其他脚本中导入使用
# 示例: from familyreset import FamilyReset
