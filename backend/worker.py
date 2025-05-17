import json
import time
from typing import Dict
from db import redis_client
from tasks import update_task_status
from dogecloud import dogecloud_api
from urllib.parse import quote

def submit_video_task(url: str) -> Dict:
    """提交视频任务到多吉云"""
    # 对URL进行编码处理
    encoded_url = quote(url, safe=':/?=&')
    params = {
        'url': encoded_url,
        'vn': '',  # 视频名称，可选
        'cid': 0,  # 分类ID，可选
        'policy': json.dumps({'custom': False}),  # 转码策略，使用默认
        'tstart': 0,  # 开始时间，可选
        'tduration': 0,  # 时长，可选
        'rights_doc': 0,  # 版权文件，可选
        'subtitle': '',  # 字幕，可选
        'callbackString': encoded_url  # 回调参数，这里用URL作为标识
    }
    
    response = dogecloud_api('/console/vfetch/add.json', params)
    if response.get('code') != 200:
        raise Exception(f"提交视频任务失败: {response.get('msg')}")
    
    return response.get('data')

def query_video_task(hash: str) -> Dict:
    """查询视频任务状态"""
    params = {'hash': hash}
    response = dogecloud_api('/console/vfetch/query.json', params)
    
    if response.get('code') != 200:
        raise Exception(f"查询视频任务状态失败: {response.get('msg')}")
    
    return response.get('data')

def process_video_tasks():
    """处理视频任务队列"""
    while True:
        # 从Redis队列中获取任务
        task_data = redis_client.blpop('video_tasks')
        
        # 解析任务数据
        _, task_json = task_data
        task = json.loads(task_json)
        task_hash = task['hash']
        url = task['url']
        
        try:
            # 提交视频任务到多吉云
            video_task = submit_video_task(url)
            dogecloud_hash = video_task['hash']
            
            # 轮询任务状态
            while True:
                task_status = query_video_task(dogecloud_hash)
                print(f"任务 {task_hash} 当前状态: {task_status}")
                
                if task_status.get('status') == 'done':
                    # 任务完成，获取vcode
                    vcode = task_status.get('vcode')
                    print(f"任务 {task_hash} 完成，获取到的完整状态: {task_status}")
                    
                    if not vcode:
                        print(f"警告：任务 {task_hash} 完成但vcode为空，继续等待...")
                        time.sleep(5)
                        continue
                    
                    # 只有在获取到有效的vcode时才更新状态并退出循环
                    update_task_status(task_hash, vcode)
                    print(f"任务 {task_hash} 状态已更新，vcode: {vcode}")
                    break
                elif task_status.get('status') == 'error':
                    # 任务失败
                    error_msg = task_status.get('error')
                    print(f"任务 {task_hash} 失败，错误信息: {error_msg}")
                    raise Exception(f"视频任务处理失败: {error_msg}")
                
                # 等待一段时间后再次查询
                time.sleep(5)
                
        except Exception as e:
            print(f"处理任务 {task_hash} 时出错: {str(e)}")
            # 可以在这里添加错误处理逻辑，比如将失败的任务记录到日志或重新入队

if __name__ == '__main__':
    print("开始处理视频任务队列...")
    process_video_tasks()