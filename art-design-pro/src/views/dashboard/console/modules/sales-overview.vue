<template>
  <div class="art-card h-105 p-5 mb-5 max-sm:mb-4">
    <div class="art-card-header">
      <div class="title">
        <h4>系统运行时长</h4>
        <p>较昨日增长<span class="text-success">+15%</span></p>
      </div>
    </div>
    <div class="relative h-9/10 mt-2 overflow-hidden">
      <ArtLineChart
        height="calc(100% - 0px)"
        :data="data"
        :xAxisData="xAxisData"
        :showAreaColor="true"
        :showAxisLine="false"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
  import { onMounted, ref } from 'vue'
  import { fetchSalesData } from '@/api/dashboard'

  /**
   * 访问量数据
   */
  const data = ref<number[]>([2, 3, 1, 4, 0, 6, 5, 5, 4, 1, 1, 2])

  /**
   * 生成日期标签 (从12天前开始到今天)
   */
  function generateDateLabels(): string[] {
    const today = new Date()
    const startDate = new Date(today)
    startDate.setDate(startDate.getDate() - 11)
    
    const labels: string[] = []
    for (let i = 0; i < 12; i++) {
      const date = new Date(startDate)
      date.setDate(date.getDate() + i)
      const month = date.getMonth() + 1
      const day = date.getDate()
      labels.push(`${month}-${day}`)
    }
    return labels
  }

  /**
   * X 轴日期标签
   */
  const xAxisData = ref<string[]>(generateDateLabels())

  /**
   * 从后端加载销售数据
   */
  const loadSalesData = async () => {
    try {
      const response = await fetchSalesData()
      if (response.code === 200) {
        const apiData = response.data
        xAxisData.value = apiData.map(item => item.month)
        data.value = apiData.map(item => item.sales)
      }
    } catch (error) {
      console.error('加载销售数据失败:', error)
    }
  }

  onMounted(() => {
    loadSalesData()
  })
</script>
