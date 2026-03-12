<template>
  <div>
    <div class="art-card p-4 mb-4 flex items-center gap-5 flex-wrap">
      <span class="text-sm text-gray-600">选择设备</span>
      <ElSelect
        v-model="selectedModel"
        placeholder="全部型号"
        clearable
        filterable
        style="width: 280px"
      >
        <ElOption
          v-for="model in deviceModelOptions"
          :key="model"
          :label="model"
          :value="model"
        />
      </ElSelect>
    </div>

    <VideoStreamBarChart :selected-model="selectedModel" />

    <ElRow :gutter="20">
      <ElCol :xs="24">
        <VideoStreamDataTable :selected-model="selectedModel" />
      </ElCol>
    </ElRow>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { fetchDroneList } from '@/api/drone'
import VideoStreamBarChart from './modules/video-stream-bar-chart.vue'
import VideoStreamDataTable from './modules/video-stream-data-table.vue'

defineOptions({ name: 'VideoStreamMonitor' })

const selectedModel = ref('')
const deviceModelOptions = ref<string[]>([])

const loadDeviceModelOptions = async () => {
  try {
    const response = await fetchDroneList({ current: 1, size: 100 })
    const records = response?.records ?? response?.data?.records
    const models = Array.isArray(records) ? records.map((item: { model?: string }) => item.model) : []

    deviceModelOptions.value = [...new Set(models.filter((model): model is string => Boolean(model)))]
  } catch (error) {
    console.error('加载设备型号列表失败:', error)
  }
}

onMounted(() => {
  loadDeviceModelOptions()
})
</script>
