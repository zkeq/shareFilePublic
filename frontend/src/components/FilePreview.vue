<template>
  <div class="w-full bg-white rounded-xl p-4">
    <!-- Image Preview -->
    <div v-if="isImage" class="flex justify-center">
      <img :src="file.url" :alt="file.name" class="max-w-full max-h-[600px] object-contain" />
    </div>

    <!-- Video Preview -->
    <div v-else-if="isVideo" class="aspect-video">
      <div id="dplayer"></div>
    </div>

    <!-- Office Preview -->
    <div v-else-if="isOffice" class="aspect-[4/3]">
      <iframe
        :src="`https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(file.url)}`"
        class="w-full h-full border-none"
      ></iframe>
    </div>

    <!-- PDF Preview -->
    <div v-else-if="isPdf" class="aspect-[4/3]">
      <iframe
        :src="`https://service.ezviz.com/mobile/download/viewer?file=${encodeURIComponent(file.url)}`"
        class="w-full h-full border-none"
      ></iframe>
    </div>

    <!-- Unsupported Format -->
    <div v-else class="text-center py-8">
      <p class="text-gray-500">该文件格式暂不支持预览</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed, nextTick, onBeforeUnmount } from 'vue'
// @ts-ignore
import DPlayer from 'dplayer'

const props = defineProps<{
  file: {
    name: string
    url: string
    type?: string
  }
}>()

// File type checks
const isImage = computed(() => {
  const ext = props.file.name.toLowerCase().split('.').pop()
  return ['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(ext || '')
})

const isVideo = computed(() => {
  const ext = props.file.name.toLowerCase().split('.').pop()
  return ['mp4', 'webm', 'ogg'].includes(ext || '')
})

const isOffice = computed(() => {
  const ext = props.file.name.toLowerCase().split('.').pop()
  return ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'].includes(ext || '')
})

const isPdf = computed(() => {
  const ext = props.file.name.toLowerCase().split('.').pop()
  return ext === 'pdf'
})

// Video player instance
let player: any = null

// Initialize video player
const initVideoPlayer = () => {
  if (isVideo.value && props.file.url) {
    player = new DPlayer({
      container: document.getElementById('dplayer'),
      video: {
        url: props.file.url,
      },
      autoplay: false,
    })
  }
}

// Clean up video player
const destroyVideoPlayer = () => {
  if (player) {
    player.destroy()
    player = null
  }
}

// Watch for file changes
watch(
  () => props.file,
  () => {
    destroyVideoPlayer()
    if (isVideo.value) {
      nextTick(() => {
        initVideoPlayer()
      })
    }
  },
  { deep: true }
)

onMounted(() => {
  if (isVideo.value) {
    initVideoPlayer()
  }
})

onBeforeUnmount(() => {
  destroyVideoPlayer()
})
</script> 