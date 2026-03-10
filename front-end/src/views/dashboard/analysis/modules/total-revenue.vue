<template>
  <div class="art-card h-100 p-5 mb-5 max-sm:mb-4">
    <div class="art-card-header">
      <div class="title">
        <h4>周水质变化趋势</h4>
      </div>
    </div>
    <ArtBarChart
      height="calc(100% - 30px)"
      :data="waterQualityTrend"
      :xAxisData="weekDays"
      :showLegend="true"
      :showAxisLine="false"
      barWidth="18%"
    />
  </div>
</template>

<script setup lang="ts">
  interface WaterQualityTrendItem {
    name: string
    data: number[]
  }

  /**
   * 一周的日期标签
   */
  const weekDays = ref(['周一', '周二', '周三', '周四', '周五', '周六', '周日'])

  /**
   * 周水质变化趋势
   * 对比溶解氧和导电率的一周变化情况
   */
  const waterQualityTrend = ref<WaterQualityTrendItem[]>([
    {
      name: '溶解氧(mg/L)',
      data: [8.2, 8.1, 8.3, 8.0, 8.4, 8.2, 8.1]
    },
    {
      name: '导电率(μS/cm)',
      data: [450, 455, 440, 460, 445, 450, 455]
    }
  ])
</script>
