<template>
  <div class="flex flex-col items-center p-5 space-y-6 bg-[#f5f5f5] min-h-screen pt-10">
    <div class="max-w-[840px] w-full border border-gray-200 rounded-xl bg-white p-6 space-y-6">
      <h1 class="text-2xl text-gray-800 text-center">Zkeq 和 Ta 的朋友们 的 文件分享服务站</h1>
      <p class="text-gray-600 text-sm pb-4">
        <span class="text-blue-500">Tips：</span>
        本工具存在的作用就是用来传输一些文件 可以代替U盘或者微信来使用 会很方便
      </p>
      <a-upload-dragger
        v-model:fileList="fileList"
        name="file"
        :multiple="true"
        action="https://www.mocky.io/v2/5cc8019d300000980a055e76"
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
        <a-col :xs="24" :sm="12" :md="6">
          <stat-card 
            type="files" 
            :title="showGlobal.files ? '全站文件个数' : '我的文件个数'" 
            :value="showGlobal.files ? globalStats.totalFiles : fileStats.totalFiles"
            suffix="个"
            @click="toggleGlobal('files')"
            class="cursor-pointer"
          />
        </a-col>
        <a-col :xs="24" :sm="12" :md="6">
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
        <a-col :xs="24" :sm="12" :md="6">
          <stat-card 
            type="speed" 
            title="当前上传速率" 
            :value="fileStats.uploadSpeed" 
            :precision="1" 
            suffix="MB/s" 
          />
        </a-col>
        <a-col :xs="24" :sm="12" :md="6">
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
    <div class="max-w-[840px] w-full bg-white rounded-xl p-6">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-xl font-medium text-gray-800">文件列表</h2>
          <div class="flex space-x-3">
            <a-button 
              :type="isMultiSelect ? 'primary' : 'default'"
              @click="toggleMultiSelect"
              class="flex items-center"
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
              class="flex items-center"
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
              class="flex items-center"
            >
              <template #icon>
                <download-outlined />
              </template>
              <span class="ml-1">批量下载{{ selectedFiles.length ? ` (${selectedFiles.length})` : '' }}</span>
            </a-button>
          </div>
        </div>
        <div v-if="fileListData.length" class="space-y-4">
          <div 
            v-for="file in fileListData" 
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
              />
            </div>
          </div>
        </div>
        <a-empty v-else description="暂无文件" />
      </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { 
  InboxOutlined, 
  CheckSquareOutlined, 
  DownloadOutlined,
  ShareAltOutlined 
} from '@ant-design/icons-vue';
import { message, Upload } from 'ant-design-vue';
import type { UploadChangeParam } from 'ant-design-vue';
import StatCard from '../components/StatCard.vue';
import FileListItem from '../components/FileListItem.vue';
import { API } from '../config.js';
import axios from 'axios';
import { formatFileSize } from '../utils/format';

const fileList = ref([]);

// 定义表格列
const columns = [
  {
    title: '文件名',
    dataIndex: 'name',
    key: 'name',
  },
  {
    title: '大小',
    dataIndex: 'size',
    key: 'size',
    customRender: ({ text }: { text: number }) => {
      return formatFileSize(text);
    },
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
  },
  {
    title: '操作',
    key: 'action',
  },
];

const handleChange = (info: UploadChangeParam) => {
  const status = info.file.status;
  if (status !== 'uploading') {
    console.log(info.file, info.fileList);
  }
  if (status === 'done') {
    message.success(`${info.file.name} 文件上传成功`);
  } else if (status === 'error') {
    message.error(`${info.file.name} 文件上传失败`);
  }
};

const handleDrop = (e: DragEvent) => {
  console.log(e);
};

// 添加删除文件方法
const handleDelete = (file: any) => {
  fileList.value = fileList.value.filter(item => item.uid !== file.uid);
  message.success('文件已删除');
};

// 添加全局状态控制
const showGlobal = ref({
  files: false,
  size: false
});

// 切换全局/个人数据显示
const toggleGlobal = (type: 'files' | 'size') => {
  showGlobal.value[type] = !showGlobal.value[type];
};

// 修改全站统计数据，从API获取
const globalStats = ref({
  totalFiles: 0,
  totalSize: 0,
  totalTraffic: 50  // 示例数据，单位GB
});

// 获取全站统计数据
const fetchGlobalStats = async () => {
  try {
    const response = await axios.get(API.getBucketStats);
    if (response.data) {
      const data = response.data;
      
      // 获取文件数量
      if (data.count?.data?.overall !== undefined) {
        globalStats.value.totalFiles = data.count.data.overall;
      }
      
      // 获取存储大小
      if (data.storage?.data?.overall !== undefined) {
        // 假设返回的大小单位为字节，转换为MB
        globalStats.value.totalSize = data.storage.data.overall / (1024 * 1024);
      }
      
      // 获取流量数据 - 计算所有日期数据的总和
      if (data.traffic?.data?.result) {
        let totalTraffic = 0;
        data.traffic.data.result.forEach(dayData => {
          // 将每天的数据相加
          if (dayData.data && dayData.data.length > 0) {
            totalTraffic += dayData.data.reduce((sum, value) => sum + value, 0);
          }
        });
        // 转换为GB
        globalStats.value.totalTraffic = totalTraffic / (1024 * 1024 * 1024);
      }
    }
  } catch (error) {
    console.error('获取全站统计数据失败:', error);
    message.error('获取全站统计数据失败');
  }
};

// 组件挂载时获取数据
onMounted(() => {
  fetchGlobalStats();
});

// 修改文件统计数据计算
const fileStats = computed(() => {
  let totalSize = 0;
  fileList.value.forEach(file => {
    totalSize += file.size || 0;
  });
  
  return {
    totalFiles: fileList.value.length,
    totalSize: formatFileSize(totalSize), // 使用新的格式化函数
    uploadSpeed: 5.7,
    usedTraffic: 1.25
  };
});
// 添加多选相关状态
const isMultiSelect = ref(false);

// 修改文件列表数据结构，添加selected属性
const fileListData = ref([
  {
    name: '示例文件.pdf',
    size: 1024 * 1024 * 2.5,
    uploadDate: '2024-01-20',
    type: 'PDF文档',
    viewCount: 10,
    downloadCount: 5,
    url: 'https://example.com/file.pdf',
    selected: false
  }
]);

// 计算已选择的文件
const selectedFiles = computed(() => {
  return fileListData.value.filter(file => file.selected);
});

// 切换多选模式
const toggleMultiSelect = () => {
  isMultiSelect.value = !isMultiSelect.value;
  if (!isMultiSelect.value) {
    // 退出多选模式时清除所有选择
    fileListData.value.forEach(file => file.selected = false);
  }
};

// 批量下载文件
const batchDownload = () => {
  const selectedUrls = selectedFiles.value.map(file => file.url);
  if (selectedUrls.length === 0) {
    message.warning('请先选择要下载的文件');
    return;
  }
  
  // 这里实现批量下载逻辑
  selectedUrls.forEach(url => {
    window.open(url);
  });
  message.success(`正在下载 ${selectedUrls.length} 个文件`);
};

// 处理列表项点击
const handleItemClick = (file: any) => {
  if (isMultiSelect.value) {
    file.selected = !file.selected;
  }
};

// 批量分享文件
const batchShare = () => {
  const selectedUrls = selectedFiles.value.map(file => file.url);
  if (selectedUrls.length === 0) {
    message.warning('请先选择要分享的文件');
    return;
  }
  
  // 这里实现批量分享逻辑
  message.success(`已选择 ${selectedUrls.length} 个文件进行分享`);
};
</script>

<style scoped>
.file-list-item {
  @apply transition-all duration-200;
}

/* 移除了 hover scale 效果 */
</style>
  
  