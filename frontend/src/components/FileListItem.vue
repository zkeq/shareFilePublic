<template>
  <div class="file-list-item transition-all duration-200 py-3 sm:py-4 px-3 sm:px-6 border border-dashed border-gray-200 hover:border-gray-300 rounded-lg mb-4">
    <!-- 文件名和操作按钮行 -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-3 space-y-2 sm:space-y-0">
      <div class="flex items-center">
        <h3 class="text-base sm:text-lg text-gray-800 hover:text-blue-500 transition-colors duration-200 cursor-pointer font-medium truncate w-full" :title="file.name">
          {{ formatFileName(file.name) }}
        </h3>
      </div>
      <div class="flex space-x-2 justify-end shrink-0">
        <!-- 主页模式显示所有按钮 -->
        <template v-if="mode === 'home'">
          <a-button type="text" size="small" @click="copyLink" class="action-btn flex items-center !px-1 sm:!px-2">
            <template #icon>
              <link-outlined class="text-indigo-500 hover:text-indigo-600" />
            </template>
            <span class="hidden sm:inline">复制链接</span>
          </a-button>
          <a-button type="text" size="small" @click="downloadFile" class="action-btn flex items-center !px-1 sm:!px-2">
            <template #icon>
              <download-outlined class="text-green-500 hover:text-green-600" />
            </template>
            <span class="hidden sm:inline">下载</span>
          </a-button>
          <a-button type="text" size="small" @click="shareFile" class="action-btn flex items-center !px-1 sm:!px-2">
            <template #icon>
              <share-alt-outlined class="text-blue-500 hover:text-blue-600" />
            </template>
            <span class="hidden sm:inline">分享</span>
          </a-button>
        </template>
        <!-- 分享页模式显示所有按钮 -->
        <template v-else>
          <a-button type="text" size="small" @click="copyLink" class="action-btn flex items-center !px-1 sm:!px-2">
            <template #icon>
              <link-outlined class="text-indigo-500 hover:text-indigo-600" />
            </template>
          </a-button>
          <a-button type="text" size="small" @click="downloadFile" class="action-btn flex items-center !px-1 sm:!px-2">
            <template #icon>
              <download-outlined class="text-green-500 hover:text-green-600" />
            </template>
            <span class="hidden sm:inline">下载</span>
          </a-button>
          <a-button type="text" size="small" @click="shareFile" class="action-btn flex items-center !px-1 sm:!px-2">
            <template #icon>
              <share-alt-outlined class="text-blue-500 hover:text-blue-600" />
            </template>
            <span class="hidden sm:inline">分享</span>
          </a-button>
        </template>
      </div>
    </div>
    
    <!-- 文件详细信息 -->
    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2 sm:gap-4 text-xs sm:text-sm text-gray-500 p-2 sm:p-4 border border-gray-100 rounded-md">
      <div class="flex items-center info-item">
        <div class="icon-wrapper bg-opacity-50 bg-purple-50 rounded-lg mr-1 sm:mr-2 flex items-center justify-center w-6 h-6 sm:w-8 sm:h-8">
          <file-outlined class="text-purple-500 text-xs sm:text-base" />
        </div>
        <span class="truncate">{{ formatFileSize(file.size) }}</span>
      </div>
      <div class="flex items-center info-item">
        <div class="icon-wrapper bg-opacity-50 bg-yellow-50 rounded-lg mr-1 sm:mr-2 flex items-center justify-center w-6 h-6 sm:w-8 sm:h-8">
          <calendar-outlined class="text-yellow-500 text-xs sm:text-base" />
        </div>
        <span class="truncate">{{ formatDate(file.uploadDate) }}</span>
      </div>
      <div class="flex items-center info-item">
        <div class="icon-wrapper bg-opacity-50 bg-blue-50 rounded-lg mr-1 sm:mr-2 flex items-center justify-center w-6 h-6 sm:w-8 sm:h-8">
          <file-text-outlined class="text-blue-500 text-xs sm:text-base" />
        </div>
        <span class="truncate">{{ formatMimeType(file.type) }}</span>
      </div>
      <div class="flex items-center info-item">
        <div class="icon-wrapper bg-opacity-50 bg-green-50 rounded-lg mr-1 sm:mr-2 flex items-center justify-center w-6 h-6 sm:w-8 sm:h-8">
          <eye-outlined class="text-green-500 text-xs sm:text-base" />
        </div>
        <span class="truncate">访问 {{ file.viewCount }} 次</span>
      </div>
      <div class="flex items-center info-item">
        <div class="icon-wrapper bg-opacity-50 bg-pink-50 rounded-lg mr-1 sm:mr-2 flex items-center justify-center w-6 h-6 sm:w-8 sm:h-8">
          <download-outlined class="text-pink-500 text-xs sm:text-base" />
        </div>
        <span class="truncate">下载 {{ file.downloadCount }} 次</span>
      </div>
    </div>

    <!-- 视频详情组件 -->
    <video-details
      v-if="mode === 'home' && isVideoFile"
      :video-url="file.url"
    />
  </div>
</template>

<script setup lang="ts">
import { 
  LinkOutlined, 
  DownloadOutlined, 
  ShareAltOutlined,
  FileOutlined,
  CalendarOutlined,
  FileTextOutlined,
  EyeOutlined
} from '@ant-design/icons-vue';
import VideoDetails from './VideoDetails.vue';
import { message, Modal } from 'ant-design-vue';
import { h, computed } from 'vue';
import { formatFileSize, formatMimeType } from '../utils/format';
import axios from 'axios';
import { API } from '../config';

interface FileItem {
  name: string;
  size: number;
  uploadDate: string;
  type: string;
  viewCount: number;
  downloadCount: number;
  url: string;
}

const props = defineProps<{
  file: FileItem;
  mode?: 'home' | 'share'; // 显示模式：home-主页模式，share-分享页模式
}>();

// 设置默认值为分享页模式
const mode = props.mode || 'share';

const emit = defineEmits(['download']);

// 判断是否为视频文件
const isVideoFile = computed(() => {
  return props.file.type.startsWith('video/');
});

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('zh-CN');
};

const formatFileName = (name: string) => {
  return name.length > 32 ? name.slice(0, 32) + '...' : name;
};

const copyLink = () => {
  navigator.clipboard.writeText(props.file.url);
  message.success('链接已复制到剪贴板');
};

const downloadFile = () => {
  // 实现下载逻辑
  window.open(props.file.url);
  // 触发下载事件
  emit('download', props.file);
};

const shareFile = async () => {
  try {
    // Create a clean copy of the file object without viewCount and downloadCount
    const fileToShare = JSON.parse(JSON.stringify(props.file));
    delete fileToShare.viewCount;
    delete fileToShare.downloadCount;

    // Submit the share request with single file list
    const response = await axios.post(API.submitShareList, [fileToShare]);
    const { hash } = response.data;
    
    // 构建分享链接
    const shareLink = `${window.location.origin}/share/${hash}`;

    // 显示分享成功弹窗
    Modal.success({
      title: '分享成功',
      class: 'share-modal',
      content: h('div', { class: 'py-2' }, [
        h('p', { class: 'text-gray-600 mb-2 text-sm' }, [
          h('span', { class: 'mr-1' }, '文件'),
          h('span', { class: 'font-medium text-gray-800 mr-1' }, props.file.name),
          h('span', '分享成功')
        ]),
        h('div', { class: 'bg-gray-50 rounded px-3 py-2 border border-gray-100' }, [
          h('code', { class: 'text-blue-600 text-sm break-all' }, shareLink)
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
  } catch (error) {
    console.error('分享文件失败:', error);
    message.error('分享文件失败');
  }
};
</script>

<style scoped>
.action-btn {
  @apply text-gray-600 hover:text-blue-500 hover:bg-blue-50 rounded transition-all duration-200 transform;
}

.info-item {
  @apply transform transition-all duration-200 hover:font-medium;
}

.icon-wrapper {
  @apply transition-all duration-200 hover:shadow-sm;
}

/* 添加移动端响应式样式 */
@media (max-width: 640px) {
  .action-btn {
    @apply min-w-0;
  }
}
</style>