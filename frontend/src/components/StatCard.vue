<template>
  <a-card :bordered="false" class="transition-all duration-300 rounded-lg shadow-sm hover:shadow-md hover:-translate-y-1 bg-white mb-4">
    <div class=" flex flex-col">
      <div class="flex items-center mb-3">
        <div :class="[
          'flex justify-center items-center w-8 h-8 rounded-md mr-3',
          {
            'bg-blue-50': type === 'files',
            'bg-green-50': type === 'size',
            'bg-orange-50': type === 'speed',
            'bg-purple-50': type === 'traffic'
          }
        ]">
          <component :is="icon" :class="[
            'text-base',
            {
              'text-blue-500': type === 'files',
              'text-green-500': type === 'size',
              'text-orange-500': type === 'speed',
              'text-purple-500': type === 'traffic'
            }
          ]" />
        </div>
        <span class="text-sm font-medium text-gray-600">{{ title }}</span>
      </div>
      <div class="flex items-baseline">
        <span :class="[
          'text-2xl font-semibold leading-tight ml-2' ,
          {
            'text-blue-500': type === 'files',
            'text-green-500': type === 'size',
            'text-orange-500': type === 'speed',
            'text-purple-500': type === 'traffic'
          }
        ]">{{ value }}</span>
        <span v-if="suffix" class="text-sm text-gray-500 ml-1">{{ suffix }}</span>
      </div>
    </div>
  </a-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { 
  FileOutlined, 
  CloudUploadOutlined, 
  ThunderboltOutlined, 
  DatabaseOutlined 
} from '@ant-design/icons-vue';

const props = defineProps({
  type: {
    type: String,
    default: 'files',
    validator: (value) => ['files', 'size', 'speed', 'traffic'].includes(value)
  },
  title: {
    type: String,
    required: true
  },
  value: {
    type: [Number, String],
    required: true
  },
  precision: {
    type: Number,
    default: 0
  },
  suffix: {
    type: String,
    default: ''
  }
});

const icon = computed(() => {
  const iconMap = {
    files: FileOutlined,
    size: DatabaseOutlined,
    speed: ThunderboltOutlined,
    traffic: CloudUploadOutlined
  };
  return iconMap[props.type];
});
</script>