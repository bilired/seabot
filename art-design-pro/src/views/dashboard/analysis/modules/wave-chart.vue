<template>
  <div class="mb-6">
    <!-- 快照网格：名称在上，数值在下 -->
    <div class="snapshot-grid mb-4">
      <div v-for="opt in chartOptions" :key="opt.key" class="snapshot-item">
        <div class="snapshot-label">{{ opt.label }}</div>
        <div class="snapshot-value">
          <span>{{ snapshotMap[opt.key] ?? '--' }}</span>
        </div>
      </div>
    </div>

    <div class="flex items-center mb-3">
      <h4 class="text-2xl font-bold mr-6">实时水质监测</h4>
      <div class="flex flex-wrap gap-2">
        <ElButton
          v-for="opt in chartOptions"
          :key="opt.key"
          :type="selectedKey === opt.key ? 'primary' : 'default'"
          size="small"
          @click="selectedKey = opt.key"
          class="chart-option-btn"
        >
          {{ opt.label }}
        </ElButton>
      </div>
    </div>

    <VChart :option="echartsOption" autoresize style="width:100%; height:380px" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, reactive } from 'vue'
import { ElButton } from 'element-plus'
import { use } from 'echarts/core'
import VChart from 'vue-echarts'
import { LineChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, GridComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

use([LineChart, TitleComponent, TooltipComponent, GridComponent, LegendComponent, CanvasRenderer])

type DataKey = 'temp' | 'ph' | 'chlorophyll' | 'salinity' | 'oxygen' | 'conductivity' | 'turbidity' | 'cyanobacteria'

const chartOptions: { key: DataKey; label: string }[] = [
  { key: 'temp', label: '水温（°C）' },
  { key: 'ph', label: 'PH值' },
  { key: 'chlorophyll', label: '叶绿素浓度（μg/L）' },
  { key: 'salinity', label: '盐度' },
  { key: 'oxygen', label: '溶解氧（mg/L）' },
  { key: 'conductivity', label: '导电率（μS/cm）' },
  { key: 'turbidity', label: '浊度（NTU）' },
  { key: 'cyanobacteria', label: '蓝绿藻（cells/mL）' }
]

const selectedKey = ref<DataKey>('temp')

// 时间轴（示意）
const timeLabels = Array.from({ length: 24 }, (_, i) => `${i}:00`)

const dataMap = reactive<Record<DataKey, number[]>>({
  temp: Array.from({ length: 24 }, () => +(20 + Math.random() * 5).toFixed(2)),
  ph: Array.from({ length: 24 }, () => +(7 + Math.random() * 0.5).toFixed(2)),
  chlorophyll: Array.from({ length: 24 }, () => +(10 + Math.random() * 10).toFixed(2)),
  salinity: Array.from({ length: 24 }, () => +(30 + Math.random() * 5).toFixed(2)),
  oxygen: Array.from({ length: 24 }, () => +(6 + Math.random() * 2).toFixed(2)),
  conductivity: Array.from({ length: 24 }, () => +(400 + Math.random() * 200).toFixed(2)),
  turbidity: Array.from({ length: 24 }, () => +(1 + Math.random() * 5).toFixed(2)),
  cyanobacteria: Array.from({ length: 24 }, () => +(1000 + Math.random() * 500).toFixed(0))
})

const snapshotMap = computed<Record<DataKey, number | string>>(() => {
  const m = {} as Record<DataKey, number | string>
  chartOptions.forEach((opt) => {
    const arr = dataMap[opt.key]
    m[opt.key] = arr && arr.length ? arr[arr.length - 1] : '--'
  })
  return m
})

let simTimer: number | undefined

function genNextValue(key: DataKey) {
  const arr = dataMap[key]
  const last = arr[arr.length - 1] ?? 0
  const delta = (Math.random() - 0.5) * (Math.abs(last) * 0.02 + 0.5)
  const next = +(Math.max(0, last + delta)).toFixed(Number.isInteger(last) ? 0 : 2)
  return next
}

function simulateUpdate() {
  ;(Object.keys(dataMap) as DataKey[]).forEach((k) => {
    dataMap[k].push(genNextValue(k))
    if (dataMap[k].length > 24) dataMap[k].shift()
  })
}

function startSimulation(interval = 5000) {
  stopSimulation()
  simulateUpdate()
  simTimer = window.setInterval(simulateUpdate, interval)
}

function stopSimulation() {
  if (simTimer) {
    clearInterval(simTimer)
    simTimer = undefined
  }
}

onMounted(() => startSimulation(5000))
onBeforeUnmount(() => stopSimulation())

const echartsOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 40, right: 20, top: 40, bottom: 40 },
  xAxis: {
    type: 'category',
    data: timeLabels,
    boundaryGap: false
  },
  yAxis: {
    type: 'value',
    splitLine: { lineStyle: { type: 'dashed' } }
  },
  series: [
    {
      name: chartOptions.find((opt) => opt.key === selectedKey.value)?.label,
      type: 'line',
      smooth: true,
      symbol: 'none',
      areaStyle: { color: 'rgba(0,123,255,0.08)' },
      lineStyle: { width: 3, color: '#409EFF' },
      data: dataMap[selectedKey.value]
    }
  ]
}))
</script>

<style scoped>
.snapshot-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; margin-bottom: 1rem }
.snapshot-item { background: #fff; border-radius: 10px; padding: 12px; display: flex; flex-direction: column; align-items: center; box-shadow: 0 1px 6px rgba(0,0,0,0.06) }
.snapshot-label { font-size: 12px; color: #6b6f73 }
.snapshot-value { font-size: 28px; font-weight: 700; margin-top: 6px }
/* keep option buttons stable size so selection styling doesn't shrink them */
.chart-option-btn {
  min-width: 120px !important;
  width: 120px !important;
  box-sizing: border-box !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  flex: 0 0 auto !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  padding: 6px 12px !important;
  gap: 4px !important;
}

/* Ensure when button becomes primary its padding/width don't change */
.chart-option-btn.el-button,
.chart-option-btn.el-button--default,
.chart-option-btn.el-button--primary {
  width: 120px !important;
  min-width: 120px !important;
  padding: 6px 12px !important;
}

/* fixed inner label to avoid width change when button style changes */
.btn-label {
  display: inline-block;
  width: 100%;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Fix: keep height identical before/after click */
.chart-option-btn,
.chart-option-btn.el-button,
.chart-option-btn.el-button--default,
.chart-option-btn.el-button--primary {
  height: 32px !important;
  line-height: 32px !important;
}

.chart-option-btn ::v-deep .el-button__content {
  height: 32px !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
}
</style>
