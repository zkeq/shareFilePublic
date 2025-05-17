import json
import os
import hashlib
from typing import Dict, Optional
from fastapi import HTTPException
from db import redis_client

# 确保tasks目录存在
TASKS_DIR = 'tasks'
os.makedirs(TASKS_DIR, exist_ok=True)

def generate_task_hash(url: str) -> str:
    """根据URL生成任务哈希值"""
    return hashlib.md5(url.encode()).hexdigest()[:8]

def save_task_info(task_hash: str, url: str, status: str = '上传中', vcode: str = '') -> None:
    """保存任务信息到JSON文件"""
    task_info = {
        'url': url,
        'status': status,
        'vcode': vcode
    }
    
    file_path = os.path.join(TASKS_DIR, f"{task_hash}.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(task_info, f, ensure_ascii=False, indent=2)

def get_task_info(task_hash: str) -> Dict:
    """获取任务信息"""
    file_path = os.path.join(TASKS_DIR, f"{task_hash}.json")
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="任务不存在")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="任务信息文件损坏")

def submit_task(url: str) -> Dict:
    """提交新任务到队列"""
    task_hash = generate_task_hash(url)
    
    # 检查任务是否已存在
    try:
        existing_task = get_task_info(task_hash)
        return {
            'hash': task_hash,
            'status': existing_task['status'],
            'message': '任务已存在'
        }
    except HTTPException:
        pass
    
    # 保存任务信息
    save_task_info(task_hash, url)
    
    # 将任务添加到Redis队列
    redis_client.rpush('video_tasks', json.dumps({
        'hash': task_hash,
        'url': url
    }))
    
    return {
        'hash': task_hash,
        'status': '上传中',
        'message': '任务已提交'
    }

def update_task_status(task_hash: str, vcode: str) -> Dict:
    """更新任务状态为已上传，并设置vcode"""
    try:
        task_info = get_task_info(task_hash)
        if task_info['status'] == '已上传':
            return {
                'hash': task_hash,
                'status': '已上传',
                'vcode': task_info['vcode'],
                'message': '任务已完成'
            }
        
        # 更新任务状态和vcode
        save_task_info(task_hash, task_info['url'], '已上传', vcode)
        
        return {
            'hash': task_hash,
            'status': '已上传',
            'vcode': vcode,
            'message': '任务状态已更新'
        }
    except HTTPException as e:
        raise e