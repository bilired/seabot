<template>
  <div class="art-card h-105 p-4 box-border mb-5 max-sm:mb-4">
    <div class="art-card-header mb-4">
      <div class="title">
        <h4>设备管理</h4>
        <p>共 <span class="text-success">{{ data.length }}</span> 台设备</p>
      </div>
    </div>
    
    <div v-if="loading" class="flex items-center justify-center h-80">
      <ElSkeleton :rows="5" animated />
    </div>
    <ElTable v-else :data="(data as Record<string, any>[])" stripe max-height="calc(100% - 60px)" size="small">
      <ElTableColumn prop="shipType" label="船型" width="80" align="center" />
      <ElTableColumn prop="length" label="长度" width="80" align="center" />
      <ElTableColumn prop="model" label="型号" width="100" align="center" />
      <ElTableColumn prop="weight" label="重量(kg)" width="100" align="center" />
      <ElTableColumn prop="functions" label="功能模块" show-overflow-tooltip />
      <ElTableColumn prop="status" label="设备状态" width="140" align="center">
        <template #default="{ row }">
          <div class="flex items-center justify-center gap-2">
            <span :class="row.status === 'online' ? 'text-success' : 'text-danger'">
              {{ row.status === 'online' ? '在线' : '离线' }}
            </span>
            <!-- changed: 点击详情打开弹窗 -->
            <ElButton link type="primary" size="small" @click="openDetails(row)">详情</ElButton>
          </div>
        </template>
      </ElTableColumn>
      <ElTableColumn prop="maxSpeed" label="最高航速(节)" width="110" align="center" />
    </ElTable>

    <!-- 设备详情组件 -->
    <DeviceDetail v-model:visible="dialogVisible" :device="selectedDevice" />
  </div>
</template>

<script setup lang="ts">
  import { ref } from 'vue'
  import { ElMessage, ElSkeleton } from 'element-plus'
  import DeviceDetail from './device-detail.vue'
  import { fetchDroneList, type DroneItem } from '@/api/drone'
  import { useTable } from '@/hooks/core/useTable'
  import type { ColumnOption } from '@/types/component'
  import { h } from 'vue'

  defineOptions({ name: 'DashboardDeviceManager' })

  const dialogVisible = ref(false)
  const selectedDevice = ref<DroneItem | null>(null)

  // 使用 useTable Hook 加载数据，与无人船设备管理页面保持一致
  const { data, loading, pagination } = useTable({
    core: {
      apiFn: fetchDroneList,
      apiParams: {
        current: 1,
        size: 100
      },
      columnsFactory: (() => [
        { prop: 'shipType', label: '船型', width: 80, align: 'center' },
        { prop: 'length', label: '长度', width: 80, align: 'center' },
        { prop: 'model', label: '型号', width: 100, align: 'center' },
        { prop: 'weight', label: '重量(kg)', width: 100, align: 'center' },
        { prop: 'functions', label: '功能模块', show_overflow_tooltip: true },
        {
          prop: 'status',
          label: '设备状态',
          width: 140,
          align: 'center',
          formatter: (row: DroneItem) => {
            const statusText = row.status === 'online' ? '在线' : '离线'
            const statusColor = row.status === 'online' ? 'text-success' : 'text-danger'
            return h('div', { class: 'flex items-center justify-center gap-2' }, [
              h('span', { class: statusColor }, statusText),
              h(
                'button',
                {
                  class: 'text-primary cursor-pointer hover:underline',
                  onClick: () => openDetails(row)
                },
                '详情'
              )
            ])
          }
        },
        { prop: 'maxSpeed', label: '最高航速(节)', width: 110, align: 'center' }
      ]) as any
    },
    performance: {
      enableCache: false // 禁用缓存，保证实时数据
    }
  })

  function openDetails(row: DroneItem) {
    try {
      selectedDevice.value = JSON.parse(JSON.stringify(row))
    } catch (e) {
      selectedDevice.value = row
    }
    dialogVisible.value = true
  }
</script>
