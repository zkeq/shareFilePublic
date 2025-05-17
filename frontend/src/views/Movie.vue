<template>
  <div class="flex flex-col items-center p-2 space-y-6 bg-[#f5f5f5] min-h-screen pt-10">
    <div class="max-w-[840px] w-full border border-gray-200 rounded-xl bg-white p-4 space-y-6">
      <!-- Video Player -->
      <div class="aspect-video">
        <div id="player"></div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="py-4 text-center">
        <a-spin />
        <p class="mt-2 text-gray-500">正在加载视频信息...</p>
      </div>

      <!-- Error State -->
      <div v-if="error" class="py-4 text-center text-red-500">
        {{ error }}
      </div>

      <!-- Announcement Section -->
      <div v-if="announcement && !loading" class="mt-6 markdown-body max-w-none">
        <h2 class="text-xl font-bold mb-4">视频公告</h2>
        <div v-html="renderedAnnouncement"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import axios from 'axios'
import { marked } from 'marked'
import { API } from '../config.js'

// Declare DogePlayer type
declare global {
  interface Window {
    DogePlayer: any;
    videoTogetherExtension: {
      CreateRoom: (roomName: string, password: string) => void;
      JoinRoom: (roomName: string, password: string) => void;
    }
  }
}

const route = useRoute()
const loading = ref(true)
const error = ref('')
const announcement = ref('')
const renderedAnnouncement = ref('')
let player: any = null

// Initialize video player and VideoTogether
const initPlayer = () => {
  const vcode = route.params.hash as string
  if (!vcode) {
    error.value = '无效的视频代码'
    loading.value = false
    return
  }

  // Load VideoTogether script
  const vtScript = document.createElement('script')
  vtScript.src = 'https://jsd.onmicrosoft.cn/gh/VideoTogether/VideoTogether@latest/release/extension.website.user.js'
  vtScript.async = true
  vtScript.onload = () => {
    // Get URL parameters for room management
    const urlParams = new URLSearchParams(window.location.search)
    const action = urlParams.get('action')
    
    // Generate room name and password based on vcode
    const roomName = `movie-${vcode}`
    const password = `pass-${vcode}`

    setTimeout(() => {
      // Handle room creation or joining
      if (action === 'create') {
        window.videoTogetherExtension.CreateRoom(roomName, password)
      } else {
        // Join room by default when no action is specified
        window.videoTogetherExtension.JoinRoom(roomName, password)
      }
    }, 2400)

    // Remove action parameter from URL
    const newUrl = new URL(window.location.href)
    newUrl.searchParams.delete('action')
    window.history.replaceState({}, '', newUrl.toString())
  }
  document.head.appendChild(vtScript)

  // Load DogePlayer script
  const dogeScript = document.createElement('script')
  dogeScript.src = 'https://player.dogecloud.com/js/loader'
  dogeScript.onload = () => {
    player = new window.DogePlayer({
      container: document.getElementById('player'),
      userId: 2220,
      vcode: vcode
    })
  }
  document.head.appendChild(dogeScript)
}

// Fetch and render announcement
const fetchAnnouncement = async () => {
  try {
    const vcode = route.params.hash as string
    const response = await axios.get(API.getNotice(vcode))
    if (response.data) {
      // Convert response.data to string if it's an object
      const announcementText = response.data.content
      
      announcement.value = announcementText
      // Wait for marked to complete
      renderedAnnouncement.value = await marked(announcementText, {
        gfm: true, // Enable GitHub Flavored Markdown
        breaks: true // Enable line breaks
      })
      loading.value = false
    }
  } catch (error) {
    console.error('获取公告失败:', error)
    message.error('获取公告失败')
    loading.value = false
  }
}

// Lifecycle hooks
onMounted(() => {
  initPlayer()
  fetchAnnouncement()
})

onBeforeUnmount(() => {
  // Cleanup player if needed
  if (player && typeof player.destroy === 'function') {
    player.destroy()
  }
  
  // Remove scripts
  const scripts = document.querySelectorAll('script[src*="VideoTogether"], script[src*="dogecloud"]')
  scripts.forEach(script => script.remove())
})
</script>

<style>

</style>