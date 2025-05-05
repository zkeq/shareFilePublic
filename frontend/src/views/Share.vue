<template>
  <div class="flex flex-col items-center p-2 space-y-6 bg-[#f5f5f5] min-h-screen pt-10">
    <div class="max-w-[840px] w-full border border-gray-200 rounded-xl bg-white p-6 space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl text-gray-800">分享文件列表</h1>
          <p class="text-sm text-gray-500 mt-2">
            访问次数：{{ viewCount }} | 下载次数：{{ downloadCount }}
          </p>
        </div>
        <a-button 
          type="primary"
          @click="batchDownload"
          :disabled="fileList.length === 0"
          class="flex items-center"
        >
          <template #icon>
            <download-outlined />
          </template>
          <span class="ml-1">全部下载</span>
        </a-button>
      </div>
      
      <!-- 文件列表 -->
      <div v-if="fileList.length" class="space-y-4">
        <div v-for="file in fileList" :key="file.name">
          <file-list-item
            :file="file"
            :show-stats="true"
            @download="handleFileDownload"
          />
        </div>
      </div>
      <div v-else-if="loading" class="py-10 text-center">
        <a-spin />
        <p class="mt-4 text-gray-500">正在加载分享文件...</p>
      </div>
      <a-empty v-else description="未找到分享文件或链接已失效" />

      <!-- 单文件预览 -->
      <file-preview
        v-if="fileList.length === 1"
        :file="fileList[0]"
        class="mt-6"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import { DownloadOutlined } from '@ant-design/icons-vue'
import axios from 'axios'
import FileListItem from '../components/FileListItem.vue'
import FilePreview from '../components/FilePreview.vue'
import { API } from '../config.js'

const route = useRoute()
const fileList = ref<any[]>([])
const loading = ref(true)
const viewCount = ref(0)
const downloadCount = ref(0)

// 获取单个文件的统计数据
const fetchFileStats = async (file: any) => {
  try {
    // 创建一个干净的文件副本，移除统计数据
    const cleanFile = JSON.parse(JSON.stringify(file))
    delete cleanFile.downloadCount
    delete cleanFile.viewCount

    // 提交到服务器获取hash
    const response = await axios.post(API.submitShareList, [cleanFile])
    const { hash } = response.data
    
    // 获取统计数据
    const statsResponse = await axios.get(API.getShareStats(hash))
    if (statsResponse.data) {
      // 更新文件的统计数据
      const index = fileList.value.findIndex(f => f.uid === file.uid)
      if (index > -1) {
        fileList.value[index] = {
          ...fileList.value[index],
          viewCount: statsResponse.data.views || 0,
          downloadCount: statsResponse.data.downloads || 0
        }
      }
    }
  } catch (error) {
    console.error('获取文件统计失败:', error)
  }
}

// 批量获取文件统计数据
const fetchAllFileStats = async () => {
  const promises = fileList.value.map(file => fetchFileStats(file))
  await Promise.allSettled(promises)
  
  // 获取当前分享链接的统计数据
  const hash = route.params.hash as string
  try {
    const shareStatsResponse = await axios.get(API.getShareStats(hash))
    if (shareStatsResponse.data) {
      // 计算总的访问次数和下载次数（文件统计 + 分享链接统计）
      viewCount.value =  
        (shareStatsResponse.data.views || 0)
      downloadCount.value = fileList.value.reduce((sum, file) => sum + (file.downloadCount || 0), 0) + 
        (shareStatsResponse.data.downloads || 0)
    }
  } catch (error) {
    console.error('获取分享链接统计失败:', error)
    // 如果获取分享链接统计失败，至少显示文件的统计数据
    viewCount.value = fileList.value.reduce((sum, file) => sum + (file.viewCount || 0), 0)
    downloadCount.value = fileList.value.reduce((sum, file) => sum + (file.downloadCount || 0), 0)
  }
}

// 获取分享文件列表
const fetchShareList = async () => {
  const hash = route.params.hash as string
  if (!hash) return

  try {
    loading.value = true
    const response = await axios.get(API.getShareList(hash))
    if (response.data) {
      fileList.value = response.data.map((file: any) => ({
        ...file,
        status: 'done',
        viewCount: 0,  // 初始化统计数据
        downloadCount: 0
      }))
      // 获取文件列表后立即获取每个文件的统计数据
      await fetchAllFileStats()
    }
  } catch (error) {
    console.error('获取分享文件列表失败:', error)
    message.error('获取分享文件列表失败')
  } finally {
    loading.value = false
  }
}

// 记录访问
const recordView = async () => {
  const hash = route.params.hash as string
  if (!hash) return
  
  try {
    await axios.post(API.incrementViews(hash))
    // 更新访问次数
    viewCount.value++
    // 更新统计数据
    await fetchAllFileStats()
  } catch (error) {
    console.error('记录访问失败:', error)
  }
}

// 记录下载
const recordDownload = async (file: any) => {
  try {
    // 创建一个干净的文件副本，移除统计数据
    const cleanFile = JSON.parse(JSON.stringify(file))
    delete cleanFile.downloadCount
    delete cleanFile.viewCount

    // 提交到服务器获取hash
    const response = await axios.post(API.submitShareList, [cleanFile])
    const { hash } = response.data
    
    await axios.post(API.incrementDownloads(hash))
    // 更新该文件的统计数据
    await fetchFileStats(file)
  } catch (error) {
    console.error('记录下载失败:', error)
  }
}

// 批量下载所有文件
const batchDownload = async () => {
  if (fileList.value.length === 0) {
    message.warning('没有可下载的文件')
    return
  }
  
  // 记录每个文件的下载
  for (const file of fileList.value) {
    if (file.url) {
      window.open(file.url)
      await recordDownload(file)
    }
  }
  
  message.success(`正在下载 ${fileList.value.length} 个文件`)
}

// 单个文件下载方法
const handleFileDownload = async (file: any) => {
  if (file.url) {
    await recordDownload(file)
    // 更新总的下载统计
    await fetchAllFileStats()
  }
}

// 定时更新统计数据
let statsUpdateInterval: any = null

onMounted(() => {
  fetchShareList()
  // 记录页面访问
  recordView()
  // 每5分钟更新一次统计数据
  statsUpdateInterval = setInterval(fetchAllFileStats, 5 * 60 * 1000)
})

onUnmounted(() => {
  if (statsUpdateInterval) {
    clearInterval(statsUpdateInterval)
  }
})
</script>

<style scoped>
.file-list-item {
  @apply transition-all duration-200;
}
</style> 