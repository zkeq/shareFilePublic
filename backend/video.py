# coding: utf-8

from dogecloud import dogecloud_api
from typing import Dict

def get_video_info(vcode: str) -> Dict:
    """获取视频详细信息"""
    params = {'vcode': vcode}
    response = dogecloud_api('/video/info.json', params)
    
    if response.get('code') != 200:
        raise Exception(f"获取视频信息失败: {response.get('msg')}")
    
    return response.get('data')

