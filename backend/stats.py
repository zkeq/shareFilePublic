from typing import Dict
from fastapi import HTTPException
from db import redis_client

def get_stats_key(hash_value: str) -> str:
    """获取统计数据的Redis键名"""
    return f"stats:{hash_value}"

def init_stats(hash_value: str) -> None:
    """初始化统计数据"""
    stats_key = get_stats_key(hash_value)
    if not redis_client.exists(stats_key):
        redis_client.hmset(stats_key, {
            "views": 0,
            "downloads": 0
        })

def get_stats(hash_value: str) -> Dict[str, int]:
    """获取统计数据"""
    stats_key = get_stats_key(hash_value)
    if not redis_client.exists(stats_key):
        raise HTTPException(status_code=404, detail="统计数据不存在")
    
    try:
        stats = redis_client.hgetall(stats_key)
        return {
            "views": int(stats.get("views", 0)),
            "downloads": int(stats.get("downloads", 0))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="获取统计数据失败")

def increment_views(hash_value: str) -> Dict[str, int]:
    """增加访问量"""
    stats_key = get_stats_key(hash_value)
    if not redis_client.exists(stats_key):
        init_stats(hash_value)
    
    try:
        # 原子性地增加访问量
        redis_client.hincrby(stats_key, "views", 1)
        return get_stats(hash_value)
    except Exception as e:
        raise HTTPException(status_code=500, detail="更新访问量失败")

def increment_downloads(hash_value: str) -> Dict[str, int]:
    """增加下载量"""
    stats_key = get_stats_key(hash_value)
    if not redis_client.exists(stats_key):
        init_stats(hash_value)
    
    try:
        # 原子性地增加下载量
        redis_client.hincrby(stats_key, "downloads", 1)
        return get_stats(hash_value)
    except Exception as e:
        raise HTTPException(status_code=500, detail="更新下载量失败")