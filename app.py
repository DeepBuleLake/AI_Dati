"""
智能答题助手(DatiAI) - 主程序
提供Web界面和核心功能入口
"""
import os
import sys
import json
import time
from datetime import datetime
from threading import Thread, Event
from flask import Flask, render_template, request, jsonify, send_from_directory

# 导入配置和模块
from config import (
    APP_NAME, APP_VERSION, DEBUG, 
    HOST, PORT, SCREENSHOT_DIR, STATIC_DIR
)
from modules.screenshot import ScreenshotManager
from modules.recognition import RecognitionManager
from modules.history import HistoryManager
from modules.anti_detect import AntiDetectManager

# 初始化Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['JSON_AS_ASCII'] = False  # 确保中文正确显示

# 全局状态
global_state = {
    "is_running": False,
    "current_task": None,
    "last_screenshot": None,
    "last_result": None,
    "status_messages": []
}

# 初始化各模块
screenshot_manager = None
recognition_manager = None
history_manager = None
anti_detect_manager = None

# 状态管理
def add_status_message(message):
    """添加状态消息"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    global_state["status_messages"].append({
        "time": timestamp,
        "message": message
    })
    # 只保留最近的50条消息
    if len(global_state["status_messages"]) > 50:
        global_state["status_messages"] = global_state["status_messages"][-50:]
    print(f"[{timestamp}] {message}")

# 截图回调
def on_screenshot(image_path):
    """截图完成后的回调"""
    add_status_message(f"截图已保存: {os.path.basename(image_path)}")
    global_state["last_screenshot"] = image_path
    
    # 自动开始识别
    if recognition_manager and not recognition_manager.processing:
        recognition_manager.process_image(image_path, async_mode=True)
        add_status_message(f"开始识别图片: {os.path.basename(image_path)}")
    else:
        add_status_message("识别服务不可用或正在处理中")

# 识别回调
def on_recognition(result):
    """识别完成后的回调"""
    if "error" in result:
        add_status_message(f"识别失败: {result['error']}")
    else:
        add_status_message("识别完成!")
        
        # 更新全局状态
        global_state["last_result"] = result
        
        # 添加到历史记录
        if history_manager and global_state["last_screenshot"]:
            history_manager.add_record(global_state["last_screenshot"], result)
            add_status_message("已添加到历史记录")

# 反检测回调
def on_detection(detection_type):
    """检测到截图行为后的回调"""
    add_status_message(f"检测到可疑活动: {detection_type}")

# 路由定义
@app.route('/')
def index():
    """首页"""
    return render_template('index.html', app_name=APP_NAME, app_version=APP_VERSION)

@app.route('/api/status')
def get_status():
    """获取当前状态"""
    return jsonify({
        "is_running": global_state["is_running"],
        "current_task": global_state["current_task"],
        "last_screenshot": os.path.basename(global_state["last_screenshot"]) if global_state["last_screenshot"] else None,
        "last_result": global_state["last_result"],
        "status_messages": global_state["status_messages"][-10:],  # 只返回最近10条消息
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route('/api/screenshot', methods=['POST'])
def take_screenshot():
    """手动触发截图"""
    if screenshot_manager:
        filepath = screenshot_manager.take_screenshot()
        if filepath:
            return jsonify({"success": True, "filepath": os.path.basename(filepath)})
    return jsonify({"success": False, "error": "截图服务不可用"})

@app.route('/api/recognize', methods=['POST'])
def recognize_image():
    """手动触发识别"""
    if not recognition_manager:
        return jsonify({"success": False, "error": "识别服务不可用"})
    
    if recognition_manager.processing:
        return jsonify({"success": False, "error": "已有识别任务正在进行中"})
    
    image_path = global_state["last_screenshot"]
    if not image_path or not os.path.exists(image_path):
        return jsonify({"success": False, "error": "没有可用的截图"})
    
    # 开始识别
    recognition_manager.process_image(image_path, async_mode=True)
    add_status_message(f"开始识别图片: {os.path.basename(image_path)}")
    
    return jsonify({"success": True})

@app.route('/api/history')
def get_history():
    """获取历史记录"""
    if not history_manager:
        return jsonify({"success": False, "error": "历史记录服务不可用"})
    
    records = history_manager.get_all_records()
    
    # 处理记录，确保JSON安全
    for record in records:
        # 只保留文件名而非完整路径
        if "image_path" in record:
            record["image_path"] = os.path.basename(record["image_path"])
    
    return jsonify({"success": True, "records": records})

@app.route('/api/history/<record_id>', methods=['DELETE'])
def delete_history(record_id):
    """删除历史记录"""
    if not history_manager:
        return jsonify({"success": False, "error": "历史记录服务不可用"})
    
    success = history_manager.delete_record(record_id)
    return jsonify({"success": success})

@app.route('/api/history/clear', methods=['POST'])
def clear_history():
    """清空历史记录"""
    if not history_manager:
        return jsonify({"success": False, "error": "历史记录服务不可用"})
    
    success = history_manager.clear_history()
    return jsonify({"success": success})

@app.route('/screenshots/<filename>')
def serve_screenshot(filename):
    """提供截图文件访问"""
    return send_from_directory(SCREENSHOT_DIR, filename)

@app.route('/api/start', methods=['POST'])
def start_service():
    """启动服务"""
    global screenshot_manager, recognition_manager, history_manager, anti_detect_manager
    global global_state
    
    if global_state["is_running"]:
        return jsonify({"success": False, "error": "服务已经在运行中"})
    
    try:
        # 初始化各模块
        if not screenshot_manager:
            screenshot_manager = ScreenshotManager(callback=on_screenshot)
        
        if not recognition_manager:
            recognition_manager = RecognitionManager(callback=on_recognition)
        
        if not history_manager:
            history_manager = HistoryManager()
        
        if not anti_detect_manager:
            anti_detect_manager = AntiDetectManager(callback=on_detection)
        
        # 启动服务
        screenshot_manager.start()
        anti_detect_manager.start()
        
        global_state["is_running"] = True
        add_status_message("服务已启动")
        
        return jsonify({"success": True})
    except Exception as e:
        error_msg = f"启动服务失败: {str(e)}"
        add_status_message(error_msg)
        return jsonify({"success": False, "error": error_msg})

@app.route('/api/stop', methods=['POST'])
def stop_service():
    """停止服务"""
    global screenshot_manager, anti_detect_manager
    global global_state
    
    if not global_state["is_running"]:
        return jsonify({"success": False, "error": "服务未在运行"})
    
    try:
        # 停止服务
        if screenshot_manager:
            screenshot_manager.stop()
        
        if anti_detect_manager:
            anti_detect_manager.stop()
        
        global_state["is_running"] = False
        add_status_message("服务已停止")
        
        return jsonify({"success": True})
    except Exception as e:
        error_msg = f"停止服务失败: {str(e)}"
        add_status_message(error_msg)
        return jsonify({"success": False, "error": error_msg})

# 主函数
def main():
    """主函数"""
    add_status_message(f"启动 {APP_NAME} v{APP_VERSION}")
    app.run(host=HOST, port=PORT, debug=DEBUG, threaded=True)

if __name__ == "__main__":
    main() 