"""
鼠标键盘控制模块
"""

import pyautogui
import keyboard
import time
import logging
from typing import Tuple, List, Optional

logger = logging.getLogger(__name__)

class MouseController:
    """鼠标控制器"""

    def __init__(self,move_duration=0.1,click_delay=0.05):
        """
                初始化鼠标控制器

                Args:
                    move_duration: 鼠标移动动画时间（秒）
                    click_delay: 点击后延迟时间（秒）
                """
        self.move_duration = move_duration
        self.click_delay = click_delay

        #安全设置
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.05 #每个动作后的暂停时间

        logger.info(f"MouseController初始化完成")

    def move_to(self,x: int, y: int,duration:float =None) -> bool:
        """
        移动鼠标到指定位置

        Args:
            x: X坐标
            y: Y坐标
            duration: 移动时间，None使用默认值

        Returns:
            bool: 是否成功
        """
        try:
            dur = duration if duration is not None else self.move_duration
            pyautogui.moveTo(x, y,duration=dur)
            logger.debug(f"鼠标移动到（{x},{y}")
            return True
        except Exception as e:
            logger.error(f"鼠标移动失败：{e}")
            return False

    def click(self,x:int=None,y:int=None,button:str="left",clicks:int =1,interval:float =None)->bool:
        """
        点击指定位置

        Args:
            x, y: 坐标，None表示当前位置
            button: 'left'|'right'|'middle'
            clicks: 点击次数
            interval: 多次点击之间的间隔

        Returns:
            bool: 是否成功
        """
        try:
            if x is not None and y is not None:
                self.move_to(x,y)

            pyautogui.click(button=button,clicks=clicks,interval=interval)
            time.sleep(self.click_delay)

            logger.debug(f"点击（{x},{y}){button}按钮{clicks}次")
            return True
        except Exception as e:
            logger.error(f"点击失败：{e}")
            return False

    def double_click(self,x:int =None,y:int = None,button:str='left') -> bool:
        """双击"""
        return self.click(x,y,button,clicks=2,interval=0.1)

    def right_click(self,x:int =None,y:int=None) -> bool:
        """右键点击"""
        return self.click(x,y,button="right")

    def drag_to(self,start_x:int,start_y:int,end_x:int,end_y:int,duration:float =1.0,button:str ='left') -> bool:
        """
        拖拽操作

        Args:
            start_x, start_y: 起始位置
            end_x, end_y: 结束位置
            duration: 拖拽时间
            button: 鼠标按钮

        Returns:
            bool: 是否成功
        """
        try:
            self.move_to(start_x,start_y)
            pyautogui.dragTo(start_x,start_y,duration=duration,button=button)
            logger.debug(f"从({start_x},{start_y})拖拽到({end_x},{end_y})")
            return True
        except Exception as e:
            logger.error(f"拖拽失败：{e}")
            return False
    def scroll(self,clicks:int,x:int=None,y:int=None)->bool:
        """
        滚动鼠标滚轮

        Args:
            clicks: 滚动单位，正数向上，负数向下
            x, y: 滚动位置，None表示当前位置

        Returns:
            bool: 是否成功
        """
        try:
            if x is not None and y is not None:
                self.move_to(x,y)

            pyautogui.scroll(clicks)
            logger.debug(f"滚动{clicks}单位")
            return True
        except Exception as e:
            logger.error(f"滚动失败：{e}")
            return False

    def get_position(self)->Tuple[int,int]:
        """获取当前鼠标位置"""
        return pyautogui.position()

    def screenshot_region(self,x1:int,y1:int,x2:int,y2:int):
        """
        截取屏幕区域

        Args:
            x1, y1: 左上角坐标
            x2, y2: 右下角坐标

        Returns:
            PIL.Image: 截图图像
        """
        try:
            region =(x1,y1,x2-x1,y2-y1)
            screenshot = pyautogui.screenshot(region=region)
            logger.debug(f"截取区域:({x1},{y1})-({x2},{y2})")
            return screenshot
        except Exception as e:
            logger.error(f"区域截图失败:{e}")
            return None

class KeyboardController:
    """键盘控制器"""

    def __init__(self,key_delay=0.1):
        """
        初始化键盘控制器

        Args:
            key_delay: 按键延迟时间（秒）
        """
        self.key_delay = key_delay
        logger.info(f"KeyboardController初始化完成")

    def press(self,key:str,presses:int=1,interval:float=None)->bool:
        """
        按下按键

        Args:
            key: 按键名称
            presses: 按下次数
            interval: 多次按键之间的间隔

        Returns:
            bool: 是否成功
        """
        try:
            inter = interval if interval is not None else self.key_delay
            pyautogui.press(key, presses=presses, interval=inter)
            logger.debug(f"按下按键: {key} {presses}次")
            return True
        except Exception as e:
            logger.error(f"按键失败: {e}")
            return False

    def type_text(self, text: str, interval: float = None) -> bool:
        """
        输入文本

        Args:
            text: 要输入的文本
            interval: 字符之间的间隔

        Returns:
            bool: 是否成功
        """
        try:
            inter = interval if interval is not None else self.key_delay
            pyautogui.write(text, interval=inter)
            logger.debug(f"输入文本: {text}")
            return True
        except Exception as e:
            logger.error(f"文本输入失败: {e}")
            return False

    def hotkey(self,*keys:str)->bool:
        """
        按下组合键

        Args:
            *keys: 按键序列，如 'ctrl', 'c'

        Returns:
            bool: 是否成功
        """
        try:
            pyautogui.hotkey(*keys)
            logger.debug(f"组合键：{'+'.join(keys)}")
            return True
        except Exception as e:
            logger.error(f"组合键失败:{e}")
            return False

    def key_down(self,key:str)->bool:
        """按下按键（不是放）"""
        try:
            pyautogui.keyDown(key)
            logger.debug(f"按下按键：{key}")
            return True
        except Exception as e:
            logger.error(f"按下按键失败{e}")
            return False


    def key_up(self,key:str)->bool:
        """释放按键"""
        try:
            pyautogui.keyUp(key)
            logger.debug(f"释放按键:{key}")
            return True
        except Exception as e:
            logger.error(f"释放按键失败:{e}")
            return False

class HotkeyManager:
    """热键管理器"""
    def __init__(self):
        self.hotkeys = {}
        self.running = False
        logger.info("HotkeyManager初始化完成")

    def register(self,key:str,callback,description:str = "")->bool:
        """
        注册热键

        Args:
            key: 热键，如 'f2', 'ctrl+shift+a'
            callback: 回调函数
            description: 热键描述

        Returns:
            bool: 是否成功
        """
        try:
            keyboard.add_hotkey(key,callback)
            self.hotkeys[key] = description
            logger.info(f"注册热键：{key}-{description}")
            return True
        except Exception as e:
            logger.error(f"热键注册失败：{e}")
            return False

    def unregister(self,key:str)->bool:
        """注销热键"""
        try:
            keyboard.remove_hotkey(key)
            if key in self.hotkeys:
                del self.hotkeys[key]
                logger.info(f"注销热键：{key}")
                return True
        except Exception as e:
            logger.error(f"热键注销失败{e}")
            return False

    def start(self):
        logger.info("开始监听热键...")
        logger.info("注册热键：")
        for key,desc in self.hotkeys.items():
            logger.info(f"  {key}-{desc}")

        self.running = True
        print("\n热键监听已启动，按ESC退出监听")

        try:
            keyboard.wait("esc")
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

    def stop(self):
        """停止监听"""
        self.running = False
        logger.info("热键监听已停止")

    def emergency_stop(self):
        """紧急停止所有自动化操作"""
        logger.waring("紧急停止！")
        #见鼠标移动安全位置
        width,height = pyautogui.size()
        pyautogui.moveTo(width//2,height//2)
        self.stop()

 #测试函数
#if__name__ == "__main__":
if __name__ == "__main__":
    #配置日志
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    print("测试控制模块...")
    print("1. 测试鼠标移动")
    print("2. 测试鼠标点击")
    print("3. 测试键盘输入")
    print("4. 测试热键监听")
    choice = input("请选择测试项目 (1-4): ").strip()

    if choice == "1":
        print("鼠标移动测试...")
        mouse = MouseController()
        width, height = pyautogui.size()

        # 画一个三角形
        points = [
            (width // 2, height // 2 - 100),
            (width // 2 + 100, height // 2 + 100),
            (width // 2 - 100, height // 2 + 100),
            (width // 2, height // 2 - 100)
        ]

        for i, (x, y) in enumerate(points):
            mouse.move_to(x, y)
            print(f"移动到点 {i + 1}: ({x}, {y})")
            time.sleep(0.5)

        print("✓ 鼠标移动测试完成")

    elif choice == "2":
        print("鼠标点击测试...")
        mouse = MouseController()
        width, height = pyautogui.size()

        # 点击屏幕中心
        mouse.click(width // 2, height // 2)
        print(f"点击屏幕中心: ({width // 2}, {height // 2})")

        # 双击测试
        time.sleep(1)
        mouse.double_click(width // 2, height // 2 + 50)
        print(f"双击: ({width // 2}, {height // 2 + 50})")

        print("✓ 鼠标点击测试完成")

    elif choice == "3":
        print("键盘输入测试...")
        keyboard_ctrl = KeyboardController()

        print("5秒后将在记事本输入文字，请切换到记事本...")
        time.sleep(5)

        text = "这是键盘控制测试\n时间: " + time.strftime("%Y-%m-%d %H:%M:%S")
        keyboard_ctrl.type_text(text)

        print("✓ 键盘输入测试完成")

    elif choice == "4":
        print("热键监听测试...")
        hotkey_mgr = HotkeyManager()


        def on_start():
            print("[热键] 开始执行")


        def on_stop():
            print("[热键] 停止执行")


        def on_pause():
            print("[热键] 暂停")


        # 注册热键
        hotkey_mgr.register('f2', on_start, "开始执行")
        hotkey_mgr.register('f3', on_stop, "停止执行")
        hotkey_mgr.register('f5', on_pause, "暂停/继续")
        hotkey_mgr.register('ctrl+shift+q', hotkey_mgr.emergency_stop, "紧急停止")

        print("热键说明:")
        print("  F2: 开始执行")
        print("  F3: 停止执行")
        print("  F5: 暂停/继续")
        print("  Ctrl+Shift+Q: 紧急停止")
        print("  ESC: 退出热键监听")
        print("\n现在可以按上述热键测试，按ESC退出")

        # 开始监听
        hotkey_mgr.start()

        print("✓ 热键监听测试完成")

    else:
        print("无效选择")






