<template>
  <div class="art-card h-128 p-5 mb-5 max-sm:mb-4">
    <div class="art-card-header">
      <div class="title">
        <h4>实时动态</h4>
        <p>新增<span class="text-success">+6</span></p>
      </div>
    </div>

    <div class="h-9/10 mt-2 overflow-hidden">
      <ElScrollbar>
        <div
          class="h-17.5 leading-17.5 border-b border-g-300 text-sm overflow-hidden last:border-b-0"
          v-for="(item, index) in list"
          :key="index"
        >
          <span class="text-g-800 font-medium">{{ item.shipName }}</span>
          <span class="mx-2 text-g-600">{{ item.event }}</span>
          <span class="text-theme">{{ item.description }}</span>
        </div>
      </ElScrollbar>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { onMounted, reactive } from 'vue'
  import { fetchUserActivity } from '@/api/dashboard'

  interface ShipEventItem {
    shipName: string
    event: string
    description: string
  }

  /**
   * 无人船事件动态列表
   * 记录无人船系统的实时事件和告警信息
   */
  const list = reactive<ShipEventItem[]>([
    {
      shipName: '1号船',
      event: '发现异常',
      description: '发现落水者'
    },
    {
      shipName: '2号船',
      event: '数据告警',
      description: '叶绿素含量超标'
    },
    {
      shipName: '3号船',
      event: '设备异常',
      description: '水温传感器故障'
    },
    {
      shipName: '4号船',
      event: '任务完成',
      description: '北区水质采样完成'
    },
    {
      shipName: '5号船',
      event: '数据告警',
      description: 'pH值异常升高'
    },
    {
      shipName: '6号船',
      event: '位置更新',
      description: '已到达目标区域'
    },
    {
      shipName: '7号船',
      event: '电池告警',
      description: '电量低于20%'
    },
    {
      shipName: '8号船',
      event: '设备异常',
      description: 'GPS信号弱'
    }
  ])

  /**
   * 从后端加载用户活动（可选，保持原有数据显示）
   */
  const loadUserActivity = async () => {
    try {
      const activities = await fetchUserActivity(8)
      if (activities && Array.isArray(activities)) {
        // 可以选择用后端数据替换，或保持原有数据
        console.log('后端活动数据:', activities)
      }
    } catch (error) {
      console.error('加载用户活动失败:', error)
    }
  }

  onMounted(() => {
    loadUserActivity()
  })
</script>
