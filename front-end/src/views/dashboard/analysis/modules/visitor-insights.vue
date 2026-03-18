<template>
  <div class="art-card h-82 p-5 mb-5 max-sm:mb-4">
    <div class="art-card-header">
      <div class="title">
        <h4>污染物监测趋势</h4>
      </div>
    </div>
    <ArtLineChart
      height="calc(100% - 30px)"
      :data="chartData"
      :xAxisData="xAxisData"
      :showLegend="true"
      :showAxisLabel="true"
      :showAxisLine="false"
      :showSplitLine="true"
    />
  </div>
</template>

<script setup lang="ts">
  import type { LineDataItem } from '@/types/component/chart'

  /**
   * X 轴数据配置
   * 表示一年的月份（1-12月）
   */
  const xAxisData = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']

  /**
   * 污染物监测趋势图表数据
   * 对比浊度和蓝绿藻的全年监测数据
   */
  const chartData = computed<LineDataItem[]>(() => [
    {
      name: '浊度(NTU)',
      data: [2.5, 3.2, 3.8, 2.1, 2.8, 4.5, 5.2, 4.8, 3.5, 2.9, 2.3, 2.0]
    },
    {
      name: '蓝绿藻(cells/mL)',
      data: [850, 1200, 2500, 1800, 2100, 3500, 4200, 3800, 2500, 1500, 950, 650]
    }
  ])
</script>
