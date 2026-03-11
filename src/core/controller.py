"""
マウスキーボード制御モジュール
"""

import pyautogui
import keyboard
import time
import logging
from typing import Tuple, List, Optional

logger = logging.getLogger(__name__)

class MouseController:
    """マウス制御器"""

    def __init__(self,move_duration=0.1,click_delay=0.05):
        """
                初期化マウス制御器

                Args:
                    move_duration: マウス移動動アニメーション時間（秒）
                    click_delay: クリック後の遅延時間（秒）
                """
        self.move_duration = move_duration
        self.click_delay = click_delay

        #セキュリティ設定
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.05 #各アクション後の一時停止止時間

        logger.info(f"MouseController初期化完了した")

    def move_to(self,x: int, y: int,duration:float =None) -> bool:
        """
        移動動マウスへポインタ定位置設定

        Args:
            x: X座標
            y: Y座標
            duration: 移動時間，Noneはデフォルト値を使用

        Returns:
            bool: 成功したか
        """
        try:
            dur = duration if duration is not None else self.move_duration
            pyautogui.moveTo(x, y,duration=dur)
            logger.debug(f"マウス移動動へ（{x},{y}")
            return True
        except Exception as e:
            logger.error(f"マウス移動動に失敗：{e}")
            return False

    def click(self,x:int=None,y:int=None,button:str="left",clicks:int =1,interval:float =None)->bool:
        """
        クリックポインタ定位置設定

        Args:
            x, y: 座標，Noneリストデモ現在位置設定
            button: 'left'|'right'|'middle'
            clicks: クリック回関数
            interval: 多回クリック之スペーススペース隔

        Returns:
            bool: 成功したか
        """
        try:
            if x is not None and y is not None:
                self.move_to(x,y)

            pyautogui.click(button=button,clicks=clicks,interval=interval)
            time.sleep(self.click_delay)

            logger.debug(f"クリック（{x},{y}){button}ボタン{clicks}回")
            return True
        except Exception as e:
            logger.error(f"クリックに失敗：{e}")
            return False

    def double_click(self,x:int =None,y:int = None,button:str='left') -> bool:
        """ダブルクリック"""
        return self.click(x,y,button,clicks=2,interval=0.1)

    def right_click(self,x:int =None,y:int=None) -> bool:
        """右キークリック"""
        return self.click(x,y,button="right")

    def drag_to(self,start_x:int,start_y:int,end_x:int,end_y:int,duration:float =1.0,button:str ='left') -> bool:
        """
        ドラッグドラッグ操作作成

        Args:
            start_x, start_y: 起始位置設定
            end_x, end_y: 終了了位置設定
            duration: ドラッグドラッグ時間
            button: マウスボタン

        Returns:
            bool: 成功したか
        """
        try:
            self.move_to(start_x,start_y)
            pyautogui.dragTo(start_x,start_y,duration=duration,button=button)
            logger.debug(f"から({start_x},{start_y})ドラッグドラッグへ({end_x},{end_y})")
            return True
        except Exception as e:
            logger.error(f"ドラッグドラッグ失敗：{e}")
            return False
    def scroll(self,clicks:int,x:int=None,y:int=None)->bool:
        """
        スクロールマウススクロール轮

        Args:
            clicks: スクロール単一位置，正数向上，负関数向下
            x, y: スクロール位置設定，Noneリストデモ現在位置設定

        Returns:
            bool: 成功したか
        """
        try:
            if x is not None and y is not None:
                self.move_to(x,y)

            pyautogui.scroll(clicks)
            logger.debug(f"スクロール{clicks}単一位置")
            return True
        except Exception as e:
            logger.error(f"スクロール失敗：{e}")
            return False

    def get_position(self)->Tuple[int,int]:
        """取得現在マウス位置設定"""
        return pyautogui.position()

    def screenshot_region(self,x1:int,y1:int,x2:int,y2:int):
        """
        キャプチャスクリーン領領域

        Args:
            x1, y1: 左上角座標
            x2, y2: 右下角座標

        Returns:
            PIL.Image: スクリーンショット画画像画像画像
        """
        try:
            region =(x1,y1,x2-x1,y2-y1)
            screenshot = pyautogui.screenshot(region=region)
            logger.debug(f"キャプチャ領領域:({x1},{y1})-({x2},{y2})")
            return screenshot
        except Exception as e:
            logger.error(f"領領域スクリーンショット失敗:{e}")
            return None

class KeyboardController:
    """キーボード制御器"""

    def __init__(self,key_delay=0.1):
        """
        初期化キーボード制御器

        Args:
            key_delay: 押すキー遅延時間（秒）
        """
        self.key_delay = key_delay
        logger.info(f"KeyboardController初期化完了した")

    def press(self,key:str,presses:int=1,interval:float=None)->bool:
        """
        押す下押すキー

        Args:
            key: 押すキー名前前
            presses: 押す下回関数
            interval: 複関数関数回押すキー之スペーススペース隔

        Returns:
            bool: 成功したか
        """
        try:
            inter = interval if interval is not None else self.key_delay
            pyautogui.press(key, presses=presses, interval=inter)
            logger.debug(f"押す下押すキー: {key} {presses}回")
            return True
        except Exception as e:
            logger.error(f"押すキー失敗: {e}")
            return False

    def type_text(self, text: str, interval: float = None) -> bool:
        """
        テキストを入力

        Args:
            text: 入力が必要テキスト
            interval: 文フィールド間の間隔

        Returns:
            bool: 成功したか
        """
        try:
            inter = interval if interval is not None else self.key_delay
            pyautogui.write(text, interval=inter)
            logger.debug(f"テキストを入力: {text}")
            return True
        except Exception as e:
            logger.error(f"テキスト入力失敗: {e}")
            return False

    def hotkey(self,*keys:str)->bool:
        """
        キーの組み結合わせを押すみ結合わせキー

        Args:
            *keys: 押すキー順序列，など 'ctrl', 'c'

        Returns:
            bool: 成功したか
        """
        try:
            pyautogui.hotkey(*keys)
            logger.debug(f"組み結合わせキー：{'+'.join(keys)}")
            return True
        except Exception as e:
            logger.error(f"組み結合わせキー失敗:{e}")
            return False

    def key_down(self,key:str)->bool:
        """押す下押すキー（放さない）"""
        try:
            pyautogui.keyDown(key)
            logger.debug(f"押す下押すキー：{key}")
            return True
        except Exception as e:
            logger.error(f"押す下押すキー失敗{e}")
            return False


    def key_up(self,key:str)->bool:
        """デコード放押すキー"""
        try:
            pyautogui.keyUp(key)
            logger.debug(f"デコード放押すキー:{key}")
            return True
        except Exception as e:
            logger.error(f"デコード放押すキー失敗:{e}")
            return False

class HotkeyManager:
    """ホットキーマネージャー"""
    def __init__(self):
        self.hotkeys = {}
        self.running = False
        logger.info("HotkeyManager初期化完了した")

    def register(self,key:str,callback,description:str = "")->bool:
        """
        コマニュアルホットキー

        Args:
            key: ホットキー，など 'f2', 'ctrl+shift+a'
            callback: コールバック関関数
            description: ホットキー説明

        Returns:
            bool: 成功したか
        """
        try:
            keyboard.add_hotkey(key,callback)
            self.hotkeys[key] = description
            logger.info(f"コマニュアルホットキー：{key}-{description}")
            return True
        except Exception as e:
            logger.error(f"ホットキー登録に失敗：{e}")
            return False

    def unregister(self,key:str)->bool:
        """コ破棄ホットキー"""
        try:
            keyboard.remove_hotkey(key)
            if key in self.hotkeys:
                del self.hotkeys[key]
                logger.info(f"コ破棄ホットキー：{key}")
                return True
        except Exception as e:
            logger.error(f"ホットキーコ破棄に失敗{e}")
            return False

    def start(self):
        logger.info("開く始リッスンホットキー...")
        logger.info("コマニュアルホットキー：")
        for key,desc in self.hotkeys.items():
            logger.info(f"  {key}-{desc}")

        self.running = True
        print("\nホットキーリッスンすでに起動，押すESC終了了リッスン")

        try:
            keyboard.wait("esc")
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

    def stop(self):
        """リッスンを停止"""
        self.running = False
        logger.info("ホットキーリッスンが停止")

    def emergency_stop(self):
        """緊急停止！すべての自動操作を停止"""
        logger.warning("緊急停止！")
        # マウスをセキュリティ位置に移動
        width, height = pyautogui.size()
        pyautogui.moveTo(width//2,height//2)
        self.stop()

# テスト関数
#if__name__ == "__main__":
if __name__ == "__main__":
    #ログ設定
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    print("テスト制御モジュール...")
    print("1. テストマウス移動動")
    print("2. テストマウスクリック")
    print("3. テストキーボード入力")
    print("4. テストホットキーリッスン")
    choice = input("ください選択テスト項目 (1-4): ").strip()

    if choice == "1":
        print("マウス移動動テスト...")
        mouse = MouseController()
        width, height = pyautogui.size()

        # 描画画像画像1つ三角形
        points = [
            (width // 2, height // 2 - 100),
            (width // 2 + 100, height // 2 + 100),
            (width // 2 - 100, height // 2 + 100),
            (width // 2, height // 2 - 100)
        ]

        for i, (x, y) in enumerate(points):
            mouse.move_to(x, y)
            print(f"移動動へノード {i + 1}: ({x}, {y})")
            time.sleep(0.5)

        print("✓ マウス移動動テスト完了した")

    elif choice == "2":
        print("マウスクリックテスト...")
        mouse = MouseController()
        width, height = pyautogui.size()

        # クリックスクリーン中心
        mouse.click(width // 2, height // 2)
        print(f"クリックスクリーン中心: ({width // 2}, {height // 2})")

        # ダブルクリックテスト
        time.sleep(1)
        mouse.double_click(width // 2, height // 2 + 50)
        print(f"ダブルクリック: ({width // 2}, {height // 2 + 50})")

        print("✓ マウスクリックテスト完了した")

    elif choice == "3":
        print("キーボード入力テスト...")
        keyboard_ctrl = KeyboardController()

        print("5秒后〜をにメモ帳に文フィールドを入力，ください切設定換へメモ帳...")
        time.sleep(5)

        text = "これはキーボード制御テスト\n時間: " + time.strftime("%Y-%m-%d %H:%M:%S")
        keyboard_ctrl.type_text(text)

        print("✓ キーボード入力テスト完了した")

    elif choice == "4":
        print("ホットキーリッスンテスト...")
        hotkey_mgr = HotkeyManager()


        def on_start():
            print("[ホットキー] 開く始実シリアル")


        def on_stop():
            print("[ホットキー] 停止止実シリアル")


        def on_pause():
            print("[ホットキー] 一時停止止")


        # コマニュアルホットキー
        hotkey_mgr.register('f2', on_start, "開く始実シリアル")
        hotkey_mgr.register('f3', on_stop, "停止止実シリアル")
        hotkey_mgr.register('f5', on_pause, "一時停止止/継続")
        hotkey_mgr.register('ctrl+shift+q', hotkey_mgr.emergency_stop, "紧急停止止")

        print("ホットキー説明:")
        print("  F2: 開く始実シリアル")
        print("  F3: 停止止実シリアル")
        print("  F5: 一時停止止/継続")
        print("  Ctrl+Shift+Q: 紧急停止止")
        print("  ESC: 終了了ホットキーキーリッスン")
        print("\n実現にできます上記のホットキーを押すキーテスト，押すESC終了了")

        # 開く始リッスン
        hotkey_mgr.start()

        print("✓ ホットキーリッスンテスト完了した")

    else:
        print("無効選択")






