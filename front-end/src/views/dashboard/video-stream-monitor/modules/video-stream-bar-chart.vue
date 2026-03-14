<template>
  <div class="mb-6">
    <div class="snapshot-grid mb-4">
      <div v-for="opt in metrics" :key="opt.key" class="snapshot-item">
        <div class="snapshot-label">{{ opt.label }}</div>
        <div class="snapshot-value">{{ latestSnapshot[opt.key] }}</div>
      </div>
    </div>

    <div class="flex items-center mb-3">
      <h4 class="text-2xl font-bold mr-6">视频流传输指标</h4>
      <div class="text-sm text-gray-500">近10条记录柱状图</div>
    </div>

    <VChart :option="echartsOption" autoresize style="width: 100%; height: 380px" />
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { use } from 'echarts/core'
import VChart from 'vue-echarts'
import { BarChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, GridComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { fetchVideoStreamData } from '@/api/dashboard'

use([BarChart, TitleComponent, TooltipComponent, GridComponent, LegendComponent, CanvasRenderer])

interface VideoStreamDataItem {
  ship_model: string
  timestamp: string
  fps: number | null
  bitrate_kbps: number | null
  loss_rate: number
  latency_ms: number | null
  jitter_ms: number | null
}

const props = withDefaults(
  defineProps<{
    selectedModel?: string
  }>(),
  {
    selectedModel: ''
  }
)

const metrics = [
  { key: 'fps', label: '实时帧率' },
  { key: 'bitrate_kbps', label: '实时码率(kbps)' },
  { key: 'loss_rate', label: '实时丢包率(%)' },
  { key: 'latency_ms', label: '实时延迟(ms)' },
  { key: 'jitter_ms', label: '实时抖动(ms)' }
] as const

const rows = ref<VideoStreamDataItem[]>([])
const timer = ref<number | null>(null)

const normalizeModel = (value?: string) => (value || '').trim().toLowerCase()

const filteredRows = computed(() => {
  if (!props.selectedModel) return rows.value
  const selected = normalizeModel(props.selectedModel)
  return rows.value.filter((item) => {
    const model = normalizeModel(item.ship_model)
    return model === selected || model.includes(selected) || selected.includes(model)
  })
})

const chartRows = computed(() => filteredRows.value.slice(0, 10).reverse())

const latestSnapshot = computed<Record<string, string | number>>(() => {
  const latest = filteredRows.value[0]
  if (!latest) {
    return {
      fps: '--',
      bitrate_kbps: '--',
      loss_rate: '--',
      latency_ms: '--',
      jitter_ms: '--'
    }
  }

  return {
    fps: latest.fps ?? '--',
    bitrate_kbps: latest.bitrate_kbps ?? '--',
    loss_rate: latest.loss_rate ?? '--',
    latency_ms: latest.latency_ms ?? '--',
    jitter_ms: latest.jitter_ms ?? '--'
  }
})

const echartsOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: { top: 0 },
  grid: { left: 40, right: 20, top: 40, bottom: 40 },
  xAxis: {
    type: 'category',
    data: chartRows.value.map((item) => item.timestamp?.slice(11) || item.timestamp)
  },
  yAxis: { type: 'value', splitLine: { lineStyle: { type: 'dashed' } } },
  series: [
    {
      name: '帧率',
      type: 'bar',
      data: chartRows.value.map((item) => item.fps ?? 0),
      itemStyle: { color: '#3b82f6' }
    },
    {
      name: '码率(kbps)',
      type: 'bar',
      data: chartRows.value.map((item) => item.bitrate_kbps ?? 0),
      itemStyle: { color: '#10b981' }
    },
    {
      name: '丢包率(%)',
      type: 'bar',
      data: chartRows.value.map((item) => item.loss_rate ?? 0),
      itemStyle: { color: '#f59e0b' }
    },
    {
      name: '延迟(ms)',
      type: 'bar',
      data: chartRows.value.map((item) => item.latency_ms ?? 0),
      itemStyle: { color: '#ef4444' }
    }
  ]
}))

const loadData = async () => {
  try {
    const data = await fetchVideoStreamData()
    if (Array.isArray(data)) {
      rows.value = data as VideoStreamDataItem[]
    }
  } catch (error) {
    console.error('加载视频流柱状图数据失败:', error)
  }
}

onMounted(() => {
  loadData()
  timer.value = window.setInterval(loadData, 5000)
})

onBeforeUnmount(() => {
  if (timer.value !== null) {
    window.clearInterval(timer.value)
    timer.value = null
  }
})
</script>

<style scoped>
.snapshot-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; margin-bottom: 1rem }
.snapshot-item {
  background: var(--art-main-bg-color);
  border: 1px solid var(--el-border-color);
  border-radius: 10px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.06);
}
.snapshot-label { font-size: 12px; color: var(--el-text-color-secondary) }
.snapshot-value { font-size: 24px; font-weight: 700; margin-top: 6px; color: var(--el-text-color-primary) }
</style>
