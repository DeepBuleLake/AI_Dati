"""
识别模块 - 负责调用Coze API进行OCR识别和答案生成
整合了原有的AIdati.py代码
"""
import os
import sys
import json
import requests
from datetime import datetime
from threading import Thread

# 导入配置
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import AUTH_TOKEN, BOT_ID, WORKFLOW_ID

class RecognitionManager:
    """识别管理器 - 负责调用Coze API进行识别"""
    
    def __init__(self, callback=None):
        """
        初始化识别管理器
        :param callback: 识别完成后的回调函数，接收识别结果参数
        """
        self.callback = callback
        self.processing = False
    
    def process_image(self, image_path, async_mode=False):
        """
        处理图片，调用Coze API进行识别
        :param image_path: 图片路径
        :param async_mode: 是否异步处理
        :return: 同步模式下返回识别结果，异步模式下返回None
        """
        if not os.path.exists(image_path):
            error_msg = f"图片文件不存在: {image_path}"
            print(error_msg)
            return {"error": error_msg}
        
        if self.processing:
            print("已有识别任务正在进行中，请稍后再试")
            return {"error": "已有识别任务正在进行中，请稍后再试"}
        
        # 标记处理状态
        self.processing = True
        
        if async_mode:
            # 异步处理
            thread = Thread(target=self._process_task, args=(image_path,))
            thread.daemon = True
            thread.start()
            return None
        else:
            # 同步处理
            return self._process_task(image_path)
    
    def _process_task(self, image_path):
        """
        执行识别任务
        :param image_path: 图片路径
        :return: 识别结果
        """
        try:
            # 1. 上传文件
            print(f"开始上传图片: {image_path}")
            file_id = self.upload_file(image_path)
            
            if not file_id:
                error_result = {"error": "文件上传失败"}
                if self.callback:
                    self.callback(error_result)
                self.processing = False
                return error_result
            
            # 2. 执行工作流
            print(f"开始执行工作流, 文件ID: {file_id}")
            result = self.execute_workflow(file_id)
            
            # 3. 处理结果
            if result:
                # 提取有用的信息
                processed_result = self.process_result(result)
                print("识别完成!")
                
                # 执行回调
                if self.callback:
                    self.callback(processed_result)
                
                self.processing = False
                return processed_result
            else:
                error_result = {"error": "识别失败，工作流执行出错"}
                if self.callback:
                    self.callback(error_result)
                self.processing = False
                return error_result
                
        except Exception as e:
            error_msg = f"识别过程出错: {str(e)}"
            print(error_msg)
            error_result = {"error": error_msg}
            
            if self.callback:
                self.callback(error_result)
            
            self.processing = False
            return error_result
    
    def upload_file(self, file_path):
        """
        上传文件到Coze平台
        :param file_path: 文件路径
        :return: 成功返回file_id，失败返回None
        """
        url = "https://api.coze.cn/v1/files/upload"
        headers = {"Authorization": AUTH_TOKEN}
        
        try:
            # 准备上传数据
            file_name = os.path.basename(file_path)
            with open(file_path, 'rb') as f:
                files = {'file': (file_name, f)}
                
                # 发送请求
                response = requests.post(url, headers=headers, files=files)
                result = response.json()

                # 调试输出
                self._print_debug_info("文件上传响应", result)

                # 处理结果
                if response.status_code == 200 and result.get('code') == 0:
                    return result['data']['id']
                else:
                    print(f"上传失败: {result.get('msg')}")
                    return None

        except Exception as e:
            print(f"上传异常: {str(e)}")
            return None
    
    def execute_workflow(self, file_id, user_context=None):
        """
        执行工作流
        :param file_id: 上传文件的ID
        :param user_context: 用户上下文信息
        :return: 工作流执行结果
        """
        url = "https://api.coze.cn/v1/workflow/run"
        headers = {"Authorization": AUTH_TOKEN}
        
        # 参数构造
        base_params = {
            "workflow_id": WORKFLOW_ID,
            "bot_id": BOT_ID,
            "is_async": False  # 同步执行
        }

        # 文件参数处理
        file_params = {
            "input": json.dumps({"file_id": file_id})
        }

        # 其他参数
        user_params = {
            "user_id": "user_" + datetime.now().strftime("%Y%m%d%H%M%S")
        }

        # 合并参数
        parameters = {**file_params, **user_params}
        if user_context:
            parameters.update(user_context)
        
        payload = {**base_params, "parameters": parameters}
        
        try:
            # 调试输出
            self._print_debug_info("工作流请求参数", payload)

            # 发送请求
            response = requests.post(url, headers=headers, json=payload)
            result = response.json()
            
            # 调试输出
            self._print_debug_info("工作流响应", result)

            # 结果处理
            if result.get('code') == 0:
                # 解析双重序列化的结果
                try:
                    return json.loads(result['data'])
                except json.JSONDecodeError:
                    return result['data']  # 兼容非JSON响应
            else:
                self._handle_workflow_errors(result)
                return None

        except Exception as e:
            print(f"请求异常: {str(e)}")
            return None
    
    def process_result(self, result):
        """
        处理工作流返回的结果，提取有用信息
        :param result: 工作流返回的原始结果
        :return: 处理后的结果
        """
        processed = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "raw": result
        }
        
        # 提取output部分
        if isinstance(result, dict) and "output" in result:
            processed["answer"] = result["output"]
        else:
            processed["answer"] = "无法解析答案"
        
        # 提取debug_url
        if isinstance(result, dict) and "debug_url" in result:
            processed["debug_url"] = result["debug_url"]
        
        return processed
    
    def _print_debug_info(self, title, data):
        """打印调试信息"""
        print(f"\n=== {title} ===")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    
    def _handle_workflow_errors(self, result):
        """工作流错误处理"""
        error_code = result.get('code')
        error_msg = result.get('msg', '')
        
        error_map = {
            4000: "参数校验失败：请检查参数类型和必填项",
            4001: "业务逻辑错误：工作流内部执行失败",
            403: "权限不足：检查令牌权限和工作流发布状态",
            404: "资源不存在：检查workflow_id是否正确",
            500: "服务器内部错误：建议重试或联系支持"
        }
        
        print(f"错误代码 {error_code}: {error_map.get(error_code, '未知错误')}")
        print(f"详细原因: {error_msg}")

# 简单测试
if __name__ == "__main__":
    def on_recognition(result):
        print(f"\n识别结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # 替换为实际的图片路径
    test_image = "../data/screenshots/test.png"
    if not os.path.exists(test_image):
        print(f"测试图片不存在: {test_image}")
        sys.exit(1)
    
    recognizer = RecognitionManager(callback=on_recognition)
    result = recognizer.process_image(test_image)
    
    print("测试完成") 