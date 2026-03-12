<template>
  <div class="art-card h-140 p-5 mb-5 max-sm:mb-4">
    <div class="art-card-header mb-4">
      <div class="title">
        <h4>视频流监测明细</h4>
        <p>无人船视频流传输记录</p>
      </div>
    </div>

    <ElTable :data="pagedData" stripe max-height="450px" size="small" style="width: 100%">
      <ElTableColumn prop="ship_model" label="型号" width="120" align="center" />
      <ElTableColumn prop="stream_protocol" label="流协议" width="100" align="center" />
      <ElTableColumn prop="video_codec" label="视频编码" width="100" align="center" />
      <ElTableColumn prop="transport_protocol" label="传输协议" width="100" align="center" />
      <ElTableColumn prop="resolution" label="分辨率" width="110" align="center" />
      <ElTableColumn prop="fps" label="帧率" width="90" align="center" />
      <ElTableColumn prop="bitrate_kbps" label="码率(kbps)" width="110" align="center" />
      <ElTableColumn prop="packet_count" label="包计数" width="110" align="center" />
      <ElTableColumn prop="frame_count" label="帧计数" width="110" align="center" />
      <ElTableColumn prop="loss_rate" label="丢包率(%)" width="100" align="center" />
      <ElTableColumn prop="latency_ms" label="延迟(ms)" width="100" align="center" />
      <ElTableColumn prop="jitter_ms" label="抖动(ms)" width="100" align="center" />
      <ElTableColumn prop="source_ip" label="源IP" width="140" align="center" />
      <ElTableColumn prop="source_port" label="源端口" width="100" align="center" />
      <ElTableColumn prop="target_ip" label="目标IP" width="140" align="center" />
      <ElTableColumn prop="target_port" label="目标端口" width="100" align="center" />
      <ElTableColumn prop="stream_url" label="流地址" min-width="220" show-overflow-tooltip />
      <ElTableColumn prop="status" label="状态" width="100" align="center" />
      <ElTableColumn prop="warn" label="警告码" width="90" align="center" />
      <ElTableColumn prop="timestamp" label="时间戳" width="180" fixed="right" align="center" />
    </ElTable>

    <div class="mt-3 flex justify-end">
      <ElPagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="filteredList.length"
        layout="total, prev, pager, next, jumper"
        background
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { fetchVideoStreamData } from '@/api/dashboard'

interface VideoStreamDataItem {
  ship_model: string
  timestamp: string
  stream_protocol: string
  video_codec: string
  transport_protocol: string
  source_ip: string
  source_port: number | null
  target_ip: string
  target_port: number | null
  stream_url: string
  resolution: string
  fps: number | null
  bitrate_kbps: number | null
  packet_count: number
  frame_count: number
  loss_rate: number
  latency_ms: number | null
  jitter_ms: number | null
  status: string
  warn: string
}

const props = withDefaults(
  defineProps<{
    selectedModel?: string
  }>(),
  {
    selectedModel: ''
  }
)

const pageSize = 10
const currentPage = ref(1)
const list = ref<VideoStreamDataItem[]>([])
const refreshTimer = ref<number | null>(null)

const normalizeModel = (value?: string) => (value || '').trim().toLowerCase()

const isModelMatched = (ship_model: string, selectedModel: string) => {
  const ship = normalizeModel(ship_model)
  const selected = normalizeModel(selectedModel)
  if (!selected) return true
  return ship === selected || ship.includes(selected) || selected.includes(ship)
}

const filteredList = computed(() => {
  if (!props.selectedModel) return list.value
  return list.value.filter((item) => isModelMatched(item.ship_model, props.selectedModel))
})

const pagedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredList.value.slice(start, start + pageSize)
})

const clampPage = (current: number, total: number) => {
  const maxPage = Math.max(1, Math.ceil(total / pageSize))
  return Math.min(Math.max(current, 1), maxPage)
}

const loadData = async () => {
  try {
    const data = await fetchVideoStreamData()
    if (Array.isArray(data)) {
      list.value = data as VideoStreamDataItem[]
      currentPage.value = clampPage(currentPage.value, list.value.length)
    }
  } catch (error) {
    console.error('加载视频流表格数据失败:', error)
  }
}

onMounted(() => {
  loadData()
  refreshTimer.value = window.setInterval(loadData, 5000)
})

onBeforeUnmount(() => {
  if (refreshTimer.value !== null) {
    window.clearInterval(refreshTimer.value)
    refreshTimer.value = null
  }
})

watch(
  () => props.selectedModel,
  () => {
    currentPage.value = 1
  }
)
</script>
