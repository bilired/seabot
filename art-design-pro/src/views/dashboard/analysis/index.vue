<!-- 分析页页面 -->
<template>
  <div>
    <WaveChart />

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
        <WaterQualityData />
      </ElCol>
    </ElRow>
  </div>
</template>

<script setup lang="ts">
import WaveChart from './modules/wave-chart.vue'
import TotalRevenue from './modules/total-revenue.vue'
import CustomerSatisfaction from './modules/customer-satisfaction.vue'
import TargetVsReality from './modules/target-vs-reality.vue'
import WaterQualityData from './modules/water-quality-data.vue'

defineOptions({ name: 'Analysis' })
</script>
