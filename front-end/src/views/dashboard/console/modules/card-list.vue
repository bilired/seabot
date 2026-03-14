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
  import { fetchDeviceStatus } from '@/api/drone'

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

  // 在线设备数通过 device-status SSE 实时更新
  let statusStream: EventSource | null = null

  async function initOnlineCount() {
    // 先用 HTTP 请求填充初始值，避免 SSE 连接建立前短暂显示 0
    try {
      const statuses = await fetchDeviceStatus()
      if (Array.isArray(statuses)) {
        dataList[0].num = statuses.filter((s) => !!s.online).length
      }
    } catch {
      // 忽略，由 SSE 兜底
    }
  }

  function startOnlineCountStream() {
    if (statusStream) {
      statusStream.close()
      statusStream = null
    }

    statusStream = new EventSource('/api/ship/device-status/?stream=1')

    statusStream.addEventListener('device-status', (evt: Event) => {
      const msg = evt as MessageEvent
      try {
        const statuses = JSON.parse(msg.data)
        if (Array.isArray(statuses)) {
          dataList[0].num = statuses.filter((s: any) => !!s.online).length
        }
      } catch {
        // ignore parse errors
      }
    })
  }

  onMounted(() => {
    loadDashboardStats()
    initOnlineCount()
    startOnlineCountStream()
  })

  onBeforeUnmount(() => {
    if (statusStream) {
      statusStream.close()
      statusStream = null
    }
  })
</script>
