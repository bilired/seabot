<!-- 分析页页面 -->
<template>
  <div>
    <div class="art-card p-4 mb-4 flex items-center gap-5 flex-wrap">
      <span class="text-sm text-gray-600">数据选择</span>
      <ElSelect
        v-model="activeDataType"
        style="width: 200px"
      >
        <ElOption label="水质数据" value="water" />
        <ElOption label="营养盐数据" value="nutrients" />
      </ElSelect>

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

    <WaveChart :selected-model="selectedModel" :data-type="activeDataType" />

    <ElRow :gutter="20" v-if="false">
      <ElCol :xl="10" :lg="10" :xs="24">
        <TotalRevenue />
      </ElCol>
      <ElCol :xl="7" :lg="7" :xs="24">
        <CustomerSatisfaction />
      </ElCol>
      <ElCol :xl="7" :lg="7" :xs="24">
        <TargetVsReality />
      </ElCol>
    </ElRow>

    <ElRow :gutter="20">
      <ElCol :xs="24">
        <WaterQualityData :selected-model="selectedModel" :data-type="activeDataType" />
      </ElCol>
    </ElRow>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { fetchDroneList } from '@/api/drone'
import WaveChart from './modules/wave-chart.vue'
import TotalRevenue from './modules/total-revenue.vue'
import CustomerSatisfaction from './modules/customer-satisfaction.vue'
import TargetVsReality from './modules/target-vs-reality.vue'
import WaterQualityData from './modules/water-quality-data.vue'

defineOptions({ name: 'Analysis' })

const selectedModel = ref('')
const activeDataType = ref<'water' | 'nutrients'>('water')
const deviceModelOptions = ref<string[]>([])

const loadDeviceModelOptions = async () => {
  try {
    const response = await fetchDroneList({ current: 1, size: 100 })
    const records = response?.records ?? response?.data?.records
    const models = Array.isArray(records) ? records.map((item: { model?: string }) => item.model) : []

    deviceModelOptions.value = [...new Set(models.filter((model): model is string => Boolean(model)))]

    if (!selectedModel.value && deviceModelOptions.value.length > 0) {
      selectedModel.value = deviceModelOptions.value[0]
    }
  } catch (error) {
    console.error('加载设备型号列表失败:', error)
  }
}

onMounted(() => {
  loadDeviceModelOptions()
})
</script>
