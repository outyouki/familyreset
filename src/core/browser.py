"""
ブラウザ自動化制御モジュール

Seleniumベースのブラウザ制御機能
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
    """ブラウザコントローラー"""

    def __init__(self,
                 browser_type: str = 'chrome',
                 headless: bool = False,
                 user_agent: Optional[str] = None,
                 window_size: Tuple[int, int] = (1920, 1080)):
        """
        ブラウザコントローラーの初期化

        Args:
            browser_type: ブラウザタイプ 'chrome' | 'firefox' | 'edge'
            headless: ヘッドレスモードにするか（ブラウザウィンドウをリストデモしない）
            user_agent: カスタム User-Agent
            window_size: ウィンドウサイズ (width, height)
        """
        self.browser_type = browser_type.lower()
        self.headless = headless
        self.user_agent = user_agent
        self.window_size = window_size
        self.driver = None

        logger.info(f"ブラウザコントローラーの初期化: {browser_type}")
        self._init_driver()

    def _init_driver(self):
        """初期化 WebDriver"""
        try:
            if self.browser_type == 'chrome':
                self._init_chrome()
            elif self.browser_type == 'firefox':
                self._init_firefox()
            elif self.browser_type == 'edge':
                self._init_edge()
            else:
                raise ValueError(f"非サポートブラウザタイプ: {self.browser_type}")

            # 設定ウィンドウサイズ
            if not self.headless:
                self.driver.set_window_size(*self.window_size)

            logger.info(f"ブラウザ初期化成功: {self.browser_type}")

        except Exception as e:
            logger.error(f"ブラウザ初期化失敗: {e}")
            raise

    def _init_chrome(self):
        """初期化 Chrome ブラウザ"""
        options = ChromeOptions()

        if self.headless:
            options.add_argument('--headless')

        # 一般的な使用設定
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument(f'--window-size={self.window_size[0]},{self.window_size[1]}')

        if self.user_agent:
            options.add_argument(f'user-agent={self.user_agent}')

        # 自動化識別子を禁止
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        self.driver = webdriver.Chrome(options=options)

    def _init_firefox(self):
        """初期化 Firefox ブラウザ"""
        options = FirefoxOptions()

        if self.headless:
            options.add_argument('--headless')

        if self.user_agent:
            options.set_preference("general.useragent.override", self.user_agent)

        self.driver = webdriver.Firefox(options=options)

    def _init_edge(self):
        """初期化 Edge ブラウザ"""
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
        URLを開く

        Args:
            url: 対象URL

        Returns:
            bool: 成功したか
        """
        try:
            self.driver.get(url)
            logger.info(f"開きました: {url}")
            return True
        except Exception as e:
            logger.error(f"URLを開く失敗: {e}")
            return False

    def find_element(self,
                     locator: Tuple[str, str],
                     timeout: int = 10) -> Optional[Any]:
        """
        単一要素を検索

        Args:
            locator: ロケーター (By.ID, 'element_id') または (By.XPATH, '//xpath')
            timeout: タイムアウト時間（秒）

        Returns:
            WebElement または None
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return element
        except TimeoutException:
            logger.warning(f"要素検索タイムアウト: {locator}")
            return None
        except Exception as e:
            logger.error(f"要素の検索に失敗: {e}")
            return None

    def find_elements(self,
                      locator: Tuple[str, str],
                      timeout: int = 10) -> List[Any]:
        """
        複関数関数要素なを検索

        Args:
            locator: ロケーター
            timeout: タイムアウト時間（秒）

        Returns:
            要素リスト
        """
        try:
            elements = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located(locator)
            )
            return elements
        except TimeoutException:
            logger.warning(f"要素が見つかつかりません: {locator}")
            return []
        except Exception as e:
            logger.error(f"要素の検索に失敗: {e}")
            return []

    def click(self,
              locator: Tuple[str, str],
              timeout: int = 10) -> bool:
        """
        要素をクリック

        Args:
            locator: 要素ロケーター
            timeout: タイムアウト時間

        Returns:
            bool: 成功したか
        """
        try:
            element = self.find_element(locator, timeout)
            if element:
                element.click()
                logger.debug(f"すでに要素をクリック: {locator}")
                return True
            return False
        except Exception as e:
            logger.error(f"クリックに失敗: {e}")
            return False

    def input_text(self,
                   locator: Tuple[str, str],
                   text: str,
                   clear_first: bool = True,
                   timeout: int = 10) -> bool:
        """
        テキストを入力

        Args:
            locator: 要素ロケーター
            text: 入力テキスト
            clear_first: 最初にクリアするか
            timeout: タイムアウト時間

        Returns:
            bool: 成功したか
        """
        try:
            element = self.find_element(locator, timeout)
            if element:
                if clear_first:
                    element.clear()
                element.send_keys(text)
                logger.debug(f"すでにテキストを入力へ: {locator}")
                return True
            return False
        except Exception as e:
            logger.error(f"テキストを入力失敗: {e}")
            return False

    def get_text(self,
                 locator: Tuple[str, str],
                 timeout: int = 10) -> Optional[str]:
        """
        要素のテキストを取得

        Args:
            locator: 要素ロケーター
            timeout: タイムアウト時間

        Returns:
            テキストコンテンツまたは None
        """
        try:
            element = self.find_element(locator, timeout)
            if element:
                return element.text
            return None
        except Exception as e:
            logger.error(f"取得テキスト失敗: {e}")
            return None

    def get_attribute(self,
                      locator: Tuple[str, str],
                      attribute: str,
                      timeout: int = 10) -> Optional[str]:
        """
        要素の属性特徴性特徴性を取得

        Args:
            locator: 要素ロケーター
            attribute: 属性特徴性特徴性名前
            timeout: タイムアウト時間

        Returns:
            属性特徴性特徴性値または None
        """
        try:
            element = self.find_element(locator, timeout)
            if element:
                return element.get_attribute(attribute)
            return None
        except Exception as e:
            logger.error(f"属性特徴性特徴性の取得に失敗: {e}")
            return None

    def wait_for_element(self,
                         locator: Tuple[str, str],
                         timeout: int = 10) -> bool:
        """
        要素がエクスポート現在するのを待機

        Args:
            locator: 要素ロケーター
            timeout: タイムアウト時間

        Returns:
            bool: 見つかつかったか
        """
        element = self.find_element(locator, timeout)
        return element is not None

    def execute_script(self, script: str, *args) -> Any:
        """
        JavaScriptを実シリアル

        Args:
            script: JavaScript コード
            *args: アップロード递给 JavaScript パラメータ

        Returns:
            実シリアル結結果
        """
        try:
            result = self.driver.execute_script(script, *args)
            logger.debug(f"すでにJavaScriptを実シリアル")
            return result
        except Exception as e:
            logger.error(f"JavaScriptを実シリアル 失敗: {e}")
            return None

    def scroll_to_element(self, locator: Tuple[str, str], timeout: int = 10) -> bool:
        """
        要素の位置設定までスクロール

        Args:
            locator: 要素ロケーター
            timeout: タイムアウト時間

        Returns:
            bool: 成功したか
        """
        try:
            element = self.find_element(locator, timeout)
            if element:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(0.5)  # 待機スクロール完了した
                logger.debug(f"すでにスクロールして要素: {locator}")
                return True
            return False
        except Exception as e:
            logger.error(f"要素へのスクロールに失敗: {e}")
            return False

    def scroll_page(self, amount: int = 500):
        """
        ページをスクロール

        Args:
            amount: スクロールピクセル数量（正数は下向き，負数は上向き）
        """
        self.driver.execute_script(f"window.scrollBy(0, {amount});")
        logger.debug(f"ページスクロール: {amount}px")

    def screenshot(self, filename: Optional[str] = None,
                  folder: str = "images/screenshots") -> Optional[str]:
        """
        現在にのページリストデモ領領域をキャプチャ

        Args:
            filename: ファイル名，None自動生成
            folder: 保存したファイルフォルダ

        Returns:
            保存存されたファイルパスまたは None
        """
        try:
            # 作成成ファイルフォルダ
            save_folder = Path(folder)
            save_folder.mkdir(parents=True, exist_ok=True)

            # 生成ファイル名
            if filename is None:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"

            filepath = save_folder / filename

            # スクリーンショット
            self.driver.save_screenshot(str(filepath))

            logger.info(f"スクリーンショットすでに保存存: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"スクリーンショット失敗: {e}")
            return None

    def screenshot_full_page(self, filename: Optional[str] = None,
                            folder: str = "images/screenshots") -> Optional[str]:
        """
        キャプチャウェブページ全ボディ（含む必要スクロール一外部）

        Args:
            filename: ファイル名
            folder: 保存したファイルフォルダ

        Returns:
            保存存されたファイルパスまたは None
        """
        try:
            # 作成成ファイルフォルダ
            save_folder = Path(folder)
            save_folder.mkdir(parents=True, exist_ok=True)

            # 生成ファイル名
            if filename is None:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"full_page_{timestamp}.png"

            filepath = save_folder / filename

            # 取得ページ总高さささ
            total_height = self.driver.execute_script(
                "return document.body.scrollHeight"
            )

            # ウィンドウ高ささを取得さ
            window_height = self.driver.execute_script(
                "return window.innerHeight"
            )

            # 使用 PIL 完全に結合スクリーンショット
            from PIL import Image
            import io

            screenshots = []
            current_position = 0

            while current_position < total_height:
                # キャプチャ現在リストデモされている領領域
                screenshot_binary = self.driver.get_screenshot_as_png()
                screenshot = Image.open(io.BytesIO(screenshot_binary))
                screenshots.append(screenshot)

                # スクロールして回の部分
                current_position += window_height - 50  # 重複50px欠落を回避
                self.driver.execute_script(f"window.scrollTo(0, {current_position});")
                time.sleep(0.3)  # 待機スクロール完了した

            # 画画像画像画像を結合
            if screenshots:
                total_width = screenshots[0].width
                total_image_height = sum(img.height for img in screenshots)

                final_image = Image.new('RGB', (total_width, total_image_height))

                y_offset = 0
                for screenshot in screenshots:
                    final_image.paste(screenshot, (0, y_offset))
                    y_offset += screenshot.height

                final_image.save(str(filepath))
                logger.info(f"全ページスクリーンショットすでに保存存: {filepath}")
                return str(filepath)

            return None

        except Exception as e:
            logger.error(f"全ページスクリーンショット失敗: {e}")
            return None

    def get_url(self) -> str:
        """現在にのURLを取得"""
        return self.driver.current_url

    def get_title(self) -> str:
        """ページタイトルを取得"""
        return self.driver.title

    def back(self):
        """戻る"""
        self.driver.back()
        logger.debug("ページ戻る")

    def forward(self):
        """前インポート"""
        self.driver.forward()
        logger.debug("進む")

    def refresh(self):
        """変更新ページ"""
        self.driver.refresh()
        logger.debug("ページ変更新")

    def close(self):
        """ブラウザを閉じる"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("ブラウザを閉じました")

    def __enter__(self):
        """コンテキストマネージャー入りインターフェース"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャー終了した"""
        self.close()

    def __del__(self):
        """デストラクタ，正しい保存ブラウザを閉じる"""
        # 自動クローズをコメントアウト，、ブラウザを開いたままにする
        # self.close()
        pass


# 便利用ロケーターによって常数量
class Locator:
    """要素ロケーターによって常数量"""
    ID = By.ID
    NAME = By.NAME
    CLASS_NAME = By.CLASS_NAME
    TAG_NAME = By.TAG_NAME
    LINK_TEXT = By.LINK_TEXT
    PARTIAL_LINK_TEXT = By.PARTIAL_LINK_TEXT
    CSS_SELECTOR = By.CSS_SELECTOR
    XPATH = By.XPATH


# テスト関関数
if __name__ == "__main__":
    # ログ設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("ブラウザ制御器テスト")
    print("=" * 60)

    # 使用コンテキストマネージャーを使用して自動ブラウザを閉じる
    with BrowserController(browser_type='chrome', headless=False) as browser:
        # ウェブページを開く
        print("\n1. 開くBaidu...")
        browser.open('https://www.baidu.com')

        # 検索検索ボックス
        print("2. 検索検索ボックス...")
        search_box = browser.find_element((Locator.ID, 'kw'))
        if search_box:
            print("   [OK] 見つかつけるへ検索ボックス")

            # テキストを入力
            print("3. 検索を入力コンテンツ...")
            browser.input_text((Locator.ID, 'kw'), 'Python Selenium')

            # クリック検索ボタン
            print("4. クリック検索...")
            browser.click((Locator.ID, 'su'))

            # 結結果を待って読み込みみみみ込みみみ
            time.sleep(2)

            # スクリーンショット
            print("5. スクリーンショット...")
            browser.screenshot('baidu_search_result.png')

            print("\n[OK] テスト完了した")
        else:
            print("   [X] 未見つかつけるへ検索ボックス")
