<template>
  <div class="flex flex-col items-center p-5 space-y-6 bg-[#f5f5f5] min-h-screen pt-10">
    <div class="max-w-[840px] w-full border border-gray-200 rounded-xl bg-white p-4 sm:p-6 space-y-4 sm:space-y-6">
      <h1 class="text-xl sm:text-2xl text-gray-800 text-center">Zkeq 和 Ta 的朋友们 的 文件分享服务站</h1>
      <p class="text-gray-600 text-xs sm:text-sm pb-2 sm:pb-4">
        <span class="text-blue-500">Tips：</span>
        本工具存在的作用就是用来传输一些文件 可以代替U盘或者微信来使用 会很方便
      </p>
      <a-upload-dragger
        v-model:fileList="uploadingList"
        name="file"
        :multiple="true"
        :customRequest="initS3Upload"
        :showUploadList="true"
        @change="handleChange"
        @drop="handleDrop"
        class="w-full transition-all duration-300 hover:border-blue-400"
      >
        <p class="text-blue-500 text-4xl mb-4">
          <inbox-outlined></inbox-outlined>
        </p>
        <p class="text-base text-gray-800 mb-2">点击或拖拽文件到此区域上传</p>
        <p class="text-sm text-gray-600">
          支持单个或批量上传，单个文件最大支持100GB，再大的话其实也可以上传
        </p>
      </a-upload-dragger>
  
      
    </div>
    
    <!-- 添加统计卡片 -->
    <div class="max-w-[840px] w-full mt-6">
      <a-row :gutter="[16, 16]">
        <a-col :xs="12" :sm="12" :md="6">
          <stat-card 
            type="files" 
            :title="showGlobal.files ? '全站文件个数' : '我的文件个数'" 
            :value="showGlobal.files ? globalStats.totalFiles : fileStats.totalFiles"
            suffix="个"
            @click="toggleGlobal('files')"
            class="cursor-pointer"
          />
        </a-col>
        <a-col :xs="12" :sm="12" :md="6">
          <stat-card 
            type="size" 
            :title="showGlobal.size ? '全站文件大小' : '我的文件大小'" 
            :value="showGlobal.size ? globalStats.totalSize : fileStats.totalSize"
            suffix="MB"
            :precision="2"
            @click="toggleGlobal('size')"
            class="cursor-pointer"
          />
        </a-col>
        <a-col :xs="12" :sm="12" :md="6">
          <stat-card 
            type="speed" 
            title="当前上传速率" 
            :value="fileStats.uploadSpeed" 
            :precision="2" 
            suffix="MB/s" 
          />
        </a-col>
        <a-col :xs="12" :sm="12" :md="6">
          <stat-card 
            type="traffic" 
            title="全站下载流量" 
            :value="globalStats.totalTraffic" 
            :precision="2" 
            suffix="GB" 
          />
        </a-col>
      </a-row>
    </div>

    <!-- 添加文件列表区域 -->
    <div class="max-w-[840px] w-full bg-white rounded-xl p-4 sm:p-6">
      <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-4 sm:mb-6 space-y-3 sm:space-y-0">
        <h2 class="text-lg sm:text-xl font-medium text-gray-800">文件列表</h2>
        <div class="flex flex-wrap gap-2 sm:space-x-3">
          <a-button 
            :type="isMultiSelect ? 'primary' : 'default'"
            @click="toggleMultiSelect"
            class="flex items-center text-xs sm:text-sm"
            :size="isMobile ? 'small' : 'middle'"
          >
            <template #icon>
              <check-square-outlined :class="isMultiSelect ? 'text-white' : 'text-gray-600'" />
            </template>
            <span class="ml-1">{{ isMultiSelect ? '取消多选' : '多选' }}</span>
          </a-button>
          <a-button 
            type="primary"
            @click="batchShare"
            :disabled="selectedFiles.length === 0"
            class="flex items-center text-xs sm:text-sm"
            :size="isMobile ? 'small' : 'middle'"
          >
            <template #icon>
              <share-alt-outlined />
            </template>
            <span class="ml-1">批量分享{{ selectedFiles.length ? ` (${selectedFiles.length})` : '' }}</span>
          </a-button>
          <a-button 
            type="primary"
            @click="batchDownload"
            :disabled="selectedFiles.length === 0"
            class="flex items-center text-xs sm:text-sm"
            :size="isMobile ? 'small' : 'middle'"
          >
            <template #icon>
              <download-outlined />
            </template>
            <span class="ml-1">批量下载{{ selectedFiles.length ? ` (${selectedFiles.length})` : '' }}</span>
          </a-button>
        </div>
      </div>
      <div v-if="fileList.length" class="space-y-4">
        <div 
          v-for="file in fileList" 
          :key="file.name" 
          class="flex items-center"
          @click="handleItemClick(file)"
        >
          <a-checkbox 
            v-if="isMultiSelect"
            v-model:checked="file.selected"
            class="mr-4"
            @click.stop
          />
          <div class="flex-1" :class="{'opacity-75': isMultiSelect && !file.selected}">
            <file-list-item
              :file="file"
              :is-selectable="isMultiSelect"
              mode="home"
            />
          </div>
        </div>
      </div>
      <a-empty v-else description="暂无文件" />
    </div>
  </div>
</template>

<script setup lang="ts">
// 导入相关依赖
import { ref, computed, onMounted, watch, onUnmounted, h } from 'vue';
import { message, Modal } from 'ant-design-vue';
import type { UploadChangeParam, UploadProps } from 'ant-design-vue';
import axios from 'axios';
import CryptoJS from 'crypto-js';

// 导入组件
import { 
  InboxOutlined, 
  CheckSquareOutlined, 
  DownloadOutlined,
  ShareAltOutlined 
} from '@ant-design/icons-vue';
import StatCard from '../components/StatCard.vue';
import FileListItem from '../components/FileListItem.vue';

// 导入工具和配置
import { API } from '../config.js';
import { formatFileSize } from '../utils/format';

// 声明 AWS 全局变量
declare const AWS: any;

// 移动端检测
const isMobile = computed(() => {
  return window.innerWidth <= 640; // 使用 sm 断点 (640px) 作为移动端判断标准
});

// 状态定义
const fileList = ref<any[]>([]); // 永久保存的文件列表
const uploadingList = ref<any[]>([]); // 临时上传列表
const isMultiSelect = ref(false);
const showGlobal = ref({
  files: false,
  size: false
});

// 从localStorage加载文件列表
const loadFileList = () => {
  try {
    const savedFiles = localStorage.getItem('uploadedFiles');
    if (savedFiles) {
      fileList.value = JSON.parse(savedFiles);
    }
  } catch (error) {
    console.error('加载文件列表失败:', error);
  }
};

// 保存文件列表到localStorage
const saveFileList = () => {
  try {
    // 创建一个不包含 selected 状态的文件列表副本
    const cleanFileList = fileList.value.map(file => {
      const cleanFile = { ...file };
      delete cleanFile.selected;
      return cleanFile;
    });
    localStorage.setItem('uploadedFiles', JSON.stringify(cleanFileList));
  } catch (error) {
    console.error('保存文件列表失败:', error);
  }
};

// 监听文件列表变化
watch(fileList, () => {
  saveFileList();
}, { deep: true });

// 上传状态
const uploadStatus = ref({
  currentSpeed: 0,
  averageSpeed: 0,
  progress: 0,
  isUploading: false,
  // 记录每个文件的上传速度
  filesSpeeds: new Map()
});

// 全局统计数据
const globalStats = ref({
  totalFiles: 0,
  totalSize: "0 MB",
  totalTraffic: "0 GB"
});

// 计算属性
const selectedFiles = computed(() => fileList.value.filter(file => file.selected));

const fileStats = computed(() => {
  const totalSize = fileList.value.reduce((sum, file) => sum + (file.size || 0), 0);
  return {
    totalFiles: fileList.value.length,
    totalSize: formatFileSize(totalSize),
    uploadSpeed: uploadStatus.value.currentSpeed,
    usedTraffic: 1.25
  };
});

// 定义上传选项类型
interface UploadOptions {
  file: File;
  onProgress?: (event: { percent: number }) => void;
  onSuccess?: (response: any) => void;
  onError?: (error: any) => void;
}

// S3上传相关方法
const initS3Upload = async (options: any) => {
  const file = options.file;
  try {
    // 更新上传列表状态
    const uploadingFile = {
      uid: file.uid,
      name: file.name,
      status: 'uploading',
      percent: 0,
      size: file.size,
      type: file.type,
      selected: false
    };
    
    // 获取上传凭证
    const response = await axios.post(API.getUploadToken);
    const { Credentials, Buckets } = response.data;
    
    if (!Credentials || !Buckets || Buckets.length === 0) {
      throw new Error('获取上传凭证失败');
    }

    const bucket = Buckets[0]; // 使用第一个 bucket

    // 初始化S3实例
    const s3 = new AWS.S3({
      region: 'ap-beijing',
      endpoint: bucket.s3Endpoint,
      credentials: {
        accessKeyId: Credentials.accessKeyId,
        secretAccessKey: Credentials.secretAccessKey,
        sessionToken: Credentials.sessionToken
      },
      params: {
        Bucket: bucket.s3Bucket
      }
    });

    // 生成当前日期作为文件夹路径
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const datePath = `/${year}-${month}-${day}`;

    // 生成文件key，添加日期前缀，使用原始文件名+时间戳
    const timestamp = new Date().getTime();
    const originalName = file.name;
    const fileNameWithoutExt = originalName.substring(0, originalName.lastIndexOf('.')) || originalName;
    const fileExt = originalName.substring(originalName.lastIndexOf('.')) || '';
    const key = `${datePath}/${fileNameWithoutExt}-${timestamp}${fileExt}`;

    // 记录上传开始时间
    const startTime = new Date().getTime();
    let lastTime = startTime;
    let lastLoaded = 0;

    // 开始上传
    uploadStatus.value.isUploading = true;
    const upload = s3.upload({
      Key: key,
      Body: file,
      ContentType: file.type
    });

    // 监听上传进度
    upload.on('httpUploadProgress', (evt: any) => {
      const percent = ((evt.loaded * 100) / evt.total).toFixed(2);
      const elapsedTime = (new Date().getTime() - startTime) / 1000;
      const fromLastTime = (new Date().getTime() - lastTime) / 1000;

      if (fromLastTime > 2) { // 增加更新间隔到2秒
        const fileSpeed = Number(((evt.loaded - lastLoaded) / fromLastTime / 1024 / 1024).toFixed(2));
        uploadStatus.value.filesSpeeds.set(file.uid, fileSpeed);
        // 计算所有正在上传文件的速度总和并保留两位小数
        uploadStatus.value.currentSpeed = Number(Array.from(uploadStatus.value.filesSpeeds.values()).reduce((sum, speed) => sum + speed, 0).toFixed(2));
        lastLoaded = evt.loaded;
        lastTime = new Date().getTime();
      }

      uploadStatus.value.averageSpeed = Number((evt.loaded / elapsedTime / 1024 / 1024).toFixed(2));
      uploadStatus.value.progress = Number(percent);

      // 调用进度回调
      if (options.onProgress) {
        options.onProgress({ percent: Number(percent) });
      }
    });

    // 发送上传请求
    const result = await upload.promise();
    
    // 上传成功，将文件添加到永久列表顶部
    const newFile = {
      uid: file.uid,
      name: file.name,
      status: 'done',
      percent: 100,
      size: file.size,
      type: file.type,
      selected: false,
      uploadDate: new Date().toISOString().split('T')[0],
      viewCount: 0,
      downloadCount: 0,
      url: `https://share-download.onmicrosoft.cn${key}`,
      response: result
    };
    
    fileList.value = [newFile, ...fileList.value];
    message.success(`${file.name} 上传成功`);

    // 获取新上传文件的统计数据
    await fetchFileStats(newFile);

    // 从临时上传列表中移除
    uploadingList.value = uploadingList.value.filter(item => item.uid !== file.uid);

    // 调用成功回调
    if (options.onSuccess) {
      options.onSuccess(result);
    }

    return result;
  } catch (error: any) {
    message.error(`上传失败: ${error.message}`);
    
    // 从临时上传列表中移除
    uploadingList.value = uploadingList.value.filter(item => item.uid !== file.uid);

    // 调用错误回调
    if (options.onError) {
      options.onError(error);
    }
    throw error;
  } finally {
    // 从速度Map中移除当前文件
    uploadStatus.value.filesSpeeds.delete(file.uid);
    // 重新计算总速度
    uploadStatus.value.currentSpeed = Array.from(uploadStatus.value.filesSpeeds.values()).reduce((sum, speed) => sum + speed, 0);
    uploadStatus.value.progress = 0;
    uploadStatus.value.averageSpeed = 0;
    // 只有当没有文件在上传时才设置isUploading为false
    if (uploadStatus.value.filesSpeeds.size === 0) {
      uploadStatus.value.isUploading = false;
    }
  }
};

// 文件上传相关方法
const handleChange = (info: UploadChangeParam<any>) => {
  const file = info.file;
  
  // 处理文件删除
  if (file.status === 'removed') {
    // 从临时上传列表中移除
    uploadingList.value = uploadingList.value.filter(item => item.uid !== file.uid);
    message.success('已取消上传');
  }
};

const handleDrop = (e: DragEvent) => {
  console.log('File dropped:', e);
};

const handleDelete = (file: any) => {
  fileList.value = fileList.value.filter(item => item.uid !== file.uid);
  saveFileList(); // 保存更新后的文件列表
  message.success('文件已删除');
};

// 数据统计相关方法
const toggleGlobal = (type: 'files' | 'size') => {
  showGlobal.value[type] = !showGlobal.value[type];
};

const fetchGlobalStats = async () => {
  try {
    const response = await axios.get(API.getBucketStats);
    if (response.data) {
      const data = response.data;
      
      if (data.count?.data?.overall !== undefined) {
        globalStats.value.totalFiles = data.count.data.overall;
      }
      
      if (data.storage?.data?.overall !== undefined) {
        globalStats.value.totalSize = formatFileSize(data.storage.data.overall);
      }
      
      if (data.traffic?.data?.result) {
        const totalTraffic = data.traffic.data.result.reduce((total, dayData) => {
          return total + (dayData.data?.reduce((sum, value) => sum + value, 0) || 0);
        }, 0);
        globalStats.value.totalTraffic = formatFileSize(totalTraffic);
      }
    }
  } catch (error) {
    console.error('获取全站统计数据失败:', error);
    message.error('获取全站统计数据失败');
  }
};

// 多选相关方法
const toggleMultiSelect = () => {
  isMultiSelect.value = !isMultiSelect.value;
  if (!isMultiSelect.value) {
    fileList.value.forEach(file => file.selected = false);
  }
};

const handleItemClick = (file: any) => {
  if (isMultiSelect.value) {
    file.selected = !file.selected;
  }
};

// 批量操作方法
const batchDownload = () => {
  const selectedUrls = selectedFiles.value.map(file => file.url);
  if (selectedUrls.length === 0) {
    message.warning('请先选择要下载的文件');
    return;
  }
  
  selectedUrls.forEach(url => window.open(url));
  message.success(`正在下载 ${selectedUrls.length} 个文件`);
};

// 获取单个文件的统计数据
const fetchFileStats = async (file: any) => {
  try {
    // 创建一个干净的文件副本，移除统计数据
    const cleanFile = JSON.parse(JSON.stringify(file));
    delete cleanFile.downloadCount;
    delete cleanFile.viewCount;

    // 提交到服务器获取hash
    const response = await axios.post(API.submitShareList, [cleanFile]);
    const { hash } = response.data;
    
    // 获取统计数据
    const statsResponse = await axios.get(API.getShareStats(hash));
    if (statsResponse.data) {
      // 更新文件的统计数据
      const index = fileList.value.findIndex(f => f.uid === file.uid);
      if (index > -1) {
        fileList.value[index] = {
          ...fileList.value[index],
          viewCount: statsResponse.data.views || 0,
          downloadCount: statsResponse.data.downloads || 0
        };
      }
    }
  } catch (error) {
    console.error('获取文件统计失败:', error);
  }
};

// 批量获取文件统计数据
const fetchAllFileStats = async () => {
  const promises = fileList.value.map(file => fetchFileStats(file));
  await Promise.allSettled(promises);
};

// 批量分享
const batchShare = async () => {
  if (selectedFiles.value.length === 0) {
    message.warning('请先选择要分享的文件');
    return;
  }

  try {
    // 创建一个干净的文件列表副本，移除统计数据
    const filesToShare = selectedFiles.value.map(file => {
      const cleanFile = JSON.parse(JSON.stringify(file));
      delete cleanFile.viewCount;
      delete cleanFile.downloadCount;
      return cleanFile;
    });

    // 提交分享请求
    const response = await axios.post(API.submitShareList, filesToShare);
    const { hash } = response.data;
    
    // 构建分享链接
    const shareLink = `${window.location.origin}/share/${hash}`;

    // 显示分享成功弹窗
    Modal.success({
      title: '批量分享成功',
      class: 'share-modal',
      content: h('div', { class: 'py-2' }, [
        h('p', { class: 'text-gray-600 mb-2 text-sm' }, [
          h('span', '已成功分享 '),
          h('span', { class: 'font-medium text-gray-800' }, selectedFiles.value.length),
          h('span', ' 个文件')
        ]),
        h('div', { class: 'bg-gray-50 rounded px-3 py-2 border border-gray-100' }, [
          h('code', { class: 'text-blue-600 text-sm break-all' }, shareLink)
        ]),
        h('div', { class: 'mt-3 text-gray-500 text-xs' }, [
          '分享文件：',
          h('div', { class: 'mt-1' },
            selectedFiles.value.map(file => 
              h('div', { class: 'truncate text-gray-600' }, `• ${file.name}`)
            )
          )
        ]),
      ]),
      okText: '复制链接',
      centered: true,
      width: 480,
      onOk: () => {
        navigator.clipboard.writeText(shareLink);
        message.success('链接已复制到剪贴板');
      }
    });

    // 更新所有分享文件的统计数据
    await Promise.all(filesToShare.map(file => fetchFileStats(file)));
    
    // 如果在多选模式下，可以选择是否退出多选模式
    if (isMultiSelect.value) {
      // 清除所有选择
      fileList.value.forEach(file => file.selected = false);
      isMultiSelect.value = false;
    }
  } catch (error) {
    console.error('分享文件失败:', error);
    message.error('批量分享失败，请稍后重试');
  }
};

// 生命周期钩子
onMounted(async () => {
  loadFileList(); // 加载保存的文件列表
  fetchGlobalStats();
  await fetchAllFileStats(); // 获取所有文件的统计数据
});

// 定时更新统计数据
let statsUpdateInterval: any = null;

onMounted(() => {
  // 每5分钟更新一次统计数据
  statsUpdateInterval = setInterval(fetchAllFileStats, 5 * 60 * 1000);
});

onUnmounted(() => {
  if (statsUpdateInterval) {
    clearInterval(statsUpdateInterval);
  }
});
</script>

<style scoped>
.file-list-item {
  @apply transition-all duration-200;
}

/* 添加移动端响应式样式 */
@media (max-width: 640px) {
  .ant-upload-drag {
    padding: 16px 8px;
  }
  
  .ant-btn {
    padding: 4px 8px;
    height: 32px;
  }
}
</style>
  
  