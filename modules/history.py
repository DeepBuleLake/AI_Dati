"""
历史记录模块 - 负责保存和查询识别历史
使用JSON文件存储历史记录
"""
import os
import sys
import json
from datetime import datetime
from threading import Lock

# 导入配置
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import HISTORY_FILE

class HistoryManager:
    """历史记录管理器 - 负责历史记录的存储和查询"""
    
    def __init__(self):
        """初始化历史记录管理器"""
        self.history_file = HISTORY_FILE
        self.lock = Lock()  # 用于线程安全的文件访问
        
        # 确保历史记录文件存在
        self._ensure_history_file()
    
    def _ensure_history_file(self):
        """确保历史记录文件存在"""
        if not os.path.exists(self.history_file):
            # 创建目录（如果不存在）
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            
            # 创建空的历史记录文件
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    def add_record(self, image_path, recognition_result):
        """
        添加历史记录
        :param image_path: 截图路径
        :param recognition_result: 识别结果
        :return: 添加的记录ID
        """
        # 创建记录
        record = {
            "id": self._generate_id(),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "image_path": image_path,
            "recognition_result": recognition_result,
        }
        
        # 添加到历史记录
        with self.lock:
            history = self.get_all_records()
            history.append(record)
            
            # 保存历史记录
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        
        print(f"已添加历史记录: ID={record['id']}")
        return record["id"]
    
    def get_record(self, record_id):
        """
        获取单条历史记录
        :param record_id: 记录ID
        :return: 历史记录，如果不存在则返回None
        """
        history = self.get_all_records()
        
        for record in history:
            if record.get("id") == record_id:
                return record
        
        return None
    
    def get_all_records(self):
        """
        获取所有历史记录
        :return: 历史记录列表
        """
        with self.lock:
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                return history
            except (FileNotFoundError, json.JSONDecodeError):
                # 如果文件不存在或JSON格式错误，则返回空列表
                return []
    
    def delete_record(self, record_id):
        """
        删除历史记录
        :param record_id: 记录ID
        :return: 是否删除成功
        """
        with self.lock:
            history = self.get_all_records()
            
            # 查找并删除记录
            for i, record in enumerate(history):
                if record.get("id") == record_id:
                    del history[i]
                    
                    # 保存历史记录
                    with open(self.history_file, 'w', encoding='utf-8') as f:
                        json.dump(history, f, ensure_ascii=False, indent=2)
                    
                    print(f"已删除历史记录: ID={record_id}")
                    return True
        
        print(f"删除历史记录失败: 找不到ID={record_id}的记录")
        return False
    
    def clear_history(self):
        """
        清空所有历史记录
        :return: 是否清空成功
        """
        with self.lock:
            try:
                # 写入空列表
                with open(self.history_file, 'w', encoding='utf-8') as f:
                    json.dump([], f)
                
                print("已清空所有历史记录")
                return True
            except Exception as e:
                print(f"清空历史记录失败: {str(e)}")
                return False
    
    def _generate_id(self):
        """
        生成唯一ID
        :return: 唯一ID
        """
        # 使用时间戳作为ID
        return f"record_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

# 简单测试
if __name__ == "__main__":
    history_manager = HistoryManager()
    
    # 添加测试记录
    test_record_id = history_manager.add_record(
        "test_image.png",
        {"answer": "测试答案", "timestamp": "2023-01-01 12:00:00"}
    )
    
    # 获取所有记录
    all_records = history_manager.get_all_records()
    print(f"所有记录: {json.dumps(all_records, indent=2, ensure_ascii=False)}")
    
    # 获取单条记录
    record = history_manager.get_record(test_record_id)
    print(f"获取记录: {json.dumps(record, indent=2, ensure_ascii=False)}")
    
    # 删除记录
    history_manager.delete_record(test_record_id)
    
    # 验证删除成功
    all_records = history_manager.get_all_records()
    print(f"删除后记录: {json.dumps(all_records, indent=2, ensure_ascii=False)}") 