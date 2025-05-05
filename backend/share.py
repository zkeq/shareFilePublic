import os
import json
import hashlib
from typing import Dict, Any, List
from fastapi import HTTPException

# 确保share目录存在
SHARE_DIR = 'share'
os.makedirs(SHARE_DIR, exist_ok=True)

def generate_hash() -> str:
    """生成8位MD5哈希值"""
    # 使用当前时间戳作为输入生成哈希值
    timestamp = str(os.urandom(16))
    md5_hash = hashlib.md5(timestamp.encode()).hexdigest()
    return md5_hash[:8]  # 返回前8位

def save_share_list(share_list: List[Any]) -> str:
    """保存分享列表并返回哈希值"""
    # 将列表序列化为JSON字符串并计算MD5
    json_str = json.dumps(share_list, ensure_ascii=False, sort_keys=True)
    hash_value = hashlib.md5(json_str.encode()).hexdigest()[:8]
    
    # 构建文件路径
    file_path = os.path.join(SHARE_DIR, f"{hash_value}.json")
    
    # 将分享列表保存到文件
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(share_list, f, ensure_ascii=False, indent=2)
    
    return hash_value

def get_share_list(hash_value: str) -> List[Any]:
    """根据哈希值获取分享列表"""
    # 构建文件路径
    file_path = os.path.join(SHARE_DIR, f"{hash_value}.json")
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="分享列表不存在")
    
    # 读取并返回分享列表
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="分享列表文件损坏")