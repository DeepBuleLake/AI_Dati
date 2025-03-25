"""
截图模块 - 负责实现全局热键截图功能
使用pyautogui和keyboard库实现
"""
import os
import time
import pyautogui
import keyboard
from datetime import datetime
from threading import Thread, Event

# 导入配置
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SCREENSHOT_HOTKEY, SCREENSHOT_FORMAT, SCREENSHOT_DIR

class ScreenshotManager:
    """截图管理器 - 负责监听热键和截取屏幕"""
    
    def __init__(self, callback=None):
        """
        初始化截图管理器
        :param callback: 截图完成后的回调函数，接收截图路径参数
        """
        self.callback = callback
        self.running = False
        self.stop_event = Event()
        self.hotkey = SCREENSHOT_HOTKEY
    
    def start(self):
        """启动热键监听线程"""
        if not self.running:
            self.running = True
            self.stop_event.clear()
            self.listener_thread = Thread(target=self._hotkey_listener, daemon=True)
            self.listener_thread.start()
            print(f"截图监听已启动，按 {self.hotkey} 进行截图")
            return True
        return False
    
    def stop(self):
        """停止热键监听"""
        if self.running:
            self.running = False
            self.stop_event.set()
            if hasattr(self, 'listener_thread') and self.listener_thread.is_alive():
                self.listener_thread.join(1.0)
            return True
        return False
    
    def _hotkey_listener(self):
        """热键监听线程"""
        keyboard.add_hotkey(self.hotkey, self.take_screenshot)
        
        # 保持线程运行，直到收到停止信号
        while not self.stop_event.is_set():
            time.sleep(0.1)
        
        # 清理热键
        keyboard.remove_hotkey(self.hotkey)
    
    def take_screenshot(self):
        """
        执行屏幕截图，并返回保存的文件路径
        :return: 截图文件的路径
        """
        try:
            # 生成文件名: timestamp.png
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{timestamp}.{SCREENSHOT_FORMAT}"
            filepath = os.path.join(SCREENSHOT_DIR, filename)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # 截取全屏
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            
            print(f"截图已保存: {filepath}")
            
            # 如果有回调函数，执行回调
            if self.callback:
                self.callback(filepath)
            
            return filepath
        except Exception as e:
            print(f"截图失败: {e}")
            return None

# 简单测试
if __name__ == "__main__":
    def on_screenshot(path):
        print(f"截图回调: {path}")
    
    manager = ScreenshotManager(callback=on_screenshot)
    manager.start()
    
    try:
        print("按 Ctrl+Alt+A 进行截图，按 Ctrl+C 退出...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        manager.stop()
        print("程序已退出") 