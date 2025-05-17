// 定义API基础URL
// export const baseURL = 'https://share-api.onmicrosoft.cn';

export const baseURL = 'http://127.0.0.1:8000';

// API路径
export const API = {
  // 获取存储桶统计数据
  getBucketStats: `${baseURL}/public/info`,
  // 获取上传凭证
  getUploadToken: `${baseURL}/upload/token`,
  // 提交分享列表
  submitShareList: `${baseURL}/share/submit`,
  // 获取分享列表
  getShareList: (hash) => `${baseURL}/share/${hash}`,
  // 获取分享统计
  getShareStats: (hash) => `${baseURL}/share/stats/${hash}`,
  // 增加访问量
  incrementViews: (hash) => `${baseURL}/share/views/${hash}`,
  // 增加下载量
  incrementDownloads: (hash) => `${baseURL}/share/downloads/${hash}`
};