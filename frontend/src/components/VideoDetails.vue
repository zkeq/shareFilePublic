<template>
  <div class="video-details mt-4 border-t border-gray-100 pt-4">
    <!-- 状态栏 -->
    <div class="flex justify-between items-center mb-4">
      <div class="flex items-center">
        转码状态: <a-tag class="ml-3" :color="statusColor">{{ taskStatus }}</a-tag>
      </div>
      <a-button
        type="primary"
        @click="submitTask"
        :loading="isSubmitting"
        :disabled="taskStatus === '已上传'"
      >提交任务</a-button>
    </div>

    <!-- 视频代码信息 -->
    <div v-if="taskStatus === '已上传' && videoCode" class="mb-4">
      <div class="info-item flex items-center">
        <span class="font-medium mr-2">视频代码 vcode：</span>
        <span class="text-blue-500">{{ videoCode }}</span>
      </div>
    </div>

    <!-- 视频详情信息 -->
    <div v-if="taskStatus === '已上传'" class="video-details-content">
      <!-- 视频封面和基本信息 -->
      <div class="flex flex-col md:flex-row gap-6 mb-6">
        <div class="video-thumbnail w-full md:w-64 h-48 md:h-36 relative overflow-hidden rounded-lg bg-gray-100">
          <template v-if="videoInfo.thumbnail">
            <img :src="videoInfo.thumbnail" class="w-full h-full object-cover" :alt="videoInfo.name" />
          </template>
          <template v-else>
            <div class="flex items-center justify-center h-full">
              <a-spin />
              <span class="ml-2 text-gray-500">处理中...</span>
            </div>
          </template>
        </div>
        <div class="flex-1">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div class="info-item">
              <span class="font-medium">视频ID：</span>
              <span>{{ videoInfo.vid }}</span>
            </div>
            <div class="info-item">
              <span class="font-medium">分辨率：</span>
              <span>{{ videoInfo.source_file?.width }}x{{ videoInfo.source_file?.height }}</span>
            </div>
            <div class="info-item">
              <span class="font-medium">文件格式：</span>
              <span>{{ videoInfo.source_file?.ext.toUpperCase() }}</span>
            </div>
            <div class="info-item">
              <span class="font-medium">视频码率：</span>
              <span>{{ formatBitrate(videoInfo.source_file?.vbr || 0) }}</span>
            </div>
            <div class="info-item">
              <span class="font-medium">宽高比：</span>
              <span>{{ videoInfo.source_file?.aspect_ratio.toFixed(3) }}</span>
            </div>
            <div class="info-item">
              <span class="font-medium">音频码率：</span>
              <span>{{ (videoInfo.source_file?.abr / 1000).toFixed(0) }} Kbps</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 转码版本 -->
      <div class="transcode-versions">
        <h4 class="text-base font-medium mb-4">转码版本</h4>
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          <div v-for="quality in videoInfo.vtypes" :key="quality.vtype" 
               class="version-card p-3 border rounded-lg">
            <div class="flex justify-between items-center mb-2">
              <span class="font-medium">{{ quality.name }}</span>
              <a-tag :color="quality.status === 'success' ? 'success' : 'warning'">
                {{ quality.status === 'success' ? '完成' : '处理中' }}
              </a-tag>
            </div>
            <div class="text-sm text-gray-500">
              <div>大小：{{ (quality.size / 1024 / 1024).toFixed(2) }} MB</div>
              <div>清晰度：{{ (quality.vbr / 1000).toFixed(0) }} K</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="flex justify-end mt-6">
        <a-button type="primary" @click="generatePlayPage" :disabled="!videoCode">生成播放页</a-button>
      </div>
    </div>
  </div>

  <!-- 播放页生成模态框 -->
  <a-modal
    v-model:visible="playPageModalVisible"
    title="生成播放页"
    @ok="handleNoticeSubmit"
    :okText="hasExistingNotice ? '更新' : '发布'"
    cancelText="取消"
    :confirmLoading="isSubmittingNotice"
    class="mobile-modal"
  >
    <div class="play-page-form">
      <!-- 播放页地址 -->
      <div class="mb-4">
        <div class="font-medium mb-2">播放页地址:</div>
        <a-input
          :value="playPageUrl"
          readonly
          class="bg-gray-50"
        />
      </div>

      <!-- 密码输入框 -->
      <div class="mb-4">
        <div class="font-medium mb-2">密码:</div>
        <a-input
          v-model:value="noticeForm.password"
          placeholder="请输入密码"
          type="password"
        />
      </div>

      <!-- 公告输入区域 -->
      <div class="mb-4">
        <div class="font-medium mb-2">公告:</div>
        <a-textarea
          v-model:value="noticeForm.content"
          placeholder="请输入公告内容"
          :rows="4"
        />
      </div>
    </div>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import { message } from 'ant-design-vue';
import axios from 'axios';
import { API } from '../config.js'

interface Props {
  videoUrl: string;
}

const props = defineProps<Props>();

interface VideoInfo {
  vid: number;
  vcode: string;
  name: string;
  description: string;
  duration: number;
  length: string;
  thumbnail: string;
  thumbnail_small: string;
  images: string[];
  source_file: {
    ext: string;
    width: number;
    height: number;
    vbr: number;
    abr: number;
    size: number;
    aspect_ratio: number;
  };
  vtypes: VideoQuality[];
  create_time_text: string;
  edited_time_text: string;
}

interface VideoQuality {
  vtype: number;
  name: string;
  status: string;
  size: number;
  vbr: number;
}

const videoInfo = ref<VideoInfo>({} as VideoInfo);

const taskStatus = ref('未提交');
const isSubmitting = ref(false);
const videoCode = ref('');
const videoQualities = ref<VideoQuality[]>([]);
const taskHash = ref('');

const statusColor = computed(() => {
  switch (taskStatus.value) {
    case '已上传': return 'success';
    case '上传中': return 'processing';
    default: return 'default';
  }
});

const formatDuration = (seconds: number): string => {
  if (!seconds) return '00:00';
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
};

const formatBitrate = (bitrate: number): string => {
  if (!bitrate) return '未知';
  return `${(bitrate / 1000000).toFixed(2)} Mbps`;
};

const getTaskHash = async () => {
  try {
    const response = await axios.post(API.getTaskHash, { url: props.videoUrl });
    taskHash.value = response.data.hash;
    return response.data.hash;
  } catch (error) {
    message.error('获取任务哈希值失败');
    return null;
  }
};

const checkTaskStatus = async (hash: string) => {
  try {
    const response = await axios.get(API.getTaskStatus(hash));
    if (response.data.status === '已上传') {
      taskStatus.value = '已上传';
      videoCode.value = response.data.vcode;
      await getVideoDetails(response.data.vcode);
      return true;
    }
    if (response.data.status === '上传中') {
      taskStatus.value = '上传中';
      return false;
    }
    return false;
  } catch (error) {
    return false;
  }
};

const submitTask = async () => {
  if (isSubmitting.value) return;
  
  isSubmitting.value = true;
  try {
    const response = await axios.post(API.submitVideoTask, { url: props.videoUrl });
    taskHash.value = response.data.hash;
    taskStatus.value = '上传中';
    
    // 开始轮询任务状态
    const pollInterval = setInterval(async () => {
      const isComplete = await checkTaskStatus(taskHash.value);
      if (isComplete) {
        clearInterval(pollInterval);
      }
    }, 3000);
    
  } catch (error) {
    message.error('提交任务失败');
  } finally {
    isSubmitting.value = false;
  }
};

const getVideoDetails = async (vcode: string) => {
  try {
    const response = await axios.get(API.getVideoDetails(vcode));
    videoInfo.value = response.data;
  } catch (error) {
    message.error('获取视频详情失败');
  }
};

// 新增的响应式变量
const playPageModalVisible = ref(false);
const isSubmittingNotice = ref(false);
const hasExistingNotice = ref(false);
const noticeForm = ref({
  password: '',
  content: '',
  vcode: ''
});

// 计算播放页URL
const playPageUrl = computed(() => {
  if (!videoCode.value) return '';
  return `${window.location.origin}/movie/${videoCode.value}`;
});

// 获取公告信息
const getNoticeInfo = async (vcode: string) => {
  try {
    const response = await axios.get(API.getNotice(vcode));
    if (response.data) {
      noticeForm.value.content = response.data.content;
      hasExistingNotice.value = true;
    } else {
      hasExistingNotice.value = false;
    }
  } catch (error) {
    hasExistingNotice.value = false;
  }
};

// 处理公告提交
const handleNoticeSubmit = async () => {
  if (hasExistingNotice.value) {
    await handleNoticeUpdate();
    return;
  }
  if (!noticeForm.value.content.trim()) {
    message.error('请输入公告内容');
    return;
  }

  if (!noticeForm.value.password.trim()) {
    message.error('请输入密码');
    return;
  }

  isSubmittingNotice.value = true;
  try {
    const payload = {
      content: noticeForm.value.content,
      vcode: videoCode.value,
      password: noticeForm.value.password
    };

    const api = hasExistingNotice.value ? API.updateNotice(videoCode.value) : API.createNotice;
    const response = await axios.post(api, payload);
    
    message.success(hasExistingNotice.value ? '公告更新成功' : '公告发布成功');
    playPageModalVisible.value = false;
  } catch (error) {
    message.error('操作失败，请检查密码是否正确');
  } finally {
    isSubmittingNotice.value = false;
  }
};

// 处理公告提交
const handleNoticeUpdate = async () => {
  if (!noticeForm.value.content.trim()) {
    message.error('请输入公告内容');
    return;
  }

  if (!noticeForm.value.password.trim()) {
    message.error('请输入密码');
    return;
  }

  isSubmittingNotice.value = true;
  try {
    const payload = {
      content: noticeForm.value.content,
      vcode: videoCode.value,
      password: noticeForm.value.password
    };

    const api = hasExistingNotice.value ? API.updateNotice(videoCode.value) : API.createNotice;
    const response = await axios.put(api, payload);
    
    message.success(hasExistingNotice.value ? '公告更新成功' : '公告发布成功');
    playPageModalVisible.value = false;
  } catch (error) {
    message.error('操作失败，请检查密码是否正确');
  } finally {
    isSubmittingNotice.value = false;
  }
};

// 修改现有的 generatePlayPage 函数
const generatePlayPage = async () => {
  if (!videoCode.value) {
    message.error('视频代码不存在');
    return;
  }
  
  noticeForm.value.vcode = videoCode.value;
  await getNoticeInfo(videoCode.value);
  playPageModalVisible.value = true;
};

onMounted(async () => {
  const hash = await getTaskHash();
  if (hash) {
    await checkTaskStatus(hash);
  }
});
</script>

<style scoped>
.video-details {
  @apply bg-white rounded-lg overflow-hidden px-4 md:px-6;
}

.info-item {
  @apply p-2 bg-gray-50 rounded text-sm md:text-base;
}

.quality-list {
  @apply flex flex-wrap justify-end;
}

.play-page-form {
  @apply space-y-4;
}

/* 添加移动端样式 */
@media (max-width: 640px) {
  .video-details {
    @apply px-3;
  }
  
  .info-item {
    @apply p-2;
  }
  
  .version-card {
    @apply text-sm;
  }
}

/* 移动端模态框样式 */
:deep(.mobile-modal) {
  @apply w-11/12 md:w-auto max-w-lg;
  
  .ant-modal-content {
    @apply p-4;
  }
  
  .ant-modal-header {
    @apply pb-3;
  }
  
  .ant-modal-body {
    @apply py-3;
  }
  
  .ant-modal-footer {
    @apply pt-3;
  }
}
</style>