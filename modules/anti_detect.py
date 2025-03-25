"""
反截图检测模块 - 提供基本的反截图检测机制
防止被浏览器安全检测或其他检测工具识别
"""
import os
import sys
import time
import random
import pyautogui
from threading import Thread, Event

# 导入配置
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class AntiDetectManager:
    """反截图检测管理器 - 提供基本的反检测机制"""
    
    def __init__(self, callback=None):
        """
        初始化反检测管理器
        :param callback: 检测到截图行为时的回调函数
        """
        self.callback = callback
        self.running = False
        self.stop_event = Event()
        
        # 检测参数
        self.check_interval = 0.5  # 检查间隔（秒）
        self.mouse_position_history = []  # 鼠标位置历史
        self.keyboard_state = {}  # 键盘状态
        self.screen_state = None  # 屏幕状态
    
    def start(self):
        """启动反检测监视线程"""
        if not self.running:
            self.running = True
            self.stop_event.clear()
            self.monitor_thread = Thread(target=self._monitor_activity, daemon=True)
            self.monitor_thread.start()
            print("反截图检测已启动")
            return True
        return False
    
    def stop(self):
        """停止反检测监视"""
        if self.running:
            self.running = False
            self.stop_event.set()
            if hasattr(self, 'monitor_thread') and self.monitor_thread.is_alive():
                self.monitor_thread.join(1.0)
            print("反截图检测已停止")
            return True
        return False
    
    def _monitor_activity(self):
        """监视活动线程"""
        print("开始监视系统活动...")
        
        # 初始化状态
        self._update_states()
        
        while not self.stop_event.is_set():
            # 检查系统状态变化
            detection = self._check_for_detection()
            
            if detection:
                print(f"检测到可疑活动: {detection}")
                
                # 如果有回调函数，执行回调
                if self.callback:
                    self.callback(detection)
                
                # 执行反检测措施
                self._apply_countermeasures(detection)
            
            # 更新状态
            self._update_states()
            
            # 随机等待时间，避免被检测到固定模式
            wait_time = self.check_interval + random.uniform(-0.1, 0.1)
            time.sleep(max(0.1, wait_time))
    
    def _update_states(self):
        """更新系统状态"""
        try:
            # 更新鼠标位置历史
            current_position = pyautogui.position()
            self.mouse_position_history.append(current_position)
            
            # 只保留最近的10个位置
            if len(self.mouse_position_history) > 10:
                self.mouse_position_history.pop(0)
            
            # 更新屏幕状态（可以采样屏幕的部分区域作为指纹）
            # 为了性能考虑，这里只取一个小区域的截图
            screen_region = (0, 0, 10, 10)  # 左上角10x10像素区域
            self.screen_state = pyautogui.screenshot(region=screen_region)
        except Exception as e:
            print(f"更新状态时出错: {e}")
    
    def _check_for_detection(self):
        """
        检查可能的截图检测行为
        :return: 检测到的行为描述，如果没有检测到则返回None
        """
        try:
            # 检查鼠标突然跳跃
            if len(self.mouse_position_history) >= 2:
                prev_pos = self.mouse_position_history[-2]
                curr_pos = self.mouse_position_history[-1]
                
                # 计算鼠标移动距离
                distance = ((curr_pos[0] - prev_pos[0]) ** 2 + (curr_pos[1] - prev_pos[1]) ** 2) ** 0.5
                
                # 如果距离过大，可能是截图工具的快速操作
                if distance > 500:  # 阈值可以根据实际情况调整
                    return "鼠标突然大幅移动，可能是截图操作"
            
            # 检查屏幕突然变化
            if self.screen_state is not None:
                current_screen = pyautogui.screenshot(region=(0, 0, 10, 10))
                
                # 比较屏幕状态变化
                # 这里简化处理，实际可以计算图像差异
                if current_screen != self.screen_state:
                    pixel_diff = True  # 简化的差异检测
                    if pixel_diff:
                        return "屏幕内容突然变化，可能是截图操作"
            
            # 没有检测到异常
            return None
        except Exception as e:
            print(f"检测过程出错: {e}")
            return None
    
    def _apply_countermeasures(self, detection_type):
        """
        应用反检测措施
        :param detection_type: 检测到的行为类型
        """
        try:
            print(f"应用反检测措施，应对: {detection_type}")
            
            # 随机选择一种反检测措施
            measures = [
                self._measure_move_mouse,
                self._measure_simulate_activity,
                # 可以添加更多反检测措施
            ]
            
            # 随机选择并执行一种措施
            random.choice(measures)()
            
        except Exception as e:
            print(f"应用反检测措施时出错: {e}")
    
    def _measure_move_mouse(self):
        """反检测措施：轻微移动鼠标"""
        try:
            # 获取当前鼠标位置
            current_x, current_y = pyautogui.position()
            
            # 在当前位置附近随机移动
            offset_x = random.randint(-5, 5)
            offset_y = random.randint(-5, 5)
            
            # 移动鼠标（相对移动）
            pyautogui.moveRel(offset_x, offset_y, duration=0.2)
            
            # 移回原位置
            time.sleep(0.1)
            pyautogui.moveTo(current_x, current_y, duration=0.2)
            
            print("已执行鼠标移动反检测措施")
        except Exception as e:
            print(f"鼠标移动措施失败: {e}")
    
    def _measure_simulate_activity(self):
        """反检测措施：模拟正常活动"""
        try:
            # 简单的模拟活动，如轻微移动鼠标
            current_x, current_y = pyautogui.position()
            
            # 记录原始位置
            original_x, original_y = current_x, current_y
            
            # 执行一系列小动作
            for _ in range(3):
                # 随机移动
                offset_x = random.randint(-20, 20)
                offset_y = random.randint(-20, 20)
                pyautogui.moveRel(offset_x, offset_y, duration=0.1)
                time.sleep(0.05)
            
            # 返回原始位置
            pyautogui.moveTo(original_x, original_y, duration=0.2)
            
            print("已执行活动模拟反检测措施")
        except Exception as e:
            print(f"活动模拟措施失败: {e}")

# 简单测试
if __name__ == "__main__":
    def on_detection(detection_type):
        print(f"检测到: {detection_type}")
    
    anti_detect = AntiDetectManager(callback=on_detection)
    anti_detect.start()
    
    try:
        print("反截图检测已启动，按Ctrl+C退出...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        anti_detect.stop()
        print("程序已退出") 