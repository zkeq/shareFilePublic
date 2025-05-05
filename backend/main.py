from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dogecloud import get_share_bucket_stats, get_upload_token
from share import save_share_list, get_share_list
from stats import get_stats as get_file_stats, increment_views, increment_downloads
from typing import Dict, Any, List

app = FastAPI()

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置为具体的域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)

@app.get("/")
def read_root():
    return {"message": "Welcome to ShareFile API"}

@app.get("/public/info")
def get_stats():
    """获取存储桶统计数据"""
    return get_share_bucket_stats()

@app.post("/share/submit")
def submit_share_list(share_list: List[Any]):
    """提交分享列表"""
    hash_value = save_share_list(share_list)
    return {"hash": hash_value}

@app.get("/share/{hash_value}")
def get_share_list_by_hash(hash_value: str):
    """获取分享列表"""
    return get_share_list(hash_value)

@app.get("/share/stats/{hash_value}")
def get_share_views(hash_value: str):
    """获取分享链接的访问量"""
    return get_file_stats(hash_value)

@app.post("/share/views/{hash_value}")
def increment_share_views(hash_value: str):
    """增加分享链接的访问量"""
    return increment_views(hash_value)

@app.post("/share/downloads/{hash_value}")
def increment_share_downloads(hash_value: str):
    """增加分享链接的下载量"""
    return increment_downloads(hash_value)

@app.post("/upload/token")
def get_upload_auth():
    """获取上传凭证，固定使用share作用域"""
    try:
        token_data = get_upload_token()
        return token_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)