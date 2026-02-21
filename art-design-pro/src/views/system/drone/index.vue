<!-- 无人船设备管理页面 -->
<template>
  <div class="drone-page art-full-height">
    <ElCard class="art-table-card" shadow="never">
      <!-- 表格头部 -->
      <ArtTableHeader v-model:columns="columnChecks" :loading="loading" @refresh="refreshData">
        <template #left>
          <ElSpace wrap>
            <ElButton type="primary" @click="handleAdd" v-ripple>
              <template #icon>
                <Icon icon="ri:add-line" />
              </template>
              添加
            </ElButton>
            <ElButton 
              type="danger" 
              @click="handleBatchDelete" 
              :disabled="selectedRows.length === 0"
              v-ripple
            >
              <template #icon>
                <Icon icon="ri:delete-bin-line" />
              </template>
              删除 {{ selectedRows.length > 0 ? `(${selectedRows.length})` : '' }}
            </ElButton>
            <ElButton @click="refreshData" v-ripple>
              <template #icon>
                <Icon icon="ri:refresh-line" />
              </template>
              刷新
            </ElButton>
          </ElSpace>
        </template>
      </ArtTableHeader>

      <!-- 表格 -->
      <ArtTable
        :loading="loading"
        :data="data"
        :columns="columns"
        :pagination="pagination"
        @selection-change="handleSelectionChange"
        @pagination:size-change="handleSizeChange"
        @pagination:current-change="handleCurrentChange"
      >
      </ArtTable>

      <!-- 控制对话框 -->
      <ControlDialog
        v-model:visible="controlDialogVisible"
        :device-data="currentDevice"
      />

      <!-- 轨迹查询对话框 -->
      <TrackDialog
        v-model:visible="trackDialogVisible"
        :device-data="currentDevice"
      />

      <!-- 设备详情对话框 -->
      <DeviceDetailModal
        v-model:visible="detailDialogVisible"
        :device="currentDevice"
      />
    </ElCard>
  </div>
</template>

<script setup lang="ts">
  import ArtButtonTable from '@/components/core/forms/art-button-table/index.vue'
  import { useTable } from '@/hooks/core/useTable'
  import { ElTag, ElButton, ElSpace, ElMessage, ElMessageBox } from 'element-plus'
  import { Icon } from '@iconify/vue'
  import { fetchDroneList, batchDeleteDrone } from '@/api/drone'
  import ControlDialog from './modules/control-dialog.vue'
  import TrackDialog from './modules/track-dialog.vue'
  import DeviceDetailModal from '@/views/dashboard/console/modules/device-detail.vue'

  defineOptions({ name: 'DroneManage' })

  interface DroneItem {
    id: string
    shipType: string
    length: number
    model: string
    weight: number
    functions: string
    status: 'online' | 'offline'
    maxSpeed: number
  }

  // 选中行
  const selectedRows = ref<DroneItem[]>([])

  // 控制对话框状态
  const controlDialogVisible = ref(false)
  const currentDevice = ref<DroneItem | null>(null)

  // 轨迹查询对话框状态
  const trackDialogVisible = ref(false)

  // 设备详情对话框状态
  const detailDialogVisible = ref(false)

  // 设备状态配置
  const DEVICE_STATUS_CONFIG = {
    online: { type: 'success' as const, text: '在线' },
    offline: { type: 'danger' as const, text: '离线' }
  } as const

  /**
   * 获取设备状态配置
   */
  const getDeviceStatusConfig = (status: 'online' | 'offline') => {
    return DEVICE_STATUS_CONFIG[status] || { type: 'info' as const, text: '未知' }
  }

  const {
    columns,
    columnChecks,
    data,
    loading,
    pagination,
    getData,
    searchParams,
    resetSearchParams,
    handleSizeChange,
    handleCurrentChange,
    refreshData
  } = useTable({
    // 核心配置
    core: {
      apiFn: fetchDroneList,
      apiParams: {
        current: 1,
        size: 10
      },
      columnsFactory: () => [
        { type: 'selection', width: 50 }, // 勾选列
        { 
          prop: 'id', 
          label: 'ID',
          width: 120
        },
        { 
          prop: 'shipType', 
          label: '船型',
          width: 100
        },
        {
          prop: 'length',
          label: '长度 (cm)',
          width: 120
        },
        { 
          prop: 'model', 
          label: '型号',
          width: 120
        },
        {
          prop: 'weight',
          label: '重量 (kg)',
          width: 120
        },
        {
          prop: 'functions',
          label: '功能模块',
          minWidth: 200
        },
        {
          prop: 'status',
          label: '设备状态',
          width: 150,
          formatter: (row) => {
            const statusConfig = getDeviceStatusConfig(row.status)
            return h('div', { class: 'flex items-center gap-2' }, [
              h(ElTag, { type: statusConfig.type }, () => statusConfig.text),
              h(
                'a',
                {
                  class: 'text-primary cursor-pointer hover:underline',
                  onClick: () => handleDetail(row)
                },
                '详情'
              )
            ])
          }
        },
        {
          prop: 'maxSpeed',
          label: '最高航速(节)',
          width: 140
        },
        {
          prop: 'operation',
          label: '操作',
          width: 200,
          fixed: 'right',
          formatter: (row) =>
            h('div', { class: 'flex gap-2' }, [
              h(
                ElButton,
                {
                  type: 'primary',
                  link: true,
                  onClick: () => handleControl(row)
                },
                () => [
                  h(Icon, { icon: 'ri:eye-line', class: 'mr-1' }),
                  '控制'
                ]
              ),
              h(
                ElButton,
                {
                  type: 'warning',
                  link: true,
                  onClick: () => handleTrack(row)
                },
                () => [
                  h(Icon, { icon: 'ri:route-line', class: 'mr-1' }),
                  '轨迹查询'
                ]
              )
            ])
        }
      ]
    }
  })

  /**
   * 处理选择改变
   */
  const handleSelectionChange = (rows: DroneItem[]) => {
    selectedRows.value = rows
  }

  /**
   * 添加设备
   */
  const handleAdd = () => {
    ElMessage.info('添加设备功能')
  }

  /**
   * 查看详情
   */
  const handleDetail = (row: DroneItem) => {
    const displayStatus = row.status === 'online' ? '在线' : '离线'
    // 创建一个新对象用于显示，保持原始状态用于其他操作
    const deviceDetail = {
      ...row,
      displayStatus,
      image: undefined
    }
    currentDevice.value = row // 传递原始数据
    detailDialogVisible.value = true
  }

  /**
   * 控制设备
   */
  const handleControl = (row: DroneItem) => {
    currentDevice.value = row
    controlDialogVisible.value = true
  }

  /**
   * 轨迹查询
   */
  const handleTrack = (row: DroneItem) => {
    currentDevice.value = row
    trackDialogVisible.value = true
  }

  /**
   * 批量删除设备
   */
  const handleBatchDelete = () => {
    if (selectedRows.value.length === 0) {
      ElMessage.warning('请先选择要删除的设备')
      return
    }

    const deviceIds = selectedRows.value.map(item => item.id).join('、')
    const count = selectedRows.value.length
    
    ElMessageBox.confirm(
      `确定要删除选中的 ${count} 个设备吗？\n设备ID: ${deviceIds}\n\n此操作不可恢复。`,
      '批量删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        draggable: true
      }
    )
      .then(async () => {
        const ids = selectedRows.value.map((item) => item.id)
        await batchDeleteDrone({ ids })
        ElMessage.success(`成功删除 ${count} 个设备`)
        selectedRows.value = []
        refreshData()
      })
      .catch(() => {
        ElMessage.info('已取消删除')
      })
  }

  // 初始加载数据
  onMounted(() => {
    getData()
  })
</script>

<style scoped lang="scss">
  .drone-page {
    padding: 16px;
  }
</style>
