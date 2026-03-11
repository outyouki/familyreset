"""
FamilyReset - ブラウザ自動化ツールクラス

テキストで要素を認識して操作を実行、XPathの手動検索が不要

基本例:
    fr = FamilyReset()
    fr.open('https://example.com') \\
      .click_text('ログイン')           \\  # 「ログイン」文字を含む要素をクリック
      .input_text('ユーザー名', 'admin') \\  # 「ユーザー名」関連の入力欄に入力
      .input_text('パスワード', '123456')  \\  # 「パスワード」関連の入力欄に入力
      .click_text('送信')            \\  # 送信ボタンをクリック
      .wait(3)                       \\  # 3秒待機
      .screenshot()                      # スクリーンショット

高度な機能:
    # 要素操作
    fr.double_click_text('ファイル')       # ダブルクリック
    fr.hover_text('メニュー')               # マウスホバー
    fr.right_click_text('オブジェクト')         # 右クリック

    # 入力操作
    fr.input_and_enter('検索', 'キーワード')  # 入力後エンター
    fr.clear_input('ユーザー名')              # 入力欄をクリア
    fr.check_element('利用規約に同意する')          # チェックボックスをオン

    # スクロール操作
    fr.scroll(500)                       # 下に500ピクセルスクロール
    fr.scroll_to_text('下部')            # 指定テキストまでスクロール
    fr.scroll_to_top()                   # トップへスクロール
    fr.scroll_to_bottom()                # ボトムへスクロール

    # ページ操作
    fr.back()                            # 戻る
    fr.forward()                         # 進む
    fr.refresh()                         # 更新
    url = fr.get_url()                   # 現在のURLを取得
    title = fr.get_title()               # ページタイトルを取得

    # 要素情報
    text = fr.get_text('タイトル')           # 要素テキストを取得
    href = fr.get_attr('リンク', 'href')   # 要素属性を取得
    exists = fr.exists('ボタン')           # 要素が存在するか確認

    # 待機操作
    fr.wait_for_text('読み込み完了', timeout=30)  # テキスト出現を待機
    fr.wait(5)                               # 5秒待機

    # JavaScript
    fr.execute_js('alert("Hello")')     # JavaScriptコードを実行
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

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FamilyReset:
    """
    FamilyReset ブラウザ自動化ツールクラス

    テキストで自動的に要素を認識して操作を実行
    """

    def __init__(self, browser_type: str = 'chrome', headless: bool = False):
        """
        初期化

        Args:
            browser_type: ブラウザタイプ ('chrome', 'firefox', 'edge')
            headless: ヘッドレスモードかどうか
        """
        self.browser = BrowserController(
            browser_type=browser_type,
            headless=headless
        )
        self.driver = self.browser.driver
        logger.info(f"FamilyReset 初期化完了 (ブラウザ: {browser_type})")

    # ========================================================================
    # 基本操作
    # ========================================================================

    def open(self, url: str) -> 'FamilyReset':
        """
        URLを開く

        Args:
            url: 目標URL

        Returns:
            self、チェーン呼び出しをサポート
        """
        logger.info(f"URLを開く: {url}")
        self.browser.open(url)
        return self

    def wait(self, seconds: float) -> 'FamilyReset':
        """
        指定時間待機

        Args:
            seconds: 待機秒数

        Returns:
            self、チェーン呼び出しをサポート
        """
        logger.info(f"{seconds} 秒待機")
        time.sleep(seconds)
        return self

    def screenshot(self, filename: str = None) -> 'FamilyReset':
        """
        スクリーンショット

        Args:
            filename: ファイル名

        Returns:
            self、チェーン呼び出しをサポート
        """
        path = self.browser.screenshot(filename)
        logger.info(f"スクリーンショット保存: {path}")
        return self

    # ========================================================================
    # テキストで要素を操作
    # ========================================================================

    def find_element_by_text(self, text: str, exact_match: bool = True,
                             timeout: int = 10) -> Optional[Any]:
        """
        テキストで要素を検索

        Args:
            text: 検索するテキスト
            exact_match: 完全一致かどうか（True=完全一致、False=部分一致）
            timeout: タイムアウト時間（秒）

        Returns:
            見つかった要素、見つからない場合は None
        """
        logger.info(f"テキスト検索: '{text}' (完全一致: {exact_match})")

        # 複数のXPath式を試行
        if exact_match:
            xpaths = [
                f"//*[normalize-space(text())='{text}']",  # 完全一致（空白を無視）
                f"//*[text()='{text}']",  # 完全完全一致
                f"//input[@value='{text}']",  # ボタンのvalue属性
                f"//button[normalize-space(text())='{text}']",  # ボタン完全一致
            ]
        else:
            xpaths = [
                f"//*[contains(text(), '{text}')]",  # テキストを含む
                f"//*[contains(normalize-space(text()), '{text}')]",  # テキストを含む（空白を無視）
                f"//input[contains(@value, '{text}')]",  # ボタンのvalue
                f"//button[contains(text(), '{text}')]",  # ボタンを含む
            ]

        # 各XPathを試行
        for xpath in xpaths:
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                logger.info(f"✓ 要素が見つかりました: {element.tag_name}")
                return element
            except TimeoutException:
                continue

        logger.warning(f"✗ '{text}' を含む要素が見つかりませんでした")
        return None

    def click_text(self, text: str, exact_match: bool = True,
                   wait_after: float = 0, timeout: int = 10) -> 'FamilyReset':
        """
        指定テキストを含む要素を検索してクリック

        Args:
            text: クリックするテキスト
            exact_match: 完全一致かどうか
            wait_after: クリック後の待機秒数
            timeout: 検索タイムアウト時間

        Returns:
            self、チェーン呼び出しをサポート
        """
        element = self.find_element_by_text(text, exact_match, timeout)

        if element is None:
            logger.error(f"クリックできません: '{text}' が見つかりません")
            return self

        # 要素にスクロール
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", element
        )
        time.sleep(0.3)

        # 複数のクリック方法を試行
        clicked = False

        # 方法1: 標準クリック
        try:
            element.click()
            clicked = True
            logger.info(f"✓ クリックしました: '{text}' (標準クリック)")
        except Exception as e:
            logger.debug(f"標準クリック失敗: {e}")

        # 方法2: JavaScriptクリック
        if not clicked:
            try:
                self.driver.execute_script("arguments[0].click();", element)
                clicked = True
                logger.info(f"✓ クリックしました: '{text}' (JavaScript)")
            except Exception as e:
                logger.debug(f"JavaScriptクリック失敗: {e}")

        # 方法3: ActionChains
        if not clicked:
            try:
                actions = ActionChains(self.driver)
                actions.move_to_element(element).click().perform()
                clicked = True
                logger.info(f"✓ クリックしました: '{text}' (ActionChains)")
            except Exception as e:
                logger.debug(f"ActionChainsクリック失敗: {e}")

        if wait_after > 0:
            time.sleep(wait_after)

        return self

    def click_text_and_save_url(self, text: str, url_file: str = 'clicked_urls.txt',
                                exact_match: bool = True, wait_after: float = 0) -> str:
        """
        テキストをクリックしてクリック後のURLを記録

        Args:
            text: クリックするテキスト
            url_file: URL保存ファイルパス
            exact_match: 完全一致かどうか
            wait_after: クリック後の待機秒数

        Returns:
            クリック後のURL
        """
        # まずクリック
        self.click_text(text, exact_match=exact_match, wait_after=wait_after)

        # ページ読み込みを待機
        self.wait(1)

        # 現在のURLを取得
        current_url = self.get_url()

        # ファイルに保存
        try:
            with open(url_file, 'a', encoding='utf-8') as f:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] クリック '{text}' -> {current_url}\n")
            logger.info(f"✓ URL保存完了: {current_url}")
        except Exception as e:
            logger.error(f"URL保存失敗: {e}")

        return current_url

    def load_urls(self, url_file: str = 'clicked_urls.txt') -> list:
        """
        ファイルから保存されたURL記録をすべて読み込み

        Args:
            url_file: URLファイルパス

        Returns:
            URL記録リスト、各項目の形式: {'timestamp': str, 'text': str, 'url': str}
        """
        urls = []
        try:
            with open(url_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        # 形式を解析: [2026-01-28 10:30:15] クリック '10d' -> https://example.com
                        import re
                        match = re.match(r'\[([^\]]+)\] クリック \'([^\']+)\' -> (.+)', line)
                        if match:
                            urls.append({
                                'timestamp': match.group(1),
                                'text': match.group(2),
                                'url': match.group(3)
                            })
            logger.info(f"✓ {len(urls)} 件のURL記録を読み込みました")
        except FileNotFoundError:
            logger.warning(f"URLファイルが存在しません: {url_file}")
        except Exception as e:
            logger.error(f"URL読み込み失敗: {e}")
        return urls

    def get_latest_url(self, text: str = None, url_file: str = 'clicked_urls.txt') -> str:
        """
        指定テキストに対応する最新のURLを取得

        Args:
            text: クリックしたテキスト（Noneの場合は最後の記録を取得）
            url_file: URLファイルパス

        Returns:
            URL文字列、見つからない場合はNone
        """
        urls = self.load_urls(url_file)
        if not urls:
            return None

        if text:
            # 指定テキストの最新URLを検索
            for record in reversed(urls):
                if text in record['text'] or record['text'] == text:
                    logger.info(f"'{text}' の最新URLが見つかりました: {record['url']}")
                    return record['url']
            logger.warning(f"'{text}' のURL記録が見つかりませんでした")
            return None
        else:
            # 最後の記録を返す
            latest = urls[-1]
            logger.info(f"最新URL: {latest['url']} (クリックテキスト: '{latest['text']}')")
            return latest['url']

    def get_all_urls(self, url_file: str = 'clicked_urls.txt') -> list:
        """
        保存されたすべてのURL記録を取得

        Args:
            url_file: URLファイルパス

        Returns:
            URL記録リスト
        """
        return self.load_urls(url_file)

    def filter_urls_by_text(self, text: str, url_file: str = 'clicked_urls.txt') -> list:
        """
        テキストでURL記録をフィルタリング

        Args:
            text: 一致するテキスト（あいまい一致をサポート）
            url_file: URLファイルパス

        Returns:
            一致したURL記録リスト
        """
        urls = self.load_urls(url_file)
        filtered = []
        for record in urls:
            if text in record['text'] or record['text'] == text:
                filtered.append(record)
        logger.info(f"'{text}' を含む {len(filtered)} 件のURL記録が見つかりました")
        return filtered

    def open_saved_url(self, text: str = None, url_file: str = 'clicked_urls.txt') -> 'FamilyReset':
        """
        保存されたURLを開く

        Args:
            text: クリックしたテキスト（Noneの場合は最後の記録のURLを開く）
            url_file: URLファイルパス

        Returns:
            self、チェーン呼び出しをサポート
        """
        url = self.get_latest_url(text, url_file)
        if url:
            logger.info(f"保存されたURLを開く: {url}")
            self.open(url)
        else:
            logger.error(f"開くURLが見つかりません")
        return self

    def input_text(self, label_text: str, value: str,
                   exact_match: bool = True, find_input: bool = True,
                   timeout: int = 10) -> 'FamilyReset':
        """
        ラベルテキストで関連する入力欄を探してテキストを入力

        Args:
            label_text: ラベルテキスト（「ユーザー名」「パスワード」など）
            value: 入力する値
            exact_match: ラベルの完全一致かどうか
            find_input: 関連する入力欄を探すかどうか（Falseの場合は見つかった要素に直接入力）
            timeout: タイムアウト時間

        Returns:
            self、チェーン呼び出しをサポート
        """
        logger.info(f"テキスト入力: ラベル='{label_text}', 値='{value}'")

        # ラベル要素を検索
        label = self.find_element_by_text(label_text, exact_match, timeout)

        if label is None:
            logger.error(f"入力できません: ラベル '{label_text}' が見つかりません")
            return self

        # 関連する入力欄を検索
        input_element = None

        if find_input:
            # 方法1: labelのfor属性
            try:
                label_for = label.get_attribute('for')
                if label_for:
                    input_element = self.driver.find_element(By.ID, label_for)
                    logger.info(f"  for属性で入力欄が見つかりました")
            except:
                pass

            # 方法2: 同じ階層または親の入力欄を検索
            if input_element is None:
                try:
                    # 親要素を検索
                    parent = label.find_element(By.XPATH, '..')

                    # 親要素内で入力欄を検索
                    inputs = parent.find_elements(By.TAG_NAME, 'input')

                    # type=textまたはtype=passwordを優先
                    for inp in inputs:
                        inp_type = inp.get_attribute('type') or 'text'
                        if inp_type in ['text', 'password', 'email', 'search']:
                            input_element = inp
                            logger.info(f"  同じ階層の要素で入力欄が見つかりました (type={inp_type})")
                            break

                    # 見つからない場合、最初の入力欄を使用
                    if input_element is None and inputs:
                        input_element = inputs[0]
                        logger.info(f"  同じ階層の要素で入力欄が見つかりました")
                except:
                    pass

            # 方法3: 隣接する入力欄を検索
            if input_element is None:
                try:
                    following = label.find_elements(By.XPATH, './following::input[1]')
                    if following:
                        input_element = following[0]
                        logger.info(f"  後続の要素で入力欄が見つかりました")
                except:
                    pass

        # 見つかったラベル自体が入力欄である場合（例：button value="ログイン"）
        if input_element is None and label.tag_name == 'input':
            input_element = label
            logger.info(f"  ラベル自体が入力欄です")

        if input_element is None:
            logger.error(f"入力できません: '{label_text}' に関連する入力欄が見つかりません")
            return self

        # テキストを入力
        try:
            input_element.clear()
            input_element.send_keys(value)
            logger.info(f"✓ 入力完了: '{value}'")
        except Exception as e:
            logger.error(f"入力失敗: {e}")

        return self

    def select_option(self, select_text: str, option_text: str,
                      exact_match: bool = True, timeout: int = 10) -> 'FamilyReset':
        """
        ドロップダウンボックスのラベルで選択肢を選択

        Args:
            select_text: ドロップダウンボックスのラベルテキスト
            option_text: 選択する選択肢のテキスト
            exact_match: ラベルの完全一致かどうか
            timeout: タイムアウト時間

        Returns:
            self、チェーン呼び出しをサポート
        """
        logger.info(f"ドロップダウン選択: ラベル='{select_text}', 選択肢='{option_text}'")

        # select要素を検索（input_textのロジックを使用）
        label = self.find_element_by_text(select_text, exact_match, timeout)

        if label is None:
            logger.error(f"ラベル '{select_text}' が見つかりませんでした")
            return self

        # 関連するselect要素を検索
        select_element = None

        try:
            # for属性
            label_for = label.get_attribute('for')
            if label_for:
                select_element = self.driver.find_element(By.ID, label_for)
        except:
            pass

        if select_element is None:
            try:
                # 同じ階層を検索
                parent = label.find_element(By.XPATH, '..')
                selects = parent.find_elements(By.TAG_NAME, 'select')
                if selects:
                    select_element = selects[0]
            except:
                pass

        if select_element is None:
            logger.error(f"'{select_text}' に関連するドロップダウンが見つかりませんでした")
            return self

        # 選択肢を選択
        try:
            from selenium.webdriver.support.ui import Select
            select = Select(select_element)
            select.select_by_visible_text(option_text)
            logger.info(f"✓ 選択完了: '{option_text}'")
        except Exception as e:
            logger.error(f"選択失敗: {e}")

        return self

    # ========================================================================
    # リスト操作
    # ========================================================================

    def find_all_by_text(self, text: str, exact_match: bool = True,
                         timeout: int = 10) -> List[Any]:
        """
        指定テキストを含むすべての要素を検索

        Args:
            text: 検索するテキスト
            exact_match: 完全一致かどうか
            timeout: タイムアウト時間

        Returns:
            要素リスト
        """
        logger.info(f"'{text}' を含むすべての要素を検索")

        # 複数のXPath式を構築
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

        # 各XPathを試行
        for xpath in xpaths:
            try:
                elements = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_all_elements_located((By.XPATH, xpath))
                )
                if elements:
                    logger.info(f"✓ {len(elements)} 個の要素が見つかりました")
                    return elements
            except TimeoutException:
                continue

        logger.warning(f"✗ '{text}' を含む要素が見つかりませんでした")
        return []

    def get_list_items(self, list_selector: str = None,
                       timeout: int = 10) -> List[dict]:
        """
        リスト項目を取得（一般的なリスト構造を自動認識）

        Args:
            list_selector: オプションのリストコンテナセレクター（XPath）
            timeout: タイムアウト時間

        Returns:
            リスト項目辞書リスト: [{'index': 0, 'text': '内容', 'element': element}, ...]
        """
        logger.info("リスト項目を取得")

        items = []

        try:
            # 複数のリスト構造を試行
            list_types = []

            # セレクターが提供された場合
            if list_selector:
                list_types.append(('custom', (By.XPATH, list_selector)))

            # 一般的なリスト構造
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
                        # テーブルは特別処理
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
                        # カスタムセレクター
                        elements = self.driver.find_elements(*locator)
                        for idx, elem in enumerate(elements):
                            text = elem.text.strip()
                            if text:
                                items.append({
                                    'index': idx,
                                    'text': text,
                                    'element': elem
                                })
                        break  # カスタムセレクターを優先
                    else:
                        # ul, ol, divなど
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
                        logger.info(f"✓ {list_type} で {len(items)} 個のリスト項目が見つかりました")
                        break

                except Exception as e:
                    logger.debug(f"{list_type} の試行失敗: {e}")
                    continue

            if not items:
                logger.warning("リスト項目が見つかりませんでした")

        except Exception as e:
            logger.error(f"リスト項目の取得失敗: {e}")

        return items

    def get_text_list(self, xpath: str = None) -> List[str]:
        """
        ページ上のすべてのテキスト内容または指定要素のテキストを取得

        Args:
            xpath: オプションのXPath式、Noneの場合はページ全体のテキストを取得

        Returns:
            テキストリスト
        """
        logger.info("テキストリストを取得")

        try:
            if xpath:
                elements = self.driver.find_elements(By.XPATH, xpath)
                texts = [elem.text.strip() for elem in elements if elem.text.strip()]
            else:
                # ページのすべての可視テキストを取得
                texts = self.driver.find_elements(By.XPATH, '//*[text()]')
                texts = [t.strip() for t in [elem.text for elem in texts] if t.strip()]

            logger.info(f"✓ {len(texts)} 個のテキストを取得しました")
            return texts

        except Exception as e:
            logger.error(f"テキストリストの取得失敗: {e}")
            return []

    def click_list_item(self, index: int, list_selector: str = None,
                        wait_after: float = 0) -> 'FamilyReset':
        """
        リストのN番目の項目をクリック

        Args:
            index: リストインデックス（0から開始）
            list_selector: オプションのリストセレクター
            wait_after: クリック後の待機秒数

        Returns:
            self、チェーン呼び出しをサポート
        """
        logger.info(f"リストの {index} 番目の項目をクリック")

        items = self.get_list_items(list_selector)

        if index < 0 or index >= len(items):
            logger.error(f"インデックスが範囲外です: 0-{len(items)-1}")
            return self

        try:
            element = items[index]['element']
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", element
            )
            time.sleep(0.3)
            element.click()
            logger.info(f"✓ クリックしました: {items[index]['text']}")

            if wait_after > 0:
                time.sleep(wait_after)

        except Exception as e:
            logger.error(f"リスト項目のクリック失敗: {e}")

        return self

    def select_and_click_list(self, list_selector: str = None,
                              prompt: str = "操作する項目を選択してください") -> 'FamilyReset':
        """
        リストを表示してユーザーに選択させ、選択した項目をクリック

        Args:
            list_selector: オプションのリストセレクター
            prompt: プロンプトテキスト

        Returns:
            self、チェーン呼び出しをサポート
        """
        items = self.get_list_items(list_selector)

        if not items:
            logger.error("選択可能なリスト項目がありません")
            return self

        print("\n" + "="*70)
        print(prompt)
        print("="*70)

        for item in items:
            print(f"  [{item['index']}] {item['text']}")

        print("="*70)

        try:
            choice = input(f"\n選択肢を入力してください (0-{len(items)-1}): ").strip()

            if not choice.isdigit():
                logger.error("無効な入力です")
                return self

            index = int(choice)

            if index < 0 or index >= len(items):
                logger.error(f"インデックスが範囲外です: 0-{len(items)-1}")
                return self

            # 選択した項目をクリック
            try:
                element = items[index]['element']
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", element
                )
                time.sleep(0.3)
                element.click()
                logger.info(f"✓ クリックしました: {items[index]['text']}")
            except Exception as e:
                logger.error(f"クリック失敗: {e}")

        except KeyboardInterrupt:
            logger.info("ユーザーが選択をキャンセルしました")

        return self

    def click_text_match(self, pattern: str, exact_match: bool = False,
                         timeout: int = 10, wait_after: float = 0) -> 'FamilyReset':
        """
        一致パターンを含むテキスト要素を検索してクリック

        Args:
            pattern: 一致パターン（部分一致をサポート）
            exact_match: 完全一致かどうか
            timeout: タイムアウト時間
            wait_after: クリック後の待機秒数

        Returns:
            self、チェーン呼び出しをサポート
        """
        logger.info(f"'{pattern}' に一致する要素を検索してクリック")

        elements = self.find_all_by_text(pattern, exact_match, timeout)

        if not elements:
            logger.error(f"'{pattern}' に一致する要素が見つかりませんでした")
            return self

        # 最初に一致した要素をクリック
        element = elements[0]
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", element
        )
        time.sleep(0.3)
        element.click()
        logger.info(f"✓ クリックしました: {element.text[:50]}")

        if wait_after > 0:
            time.sleep(wait_after)

        return self

    # ========================================================================
    # 要素情報の取得
    # ========================================================================

    def get_text(self, text: str, exact_match: bool = True,
                 timeout: int = 10) -> Optional[str]:
        """
        指定テキストを含む要素のテキスト内容を取得

        Args:
            text: 検索するテキスト
            exact_match: 完全一致かどうか
            timeout: タイムアウト時間

        Returns:
            要素のテキスト内容、見つからない場合はNone
        """
        element = self.find_element_by_text(text, exact_match, timeout)
        if element:
            text_content = element.text
            logger.info(f"テキスト取得: '{text_content}'")
            return text_content
        return None

    def get_attr(self, text: str, attr_name: str,
                 exact_match: bool = True, timeout: int = 10) -> Optional[str]:
        """
        指定テキストを含む要素の属性値を取得

        Args:
            text: 検索するテキスト
            attr_name: 属性名（'href', 'id', 'class' など）
            exact_match: 完全一致かどうか
            timeout: タイムアウト時間

        Returns:
            属性値、見つからない場合はNone
        """
        element = self.find_element_by_text(text, exact_match, timeout)
        if element:
            attr_value = element.get_attribute(attr_name)
            logger.info(f"属性取得 {attr_name}: '{attr_value}'")
            return attr_value
        return None

    def exists(self, text: str, exact_match: bool = True,
               timeout: int = 5) -> bool:
        """
        指定テキストを含む要素が存在するか確認

        Args:
            text: 検索するテキスト
            exact_match: 完全一致かどうか
            timeout: タイムアウト時間

        Returns:
            Trueは存在、Falseは不存在
        """
        element = self.find_element_by_text(text, exact_match, timeout)
        exists = element is not None
        logger.info(f"要素 '{text}' は{'存在します' if exists else '存在しません'}")
        return exists

    def exists_xpath(self, xpath: str, timeout: int = 2) -> bool:
        """
        XPath要素が存在するか確認

        Args:
            xpath: XPath式
            timeout: タイムアウト時間（秒）

        Returns:
            Trueは存在、Falseは不存在
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
        指定テキストを含む要素が出現するのを待機

        Args:
            text: 待機するテキスト
            exact_match: 完全一致かどうか
            timeout: 最長待機時間

        Returns:
            Trueは要素出現、Falseはタイムアウト
        """
        logger.info(f"テキスト出現を待機: '{text}' (最長 {timeout} 秒)")
        element = self.find_element_by_text(text, exact_match, timeout)
        return element is not None

    # ========================================================================
    # クリック操作（拡張）
    # ========================================================================

    def click_xpath(self, xpath: str, index: int = 0,
                    wait_after: float = 0) -> 'FamilyReset':
        """
        XPathで要素をクリック

        Args:
            xpath: XPath式
            index: 要素インデックス（複数一致がある場合）
            wait_after: クリック後の待機秒数

        Returns:
            self、チェーン呼び出しをサポート
        """
        logger.info(f"XPathでクリック: {xpath} (インデックス: {index})")

        try:
            elements = self.driver.find_elements(By.XPATH, xpath)

            if not elements:
                logger.error(f"XPath要素が見つかりません: {xpath}")
                return self

            if len(elements) <= index:
                logger.error(f"インデックスが範囲外です: {len(elements)} 個の要素が見つかりました、要求インデックス {index}")
                return self

            element = elements[index]
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", element
            )
            time.sleep(0.3)
            element.click()
            logger.info(f"✓ {index + 1} 番目の要素をクリックしました")

            if wait_after > 0:
                time.sleep(wait_after)

        except Exception as e:
            logger.error(f"XPathクリック失敗: {e}")

        return self

    def double_click_text(self, text: str, exact_match: bool = True,
                          wait_after: float = 0) -> 'FamilyReset':
        """
        指定テキストを含む要素をダブルクリック

        Args:
            text: ダブルクリックするテキスト
            exact_match: 完全一致かどうか
            wait_after: ダブルクリック後の待機秒数

        Returns:
            self、チェーン呼び出しをサポート
        """
        logger.info(f"ダブルクリック: '{text}'")

        element = self.find_element_by_text(text, exact_match)

        if element:
            try:
                actions = ActionChains(self.driver)
                actions.double_click(element).perform()
                logger.info(f"✓ ダブルクリックしました: '{text}'")

                if wait_after > 0:
                    time.sleep(wait_after)
            except Exception as e:
                logger.error(f"ダブルクリック失敗: {e}")

        return self

    def hover_text(self, text: str, exact_match: bool = True,
                   wait_after: float = 0) -> 'FamilyReset':
        """
        指定テキストを含む要素にマウスをホバー

        Args:
            text: 対象テキスト
            exact_match: 完全一致かどうか
            wait_after: ホバー後の待機秒数

        Returns:
            self、チェーン呼び出しをサポート
        """
        logger.info(f"マウスホバー: '{text}'")

        element = self.find_element_by_text(text, exact_match)

        if element:
            try:
                actions = ActionChains(self.driver)
                actions.move_to_element(element).perform()
                logger.info(f"✓ ホバーしました: '{text}'")

                if wait_after > 0:
                    time.sleep(wait_after)
            except Exception as e:
                logger.error(f"ホバー失敗: {e}")

        return self

    # ========================================================================
    # 入力操作（拡張）
    # ========================================================================

    def input_and_enter(self, label_text: str, value: str,
                        exact_match: bool = True) -> 'FamilyReset':
        """
        入力欄にテキストを入力してエンターキーを押す

        Args:
            label_text: ラベルテキスト
            value: 入力する値
            exact_match: ラベルの完全一致かどうか

        Returns:
            self、チェーン呼び出しをサポート
        """
        logger.info(f"入力してエンター: ラベル='{label_text}', 値='{value}'")

        # ラベル要素を検索
        label = self.find_element_by_text(label_text, exact_match)

        if label is None:
            logger.error(f"ラベル '{label_text}' が見つかりませんでした")
            return self

        # 関連する入力欄を検索
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
            logger.error(f"'{label_text}' に関連する入力欄が見つかりませんでした")
            return self

        # 入力してエンター
        try:
            from selenium.webdriver.common.keys import Keys
            input_element.clear()
            input_element.send_keys(value)
            input_element.send_keys(Keys.RETURN)
            logger.info(f"✓ 入力してエンターしました: '{value}'")
            time.sleep(1)  # 送信を待機
        except Exception as e:
            logger.error(f"入力してエンター失敗: {e}")

        return self

    def clear_input(self, label_text: str,
                    exact_match: bool = True) -> 'FamilyReset':
        """
        入力欄をクリア

        Args:
            label_text: ラベルテキスト
            exact_match: 完全一致かどうか

        Returns:
            self、チェーン呼び出しをサポート
        """
        logger.info(f"入力欄をクリア: '{label_text}'")

        label = self.find_element_by_text(label_text, exact_match)

        if label:
            try:
                parent = label.find_element(By.XPATH, '..')
                inputs = parent.find_elements(By.TAG_NAME, 'input')

                if inputs:
                    inputs[0].clear()
                    logger.info(f"✓ クリアしました: '{label_text}'")
            except Exception as e:
                logger.error(f"クリア失敗: {e}")

        return self

    # ========================================================================
    # チェックボックス/ラジオボタン操作
    # ========================================================================

    def check_element(self, label_text: str, check: bool = True,
                      exact_match: bool = True) -> 'FamilyReset':
        """
        チェックボックス/ラジオボタンをオン/オフ

        Args:
            label_text: ラベルテキスト
            check: Trueはオン、Falseはオフ
            exact_match: 完全一致かどうか

        Returns:
            self、チェーン呼び出しをサポート
        """
        action = "オン" if check else "オフ"
        logger.info(f"{action}: '{label_text}'")

        label = self.find_element_by_text(label_text, exact_match)

        if not label:
            logger.error(f"ラベルが見つかりません: '{label_text}'")
            return self

        input_element = None

        # 方法1: label自体がinputかチェック
        if label.tag_name == 'input':
            inp_type = label.get_attribute('type')
            if inp_type in ['checkbox', 'radio']:
                input_element = label
                logger.debug("  ラベル自体がinputです")

        # 方法2: labelのfor属性で検索
        if input_element is None:
            try:
                label_for = label.get_attribute('for')
                if label_for:
                    input_element = self.driver.find_element(By.ID, label_for)
                    logger.debug(f"  for属性で見つかりました: #{label_for}")
            except:
                pass

        # 方法3: 親要素内で検索
        if input_element is None:
            try:
                parent = label.find_element(By.XPATH, '..')
                inputs = parent.find_elements(By.TAG_NAME, 'input')
                for inp in inputs:
                    inp_type = inp.get_attribute('type')
                    if inp_type in ['checkbox', 'radio']:
                        input_element = inp
                        logger.debug("  親要素内でinputが見つかりました")
                        break
            except:
                pass

        # 方法4: 前の要素で検索（前のinput）
        if input_element is None:
            try:
                preceding = label.find_elements(By.XPATH, './preceding::input[1]')
                for inp in preceding:
                    inp_type = inp.get_attribute('type')
                    if inp_type in ['checkbox', 'radio']:
                        input_element = inp
                        logger.debug("  前の要素でinputが見つかりました")
                        break
            except:
                pass

        # 方法5: 後の要素で検索（後のinput）
        if input_element is None:
            try:
                following = label.find_elements(By.XPATH, './following::input[1]')
                for inp in following:
                    inp_type = inp.get_attribute('type')
                    if inp_type in ['checkbox', 'radio']:
                        input_element = inp
                        logger.debug("  後の要素でinputが見つかりました")
                        break
            except:
                pass

        # オン/オフを実行
        if input_element:
            try:
                is_selected = input_element.is_selected()

                # 要素にスクロール
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", input_element
                )
                time.sleep(0.3)

                # クリックが必要か判断
                if check and not is_selected:
                    input_element.click()
                    logger.info(f"✓ オンにしました: '{label_text}'")
                elif not check and is_selected:
                    input_element.click()
                    logger.info(f"✓ オフにしました: '{label_text}'")
                else:
                    logger.info(f"  状態は正しいです、操作不要: '{label_text}'")

            except Exception as e:
                logger.error(f"{action}失敗: {e}")
                # JavaScriptクリックを試行
                try:
                    self.driver.execute_script("arguments[0].click();", input_element)
                    logger.info(f"✓ JavaScriptで{action}成功: '{label_text}'")
                except:
                    logger.error(f"JavaScriptクリックも失敗しました")
        else:
            logger.error(f"'{label_text}' に関連するチェックボックス/ラジオボタンが見つかりませんでした")

        return self

    # ========================================================================
    # スクロール操作
    # ========================================================================

    def scroll(self, amount: int = 500) -> 'FamilyReset':
        """
        ページをスクロール

        Args:
            amount: スクロールピクセル（正数は下、負数は上）

        Returns:
            self、チェーン呼び出しをサポート
        """
        self.driver.execute_script(f"window.scrollBy(0, {amount});")
        logger.info(f"ページスクロール: {amount}px")
        return self

    def scroll_to_text(self, text: str, exact_match: bool = True,
                       timeout: int = 10) -> 'FamilyReset':
        """
        指定テキストを含む要素までスクロール

        Args:
            text: 対象テキスト
            exact_match: 完全一致かどうか
            timeout: タイムアウト時間

        Returns:
            self、チェーン呼び出しをサポート
        """
        logger.info(f"テキストまでスクロール: '{text}'")

        element = self.find_element_by_text(text, exact_match, timeout)

        if element:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", element
            )
            time.sleep(0.5)
            logger.info(f"✓ スクロールしました: '{text}'")

        return self

    def scroll_to_top(self) -> 'FamilyReset':
        """ページトップへスクロール"""
        self.driver.execute_script("window.scrollTo(0, 0);")
        logger.info("ページトップへスクロールしました")
        return self

    def scroll_to_bottom(self) -> 'FamilyReset':
        """ページボトムへスクロール"""
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        logger.info("ページボトムへスクロールしました")
        return self

    # ========================================================================
    # ページ操作
    # ========================================================================

    def back(self) -> 'FamilyReset':
        """戻る"""
        self.driver.back()
        logger.info("ページを戻りました")
        return self

    def forward(self) -> 'FamilyReset':
        """進む"""
        self.driver.forward()
        logger.info("ページを進みました")
        return self

    def refresh(self) -> 'FamilyReset':
        """ページ更新"""
        self.driver.refresh()
        logger.info("ページを更新しました")
        return self

    def get_url(self) -> str:
        """現在のURLを取得"""
        url = self.driver.current_url
        logger.info(f"現在のURL: {url}")
        return url

    def get_title(self) -> str:
        """ページタイトルを取得"""
        title = self.driver.title
        logger.info(f"ページタイトル: {title}")
        return title

    def get_page_source(self) -> str:
        """ページHTMLソースを取得"""
        return self.driver.page_source

    def execute_js(self, script: str, *args) -> Any:
        """
        JavaScriptコードを実行

        Args:
            script: JavaScriptコード
            *args: JavaScriptに渡すパラメータ

        Returns:
            実行結果
        """
        result = self.driver.execute_script(script, *args)
        logger.info(f"JavaScriptを実行しました")
        return result

    # ========================================================================
    # タブ操作
    # ========================================================================

    def switch_tab(self, index: int = -1) -> 'FamilyReset':
        """
        タブを切り替え

        Args:
            index: タブインデックス、-1は最新

        Returns:
            self、チェーン呼び出しをサポート
        """
        all_windows = self.driver.window_handles

        if not all_windows:
            logger.warning("開いているタブがありません")
            return self

        if index == -1:
            index = len(all_windows) - 1

        self.driver.switch_to.window(all_windows[index])
        logger.info(f"タブ {index + 1}/{len(all_windows)} に切り替えました")

        return self

    # ========================================================================
    # 高度な操作
    # ========================================================================

    def delete_all_settings(self, target_xpath: str = '//*[@id="__nuxt"]/section/div/a[1]',
                            delete_button_text: str = '設定を削除する',
                            confirm_button_text: str = '削除',
                            max_iterations: int = 100) -> int:
        """
        設定項目の一括削除

        目標要素が消えるまで以下の操作をループ実行：
        1. 目標XPath要素をクリック（デフォルトは最初のもの）
        2. 削除ボタンをクリック
        3. 削除を確認（ダイアログ内の確認ボタン）

        Args:
            target_xpath: 目標要素のXPath（デフォルト a[1]、削除後リスト更新）
            delete_button_text: 削除ボタンテキスト
            confirm_button_text: 確認ボタンテキスト
            max_iterations: 最大ループ回数（無限ループ防止）

        Returns:
            削除した項目数
        """
        logger.info("一括削除を開始します")
        count = 0

        while self.exists_xpath(target_xpath) and count < max_iterations:
            count += 1
            logger.info(f"--- {count} 回目の削除 ---")

            # 1. 目標要素をクリック
            logger.info("1. 設定項目をクリック...")
            self.click_xpath(target_xpath)
            self.wait(1)

            # 2. 削除ボタンをクリック
            logger.info(f"2. '{delete_button_text}' をクリック...")
            self.click_text(delete_button_text, exact_match=False)
            self.wait(2.5)  # ダイアログ完全表示のために待機時間を延長

            # 3. 確認ボタンをクリック（ダイアログ内）
            logger.info(f"3. ダイアログ内の '{confirm_button_text}' をクリック...")

            # 複数の方法で確認ボタンクリックを試行
            clicked = False

            # 方法1: テキストで検索してクリック（完全一致を優先）
            try:
                # まず完全一致で試行
                element = self.find_element_by_text(confirm_button_text, exact_match=True, timeout=3)
                if element:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                    time.sleep(0.3)
                    element.click()
                    clicked = True
                    logger.info(f"  ✓ 標準クリック成功（完全一致）")
            except Exception as e:
                logger.debug(f"  完全一致失敗: {e}")

            # 方法2: JavaScriptクリック（完全一致を優先）
            if not clicked:
                try:
                    xpaths = [
                        # 完全一致を優先
                        f"//button[normalize-space(text())='{confirm_button_text}']",
                        f"//a[normalize-space(text())='{confirm_button_text}']",
                        f"//div[normalize-space(text())='{confirm_button_text}']",
                        f"//span[normalize-space(text())='{confirm_button_text}']",
                        f"//*[normalize-space(text())='{confirm_button_text}']",
                        # 完全一致が見つからない場合、あいまい一致を使用
                        f"//button[contains(text(), '{confirm_button_text}')]",
                        f"//a[contains(text(), '{confirm_button_text}')]",
                        f"//div[contains(text(), '{confirm_button_text}')]",
                        f"//span[contains(text(), '{confirm_button_text}')]",
                        f"//*[contains(text(), '{confirm_button_text}')]",
                    ]
                    for xpath in xpaths:
                        elements = self.driver.find_elements(By.XPATH, xpath)
                        logger.debug(f"  XPath '{xpath}' で {len(elements)} 個の要素が見つかりました")
                        for elem in elements:
                            try:
                                if elem.is_displayed() and elem.is_enabled():
                                    self.driver.execute_script("arguments[0].click();", elem)
                                    clicked = True
                                    logger.info(f"  ✓ JavaScriptクリック成功 (XPath: {xpath})")
                                    time.sleep(0.5)  # クリック有効化の短い待機
                                    break
                            except Exception as inner_e:
                                logger.debug(f"    要素クリック失敗: {inner_e}")
                        if clicked:
                            break
                except Exception as e:
                    logger.debug(f"  JavaScriptクリック失敗: {e}")

            # 方法3: ActionChainsを使用
            if not clicked:
                try:
                    elements = self.find_all_by_text(confirm_button_text, exact_match=False, timeout=2)
                    for elem in elements:
                        if elem.is_displayed() and elem.is_enabled():
                            actions = ActionChains(self.driver)
                            actions.move_to_element(elem).click().perform()
                            clicked = True
                            logger.info(f"  ✓ ActionChainsクリック成功")
                            break
                except Exception as e:
                    logger.debug(f"  ActionChainsクリック失敗: {e}")

            if not clicked:
                logger.warning(f"  ✗ 確認ボタン '{confirm_button_text}' をクリックできませんでした")
                # デバッグ用にスクリーンショットを試行
                self.screenshot(f'failed_click_confirm_{count}')

            self.wait(2)  # 削除操作完了を待機

            # クリック失敗の場合、「削除」を含むすべての要素情報を取得
            if not clicked:
                logger.warning("'削除'を含むすべての要素を検索試行...")
                try:
                    all_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '削除')]")
                    logger.info(f"{len(all_elements)} 個の'削除'を含む要素が見つかりました")
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
                    logger.debug(f"要素検索失敗: {e}")

            logger.info(f"✓ {count} 回目の削除完了")

        # 終了理由を確認
        if not self.exists_xpath(target_xpath):
            logger.info(f"[OK] すべての設定を削除しました、合計 {count} 項目")
        else:
            logger.warning(f"最大ループ回数 {max_iterations} に達しました、まだ項目が残っている可能性があります")

        return count

    def delete_items_in_container(self, container_xpath: str,
                                  delete_button_text: str = '削除',
                                  confirm_button_text: str = None,
                                  confirm_button_xpath: str = None,
                                  max_iterations: int = 100) -> int:
        """
        指定コンテナ内で項目をループ削除

        コンテナ要素が消えるまで以下の操作をループ実行：
        1. コンテナが存在するか確認
        2. コンテナ内の削除ボタンをクリック
        3. confirm_button_xpathまたはconfirm_button_textが提供された場合、確認ボタンをクリック

        Args:
            container_xpath: コンテナ要素のXPath
            delete_button_text: 削除ボタンテキスト
            confirm_button_text: 確認ボタンテキスト（オプション）
            confirm_button_xpath: 確認ボタンXPath（オプション、提供された場合優先使用、テキスト一致より正確）
            max_iterations: 最大ループ回数

        Returns:
            削除した項目数
        """
        logger.info(f"コンテナ内での項目削除を開始: {container_xpath}")
        count = 0

        while self.exists_xpath(container_xpath) and count < max_iterations:
            count += 1
            logger.info(f"--- {count} 回目の削除 ---")

            try:
                # 1. コンテナ要素を取得
                try:
                    container = self.driver.find_element(By.XPATH, container_xpath)
                    logger.debug(f"コンテナ要素が見つかりました")
                except Exception as e:
                    logger.error(f"コンテナ要素が見つかりません: {e}")
                    logger.info("コンテナが消えました、削除タスク終了")
                    break

                # 2. コンテナ内で削除ボタンを検索
                clicked = False

                # 方法1: ボタンテキスト完全一致（優先試行）
                try:
                    xpaths = [
                        f"{container_xpath}//button[normalize-space(text())='{delete_button_text}']",
                        f"{container_xpath}//a[normalize-space(text())='{delete_button_text}']",
                        f"{container_xpath}//div[normalize-space(text())='{delete_button_text}']",
                        f"{container_xpath}//span[normalize-space(text())='{delete_button_text}']",
                        f"{container_xpath}//*[normalize-space(text())='{delete_button_text}']",
                        # あいまい一致
                        f"{container_xpath}//button[contains(text(), '{delete_button_text}')]",
                        f"{container_xpath}//a[contains(text(), '{delete_button_text}')]",
                        f"{container_xpath}//div[contains(text(), '{delete_button_text}')]",
                        f"{container_xpath}//span[contains(text(), '{delete_button_text}')]",
                        f"{container_xpath}//*[contains(text(), '{delete_button_text}')]",
                    ]

                    for xpath in xpaths:
                        elements = self.driver.find_elements(By.XPATH, xpath)
                        logger.info(f"  XPath '{xpath}' で {len(elements)} 個の要素が見つかりました")

                        for elem in elements:
                            try:
                                if elem.is_displayed() and elem.is_enabled():
                                    self.driver.execute_script(
                                        "arguments[0].scrollIntoView({block: 'center'});", elem
                                    )
                                    time.sleep(0.3)
                                    elem.click()
                                    clicked = True
                                    logger.info(f"  ✓ クリック成功: {delete_button_text}")
                                    time.sleep(0.5)
                                    break
                            except Exception as inner_e:
                                logger.debug(f"    要素クリック失敗: {inner_e}")
                        if clicked:
                            break

                except Exception as e:
                    logger.debug(f"削除ボタン検索失敗（方法1）: {e}")

                # 方法2: コンテナ内ですべての要素を直接検索
                if not clicked:
                    try:
                        # コンテナ内でテキストを含むすべての要素を検索
                        all_elements = container.find_elements(By.XPATH, f".//*[contains(text(), '{delete_button_text}')]")
                        logger.info(f"  コンテナ内検索：{len(all_elements)} 個の '{delete_button_text}' を含む要素が見つかりました")

                        # 完全一致する要素を優先選択
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

                        # 完全一致を優先使用
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
                                    match_type = "完全一致" if exact_matches else "あいまい一致"
                                    logger.info(f"  ✓ テキストでクリック成功 ({match_type}): {delete_button_text}")
                                    time.sleep(0.5)
                                    break
                            except Exception as inner_e:
                                logger.debug(f"    要素クリック失敗: {inner_e}")

                    except Exception as e:
                        logger.debug(f"コンテナ内検索失敗: {e}")

                if not clicked:
                    logger.warning(f"  ✗ 削除ボタン '{delete_button_text}' をクリックできませんでした")
                    logger.warning("  コンテナ内要素情報：")
                    try:
                        # デバッグ用にコンテナ内のすべての要素を出力
                        all_elems = container.find_elements(By.XPATH, ".//*")
                        logger.info(f"  コンテナ内に合計 {len(all_elems)} 個の要素があります")
                        for i, elem in enumerate(all_elems[:10]):  # 最初の10個のみ表示
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

                # 確認ボタンをクリック（ページ全体で検索、コンテナ内ではない）
                # 確認ボタンは通常ポップアップダイアログ内にあり、ダイアログはコンテナ外にある可能性があります
                if confirm_button_xpath or confirm_button_text:
                    if confirm_button_xpath:
                        logger.info(f"  XPathで確認ボタンをクリック: {confirm_button_xpath}")
                    else:
                        logger.info(f"  確認ボタン '{confirm_button_text}' をクリック...")

                    self.wait(2.5)  # 確認ダイアログ完全表示のために待機時間を延長

                    # 複数の方法で確認ボタンクリックを試行
                    confirm_clicked = False

                    # 方法0: XPathを直接使用（最優先、最正確）
                    if confirm_button_xpath and not confirm_clicked:
                        try:
                            element = self.driver.find_element(By.XPATH, confirm_button_xpath)
                            if element:
                                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                                time.sleep(0.3)
                                element.click()
                                confirm_clicked = True
                                logger.info(f"  ✓ 確認ボタンクリック成功（直接XPath）")
                        except Exception as e:
                            logger.debug(f"  直接XPathクリック失敗: {e}")

                    # 方法1: 完全テキスト一致（XPathが提供されていない場合またはXPath失敗時）
                    if not confirm_clicked and confirm_button_text:
                        try:
                            element = self.find_element_by_text(confirm_button_text, exact_match=True, timeout=5)
                            if element:
                                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                                time.sleep(0.3)
                                element.click()
                                confirm_clicked = True
                                logger.info(f"  ✓ 確認ボタンクリック成功（完全一致）")
                        except Exception as e:
                            logger.debug(f"  完全一致失敗: {e}")

                    # 方法2: JavaScriptクリック（テキスト一致使用時のみ）
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
                                logger.debug(f"  XPath '{xpath}' で {len(elements)} 個の要素が見つかりました")
                                for elem in elements:
                                    try:
                                        if elem.is_displayed() and elem.is_enabled():
                                            self.driver.execute_script("arguments[0].click();", elem)
                                            confirm_clicked = True
                                            logger.info(f"  ✓ 確認ボタンクリック成功 (XPath: {xpath})")
                                            time.sleep(0.5)
                                            break
                                    except Exception as inner_e:
                                        logger.debug(f"    確認ボタンクリック失敗: {inner_e}")
                                if confirm_clicked:
                                    break
                        except Exception as e:
                            logger.debug(f"  JavaScript確認ボタンクリック失敗: {e}")

                    # 方法3: ActionChainsを使用
                    if not confirm_clicked:
                        try:
                            elements = self.find_all_by_text(confirm_button_text, exact_match=False, timeout=2)
                            logger.debug(f"  テキスト検索で {len(elements)} 個の要素が見つかりました")
                            for elem in elements:
                                try:
                                    if elem.is_displayed() and elem.is_enabled():
                                        actions = ActionChains(self.driver)
                                        actions.move_to_element(elem).click().perform()
                                        confirm_clicked = True
                                        logger.info(f"  ✓ ActionChainsクリック成功")
                                        time.sleep(0.5)
                                        break
                                except Exception as inner_e:
                                    logger.debug(f"    ActionChainsクリック失敗: {inner_e}")
                        except Exception as e:
                            logger.debug(f"  ActionChainsクリック失敗: {e}")

                    # まだ失敗の場合、テキストを含むすべての要素情報を出力
                    if not confirm_clicked:
                        logger.warning(f"  ✗ 確認ボタン '{confirm_button_text}' をクリックできませんでした")
                        logger.warning("  テキストを含むすべての要素を検索試行...")
                        try:
                            all_elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{confirm_button_text}')]")
                            logger.info(f"  {len(all_elements)} 個の '{confirm_button_text}' を含む要素が見つかりました")
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
                            logger.debug(f"  要素検索失敗: {e}")

                        self.screenshot(f'failed_click_confirm_{count}')

                # 削除操作完了を待機
                self.wait(1.5)

                logger.info(f"✓ {count} 回目の削除完了")

            except Exception as e:
                logger.error(f"削除プロセスエラー: {e}")
                break

        # 終了理由を確認
        if not self.exists_xpath(container_xpath):
            logger.info(f"[OK] コンテナ内のすべての項目を削除しました、合計 {count} 項目")
        else:
            logger.warning(f"最大ループ回数 {max_iterations} に達しました、まだ項目が残っている可能性があります")

        return count

    # ========================================================================
    # その他の操作
    # ========================================================================

    def close(self):
        """ブラウザを閉じる"""
        self.browser.close()
        logger.info("ブラウザを閉じました")

    def __enter__(self):
        """コンテキストマネージャー入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャー出口"""
        self.close()


# FamilyResetツールクラス - 他のスクリプトでインポートして使用
# 例: from familyreset import FamilyReset
