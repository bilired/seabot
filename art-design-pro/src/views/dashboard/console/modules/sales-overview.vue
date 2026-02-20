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
  /**
   * 访问量数据
   * 记录从12天前到今天的访问量统计
   */
  const data = [2, 3, 1, 4, 0, 6, 5,5, 4, 1, 1, 2]

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
   * X 轴日期标签 (从12天前开始到今天)
   */
  const xAxisData = generateDateLabels()
</script>
