<template>
  <div class="art-card h-105 p-4 box-border mb-5 max-sm:mb-4">
    <div class="art-card-header mb-4">
      <div class="title">
        <h4>设备管理</h4>
        <p>共 <span class="text-success">{{ deviceList.length }}</span> 台设备</p>
      </div>
    </div>
    
    <ElTable :data="deviceList" stripe max-height="calc(100% - 60px)" size="small">
      <ElTableColumn prop="shipType" label="船型" width="80" align="center" />
      <ElTableColumn prop="length" label="长度" width="80" align="center" />
      <ElTableColumn prop="model" label="型号" width="100" align="center" />
      <ElTableColumn prop="weight" label="重量(kg)" width="100" align="center" />
      <ElTableColumn prop="functions" label="功能模块" show-overflow-tooltip />
      <ElTableColumn prop="status" label="设备状态" width="140" align="center">
        <template #default="{ row }">
          <div class="flex items-center justify-center gap-2">
            <span :class="row.status === '在线' ? 'text-success' : 'text-danger'">
              {{ row.status }}
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
  import { ref, watch } from 'vue'
  import DeviceDetail from './device-detail.vue'

  interface DeviceItem {
    shipType: string
    length: number
    model: string
    weight: number
    functions: string
    status: string
    maxSpeed: number
    image?: string
  }

  /**
   * 无人船设备列表
   * 显示各设备的基本信息和状态
   */
  const dialogVisible = ref(false)
  const selectedDevice = ref<DeviceItem | null>(null)

  function openDetails(row: DeviceItem) {
    console.log('openDetails called', row)
    // clone to a plain object to avoid passing a reactive Proxy
    try {
      selectedDevice.value = JSON.parse(JSON.stringify(row))
    } catch (e) {
      // fallback: assign as-is
      selectedDevice.value = row as any
    }
    dialogVisible.value = true
  }
  
  // debug watch
  watch(dialogVisible, (v) => console.log('dialogVisible ->', v))

   const deviceList: DeviceItem[] = [
    {
      shipType: '双体',
      length: 255,
      model: 'DL-3026',
      weight: 51,
      functions: '图传、采样、营养盐监测',
      status: '离线',
      maxSpeed: 14,
      image: 'https://via.placeholder.com/740x420?text=无人船+DL-3026'
    },
    {
      shipType: '双体',
      length: 220,
      model: 'DL-3022',
      weight: 44,
      functions: '图传、采样、多参数水质监测',
      status: '离线',
      maxSpeed: 12,
      image: 'https://via.placeholder.com/740x420?text=无人船+DL-3022'
    }
  ]
</script>
