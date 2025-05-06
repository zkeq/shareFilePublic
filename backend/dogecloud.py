# coding: utf-8
import requests
import redis
import datetime
import os

from hashlib import sha1
import hmac
import requests
import json
import urllib

import time

def dogecloud_api(api_path, data, json_mode=False):

    # 这里替换为你的多吉云永久 AccessKey 和 SecretKey，可在用户中心 - 密钥管理中查看
    # 请勿在客户端暴露 AccessKey 和 SecretKey，否则恶意用户将获得账号完全控制权
    access_key = os.environ.get('DOGECLOUD_ACCESS_KEY')
    secret_key = os.environ.get('DOGECLOUD_SECRET_KEY')
    
    if not access_key or not secret_key:
        raise ValueError("缺少多吉云API凭证，请设置环境变量DOGECLOUD_ACCESS_KEY和DOGECLOUD_SECRET_KEY")

    body = ''
    mime = ''
    if json_mode:
        body = json.dumps(data)
        mime = 'application/json'
    else:
        body = urllib.parse.urlencode(data)  # Python 2 可以直接用 urllib.urlencode
        mime = 'application/x-www-form-urlencoded'
    sign_str = api_path + "\n" + body
    signed_data = hmac.new(secret_key.encode('utf-8'), sign_str.encode('utf-8'), sha1)
    sign = signed_data.digest().hex()
    authorization = 'TOKEN ' + access_key + ':' + sign
    response = requests.post('https://api.dogecloud.com' + api_path, data=body, headers={
        'Authorization': authorization,
        'Content-Type': mime
    })
    return response.json()

def get_share_bucket_count():
    """
    查询 share 桶最近3天的文件数量
    返回: API 响应的 JSON 数据
    """
    # 获取当前日期
    today = datetime.datetime.now()
    # 计算3天前的日期
    three_days_ago = today - datetime.timedelta(days=2)
    
    # 格式化日期为 YYYY-MM-DD 格式
    end_date = today.strftime('%Y-%m-%d')
    start_date = three_days_ago.strftime('%Y-%m-%d')
    
    # 准备请求参数
    params = {
        'bucket': 'share',
        'start_date': start_date,
        'end_date': end_date,
        'granularity': 'day'
    }
    
    # 调用 API
    return dogecloud_api('/oss/stat/count.json', params)

def get_share_bucket_storage():
    """
    查询 share 桶最近3天的存储容量
    返回: API 响应的 JSON 数据，存储容量单位为字节
    """
    # 获取当前日期
    today = datetime.datetime.now()
    # 计算3天前的日期
    three_days_ago = today - datetime.timedelta(days=2)
    
    # 格式化日期为 YYYY-MM-DD 格式
    end_date = today.strftime('%Y-%m-%d')
    start_date = three_days_ago.strftime('%Y-%m-%d')
    
    # 准备请求参数
    params = {
        'bucket': 'share',
        'start_date': start_date,
        'end_date': end_date,
        'granularity': 'day'
    }
    
    # 调用 API
    return dogecloud_api('/oss/stat/space.json', params)

def get_share_bucket_traffic():
    """
    查询 share 桶从2025年5月5日到今天的流量数据
    返回: API 响应的 JSON 数据，流量单位为字节
    """
    # 获取当前日期
    today = datetime.datetime.now()
    # 设置开始日期为2025年5月5日
    start_date = '2025-05-05'
    
    # 格式化结束日期为 YYYY-MM-DD 格式
    end_date = today.strftime('%Y-%m-%d')
    
    # 准备请求参数
    params = {
        'bucket': 'share',
        'start_date': start_date,
        'end_date': end_date,
        'granularity': 'day'  # 使用按天统计的粒度
    }
    
    # 调用 API
    return dogecloud_api('/oss/stat/traffic.json', params)

def get_share_bucket_stats():
    """
    获取share桶的所有统计数据，包括文件数量、存储容量和流量数据
    数据会被缓存1小时
    返回: 包含三个统计数据的字典
    """
    from db import redis_client
    import json
    
    # 缓存键名
    cache_key = 'share_bucket_stats'
    
    # 尝试从缓存获取数据
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return json.loads(cached_data)
    
    # 如果缓存不存在，则获取新数据
    stats = {
        'count': get_share_bucket_count(),
        'storage': get_share_bucket_storage(),
        'traffic': get_share_bucket_traffic()
    }
    
    # 将数据存入缓存，设置24小时过期时间
    redis_client.setex(cache_key, 3600 * 24, json.dumps(stats))
    
    return stats

def get_upload_token():
    """
    获取上传文件的临时密钥，使用当前日期作为文件夹前缀的上传权限
    :return: 临时密钥信息
    """
    # 获取当前日期作为文件夹前缀
    today = datetime.datetime.now()
    date_prefix = today.strftime('%Y-%m-%d')
    
    data = {
        "channel": "OSS_UPLOAD",
        "scopes": [f"share:{date_prefix}/*"]
    }
    
    # 调用多吉云API获取临时密钥
    response = dogecloud_api('/auth/tmp_token.json', data, json_mode=True)
    
    if response.get('code') != 200:
        raise Exception(f"获取上传凭证失败: {response.get('msg')}")
    
    return response.get('data')

if __name__ == '__main__':
    # # 获取并打印所有统计数据
    # print(get_share_bucket_stats())
    print(get_share_bucket_storage())