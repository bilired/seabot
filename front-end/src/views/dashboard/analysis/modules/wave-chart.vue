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
      <h4 class="text-2xl font-bold mr-6">{{ chartTitle }}</h4>
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
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { ElButton } from 'element-plus'
import { use } from 'echarts/core'
import VChart from 'vue-echarts'
import { LineChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, GridComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { fetchNutrientData, fetchWaterQualityData } from '@/api/dashboard'

use([LineChart, TitleComponent, TooltipComponent, GridComponent, LegendComponent, CanvasRenderer])

type WaterDataKey =
  | 'temp'
  | 'ph'
  | 'chlorophyll'
  | 'salinity'
  | 'oxygen'
  | 'conductivity'
  | 'turbidity'
  | 'cyanobacteria'

type NutrientDataKey =
  | 'phosphate'
  | 'ammonia'
  | 'nitrate'
  | 'nitrite'

type DataKey = WaterDataKey | NutrientDataKey

interface WaterQualityDataItem {
  shipModel: string
  temperature: number
  ph: number
  chlorophyll: number
  salinity: number
  dissolvedOxygen: number
  conductivity: number
  turbidity: number
  algae: number
  collectionTime: string
}

interface NutrientDataItem {
  shipModel: string
  phosphate: number
  phosphateTime: string
  ammonia: number
  ammoniaTime: string
  nitrate: number
  nitrateTime: string
  nitrite: number
  nitriteTime: string
  collectionTime: string
}

const props = withDefaults(
  defineProps<{
    selectedModel?: string
    dataType?: 'water' | 'nutrients'
  }>(),
  {
    selectedModel: '',
    dataType: 'water'
  }
)

const waterChartOptions: { key: WaterDataKey; label: string }[] = [
  { key: 'temp', label: '水温（°C）' },
  { key: 'ph', label: 'PH值' },
  { key: 'chlorophyll', label: '叶绿素浓度（μg/L）' },
  { key: 'salinity', label: '盐度' },
  { key: 'oxygen', label: '溶解氧（mg/L）' },
  { key: 'conductivity', label: '导电率（μS/cm）' },
  { key: 'turbidity', label: '浊度（NTU）' },
  { key: 'cyanobacteria', label: '蓝绿藻（cells/mL）' }
]

const nutrientChartOptions: { key: NutrientDataKey; label: string }[] = [
  { key: 'phosphate', label: '磷酸盐（mg/L）' },
  { key: 'ammonia', label: '氨氮（mg/L）' },
  { key: 'nitrate', label: '硝酸盐（mg/L）' },
  { key: 'nitrite', label: '亚硝酸盐（mg/L）' }
]

const chartOptions = computed(() =>
  props.dataType === 'water' ? waterChartOptions : nutrientChartOptions
)

const selectedKey = ref<DataKey>('temp')

const waterQualityDataList = ref<WaterQualityDataItem[]>([])
const nutrientDataList = ref<NutrientDataItem[]>([])

const normalizeModel = (value?: string) => (value || '').trim().toLowerCase()

const isModelMatched = (shipModel: string, selectedModel: string) => {
  const ship = normalizeModel(shipModel)
  const selected = normalizeModel(selectedModel)
  if (!selected) return true
  return ship === selected || ship.includes(selected) || selected.includes(ship)
}

const filteredWaterQualityDataList = computed(() => {
  if (!props.selectedModel) {
    return waterQualityDataList.value
  }

  return waterQualityDataList.value.filter((item) => isModelMatched(item.shipModel, props.selectedModel))
})

const filteredNutrientDataList = computed(() => {
  if (!props.selectedModel) {
    return nutrientDataList.value
  }

  return nutrientDataList.value.filter((item) => isModelMatched(item.shipModel, props.selectedModel))
})

const snapshotMap = computed<Record<string, number | string>>(() => {
  const map: Record<string, number | string> = {}
  chartOptions.value.forEach((option) => {
    map[option.key] = '--'
  })

  if (props.dataType === 'water') {
    const latest = filteredWaterQualityDataList.value[0]
    if (!latest) return map
    map.temp = latest.temperature
    map.ph = latest.ph
    map.chlorophyll = latest.chlorophyll
    map.salinity = latest.salinity
    map.oxygen = latest.dissolvedOxygen
    map.conductivity = latest.conductivity
    map.turbidity = latest.turbidity
    map.cyanobacteria = latest.algae
    return map
  }

  const latestNutrient = filteredNutrientDataList.value[0]
  if (!latestNutrient) return map
  map.phosphate = latestNutrient.phosphate
  map.ammonia = latestNutrient.ammonia
  map.nitrate = latestNutrient.nitrate
  map.nitrite = latestNutrient.nitrite
  return map
})

const MAX_POINTS = 10

const historyData = computed(() => {
  const source = props.dataType === 'water' ? filteredWaterQualityDataList.value : filteredNutrientDataList.value
  return [...source].reverse().slice(-MAX_POINTS)
})

const timeLabels = computed(() =>
  historyData.value.map((item) => item.collectionTime?.slice(11) || item.collectionTime)
)

const seriesDataMap = computed<Record<DataKey, number[]>>(() => {
  if (props.dataType === 'water') {
    const data = historyData.value as WaterQualityDataItem[]
    return {
      temp: data.map((item) => item.temperature),
      ph: data.map((item) => item.ph),
      chlorophyll: data.map((item) => item.chlorophyll),
      salinity: data.map((item) => item.salinity),
      oxygen: data.map((item) => item.dissolvedOxygen),
      conductivity: data.map((item) => item.conductivity),
      turbidity: data.map((item) => item.turbidity),
      cyanobacteria: data.map((item) => item.algae),
      phosphate: [],
      ammonia: [],
      nitrate: [],
      nitrite: []
    }
  }

  const data = historyData.value as NutrientDataItem[]
  return {
    temp: [],
    ph: [],
    chlorophyll: [],
    salinity: [],
    oxygen: [],
    conductivity: [],
    turbidity: [],
    cyanobacteria: [],
    phosphate: data.map((item) => item.phosphate),
    ammonia: data.map((item) => item.ammonia),
    nitrate: data.map((item) => item.nitrate),
    nitrite: data.map((item) => item.nitrite)
  }
})

let refreshTimer: number | undefined

async function loadWaterQualityData() {
  try {
    const data = await fetchWaterQualityData()
    if (Array.isArray(data)) {
      waterQualityDataList.value = data
    }
  } catch (error) {
    console.error('加载水质曲线数据失败:', error)
  }
}

async function loadNutrientData() {
  try {
    const data = await fetchNutrientData()
    if (Array.isArray(data)) {
      nutrientDataList.value = data
    }
  } catch (error) {
    console.error('加载营养盐曲线数据失败:', error)
  }
}

function startAutoRefresh(interval = 5000) {
  stopAutoRefresh()
  loadWaterQualityData()
  loadNutrientData()
  refreshTimer = window.setInterval(() => {
    loadWaterQualityData()
    loadNutrientData()
  }, interval)
}

function stopAutoRefresh() {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = undefined
  }
}

onMounted(() => startAutoRefresh(5000))
onBeforeUnmount(() => stopAutoRefresh())

watch(
  () => props.dataType,
  (type) => {
    selectedKey.value = type === 'water' ? 'temp' : 'phosphate'
  },
  { immediate: true }
)

const chartTitle = computed(() =>
  props.dataType === 'water' ? '实时水质监测' : '实时营养盐监测'
)

const echartsOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 40, right: 20, top: 40, bottom: 40 },
  xAxis: {
    type: 'category',
    data: timeLabels.value,
    boundaryGap: false
  },
  yAxis: {
    type: 'value',
    splitLine: { lineStyle: { type: 'dashed' } }
  },
  series: [
    {
      name: chartOptions.value.find((opt) => opt.key === selectedKey.value)?.label,
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      label: {
        show: true,
        position: 'top',
        formatter: ({ value }: { value: number }) =>
          Number.isFinite(value) ? Number(value).toFixed(2).replace(/\.00$/, '') : '--'
      },
      areaStyle: { color: 'rgba(0,123,255,0.08)' },
      lineStyle: { width: 3, color: '#409EFF' },
      data: seriesDataMap.value[selectedKey.value]
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
