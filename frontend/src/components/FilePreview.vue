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

    <!-- Audio Preview -->
    <div v-else-if="isAudio" class="w-full max-w-3xl mx-auto">
      <div id="aplayer" class="rounded-lg shadow-sm"></div>
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
// @ts-ignore
import APlayer from 'aplayer'
import 'aplayer/dist/APlayer.min.css'

// Declare VideoTogether extension type
declare global {
  interface Window {
    videoTogetherExtension: {
      CreateRoom: (roomName: string, password: string) => void;
      JoinRoom: (roomName: string, password: string) => void;
    }
  }
}

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

const isAudio = computed(() => {
  const ext = props.file.name.toLowerCase().split('.').pop()
  return ['mp3', 'wav', 'ogg', 'aac', 'm4a', 'flac', 'wma', 'ape', 'opus', 'mid', 'midi', 'amr', 'm4r', '3gp', 'aa', 'aax', 'aiff', 'alac', 'ac3', 'dsf', 'dff'].includes(ext || '')
})

const isVideo = computed(() => {
  const ext = props.file.name.toLowerCase().split('.').pop()
  return ['mp4', 'webm', 'ogg', 'm3u8', 'flv', 'mov', 'm4v', 'avi', 'wmv', 'mkv', 'mpeg', 'mpg', '3gp', 'ts'].includes(ext || '')
})

const isOffice = computed(() => {
  const ext = props.file.name.toLowerCase().split('.').pop()
  return ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'].includes(ext || '')
})

const isPdf = computed(() => {
  const ext = props.file.name.toLowerCase().split('.').pop()
  return ext === 'pdf'
})

// Media player instances
let videoPlayer: any = null
let audioPlayer: any = null

// Initialize video player
const initVideoPlayer = () => {
  if (isVideo.value && props.file.url) {
    // Load VideoTogether script dynamically
    const script = document.createElement('script')
    script.src = 'https://jsd.onmicrosoft.cn/gh/VideoTogether/VideoTogether@latest/release/extension.website.user.js'
    script.async = true
    script.onload = () => {
      // Get URL parameters
      const urlParams = new URLSearchParams(window.location.search);
      const action = urlParams.get('action');
      
      // Generate room name and password based on file URL hash
      const fileUrlHash = btoa(props.file.url).replace(/[/+=]/g, '').substring(0, 8);
      const roomName = `sfp-${fileUrlHash}`;
      const password = `password-${fileUrlHash}`;

     
     setTimeout(() => {
      // Handle room creation or joining based on URL parameter
      if (action === 'create') {
        window.videoTogetherExtension.CreateRoom(roomName, password);
      } else if (action === 'join') {
        window.videoTogetherExtension.JoinRoom(roomName, password);
      }
     }, 1200)

      // Remove action parameter from URL without page reload
      const newUrl = new URL(window.location.href);
      newUrl.searchParams.delete('action');
      window.history.replaceState({}, '', newUrl.toString());
    }
    document.head.appendChild(script)

    videoPlayer = new DPlayer({
      container: document.getElementById('dplayer'),
      video: {
        url: props.file.url,
      },
      autoplay: false,
    })
  }
}

// Initialize audio player
const initAudioPlayer = () => {
  if (isAudio.value && props.file.url) {
    audioPlayer = new APlayer({
      container: document.getElementById('aplayer'),
      audio: [{
        name: props.file.name,
        url: props.file.url,
      }],
      autoplay: false,
    })
  }
}

// Clean up video player
const destroyVideoPlayer = () => {
  if (videoPlayer) {
    videoPlayer.destroy()
    videoPlayer = null
  }
  // Remove VideoTogether script when destroying player
  const script = document.querySelector('script[src*="VideoTogether"]')
  if (script) {
    script.remove()
  }
}

// Clean up audio player
const destroyAudioPlayer = () => {
  if (audioPlayer) {
    audioPlayer.destroy()
    audioPlayer = null
  }
}

// Watch for file changes
watch(
  () => props.file,
  () => {
    destroyVideoPlayer()
    destroyAudioPlayer()
    if (isVideo.value) {
      nextTick(() => {
        initVideoPlayer()
      })
    } else if (isAudio.value) {
      nextTick(() => {
        initAudioPlayer()
      })
    }
  },
  { deep: true }
)

onMounted(() => {
  if (isVideo.value) {
    initVideoPlayer()
  } else if (isAudio.value) {
    initAudioPlayer()
  }
})

onBeforeUnmount(() => {
  destroyVideoPlayer()
  destroyAudioPlayer()
})
</script>