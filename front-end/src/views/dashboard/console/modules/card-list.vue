<template>
  <ElRow :gutter="20" class="flex">
    <ElCol v-for="(item, index) in dataList" :key="index" :sm="12" :md="6" :lg="6">
      <div class="art-card relative flex flex-col justify-center h-35 px-5 mb-5 max-sm:mb-4">
        <span class="text-g-700 text-sm">{{ item.des }}</span>
        <ArtCountTo class="text-[26px] font-medium mt-2" :target="item.num" :duration="1300" />
        
        <div
          class="absolute top-0 bottom-0 right-5 m-auto size-12.5 rounded-xl flex-cc bg-theme/10"
        >
          <ArtSvgIcon :icon="item.icon" class="text-xl text-theme" />
        </div>
      </div>
    </ElCol>
  </ElRow>
</template>

<script setup lang="ts">
  import { onBeforeUnmount, onMounted, reactive } from 'vue'
  import { fetchDashboardStats } from '@/api/dashboard'
  import { subscribeDeviceStatus } from '@/hooks/core/use-device-status-poller'

  interface CardDataItem {
    des: string
    icon: string
    startVal: number
    duration: number
    num: number
  }

  /**
   * 卡片统计数据列表
   * 展示在线设备数、系统运行时长、月新增设备数和今日动态数等核心数据指标
   */
  const dataList = reactive<CardDataItem[]>([
    {
      des: '在线设备数',
      icon: 'ri:ship-line',
      startVal: 0,
      duration: 1000,
      num: 0,
     
    },
    {
      des: '系统运行时长(天)',
      icon: 'ri:time-line',
      startVal: 0,
      duration: 1000,
      num: 0,
   
    },
    {
      des: '月新增设备',
      icon: 'ri:add-circle-line',
      startVal: 0,
      duration: 1000,
      num: 0,
   
    },
    {
      des: '今日动态数',
      icon: 'ri:pulse-line',
      startVal: 0,
      duration: 1000,
      num: 0,
     
    }
  ])

  /**
   * 从后端加载仪表板数据（非在线设备数）
   */
  const loadDashboardStats = async () => {
    try {
      const data = await fetchDashboardStats()
      if (data) {
        dataList[1].num = data.systemUptime || 0
        dataList[2].num = data.monthlyNewDevices || 0
        dataList[3].num = data.todayActivities || 0
      }
    } catch (error) {
      console.error('加载仪表板数据失败:', error)
    }
  }

  let unsubscribeDeviceStatus: (() => void) | null = null

  function applyOnlineCount(statuses: Array<{ online?: boolean }>) {
    dataList[0].num = statuses.filter((s) => !!s.online).length
  }

  function startOnlineCountPolling() {
    stopOnlineCountPolling()
    unsubscribeDeviceStatus = subscribeDeviceStatus((statuses) => {
      applyOnlineCount(statuses)
    })
  }

  function stopOnlineCountPolling() {
    if (unsubscribeDeviceStatus) {
      unsubscribeDeviceStatus()
      unsubscribeDeviceStatus = null
    }
  }

  onMounted(() => {
    loadDashboardStats()
    startOnlineCountPolling()
  })

  onBeforeUnmount(() => {
    stopOnlineCountPolling()
  })
</script>
