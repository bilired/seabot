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
        :data="(data as Record<string, any>[])"
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

      <!-- 添加设备对话框 -->
      <ElDialog v-model="addDialogVisible" title="添加新设备" width="500px" @close="resetForm">
        <ElForm :model="formData" :rules="formRules" ref="formRef" label-width="100px">
          <ElFormItem label="船型" prop="shipType">
            <ElInput v-model="formData.shipType" placeholder="例如：双体" />
          </ElFormItem>
          <ElFormItem label="型号" prop="model">
            <ElInput v-model="formData.model" placeholder="例如：DL-3022" />
          </ElFormItem>
          <ElFormItem label="长度(m)" prop="length">
            <ElInputNumber v-model.number="formData.length" :min="0" :step="1" />
          </ElFormItem>
          <ElFormItem label="重量(kg)" prop="weight">
            <ElInputNumber v-model.number="formData.weight" :min="0" :step="0.1" />
          </ElFormItem>
          <ElFormItem label="最高航速(节)" prop="maxSpeed">
            <ElInputNumber v-model.number="formData.maxSpeed" :min="0" :step="0.5" />
          </ElFormItem>
          <ElFormItem label="功能模块" prop="functions">
            <ElInput v-model="formData.functions" placeholder="例如：图传、采样、水质监测" />
          </ElFormItem>
        </ElForm>
        <template #footer>
          <ElButton @click="addDialogVisible = false">取消</ElButton>
          <ElButton type="primary" @click="submitAddDevice" :loading="submitting">提交</ElButton>
        </template>
      </ElDialog>
    </ElCard>
  </div>
</template>

<script setup lang="ts">
  import { ref, onMounted, h } from 'vue'
  import ArtButtonTable from '@/components/core/forms/art-button-table/index.vue'
  import { useTable } from '@/hooks/core/useTable'
  import type { ColumnOption } from '@/types/component'
  import type { FormInstance } from 'element-plus'
  import { ElTag, ElButton, ElSpace, ElMessage, ElMessageBox, ElDialog, ElForm, ElFormItem, ElInput, ElInputNumber } from 'element-plus'
  import { Icon } from '@iconify/vue'
  import { fetchDroneList, batchDeleteDrone, createDrone, type DroneItem } from '@/api/drone'
  import ControlDialog from './modules/control-dialog.vue'
  import TrackDialog from './modules/track-dialog.vue'
  import DeviceDetailModal from '@/views/dashboard/console/modules/device-detail.vue'

  defineOptions({ name: 'DroneManage' })

  // 选中行
  const selectedRows = ref<DroneItem[]>([])

  // 控制对话框状态
  const controlDialogVisible = ref(false)
  const currentDevice = ref<DroneItem | null>(null)

  // 轨迹查询对话框状态
  const trackDialogVisible = ref(false)

  // 设备详情对话框状态
  const detailDialogVisible = ref(false)

  // 添加设备对话框状态
  const addDialogVisible = ref(false)
  const formRef = ref<FormInstance>()
  const submitting = ref(false)
  const formData = ref({
    shipType: '',
    model: '',
    length: 0,
    weight: 0,
    maxSpeed: 0,
    functions: ''
  })

  // 表单验证规则
  const formRules = {
    shipType: [{ required: true, message: '请输入船型', trigger: 'blur' }],
    model: [{ required: true, message: '请输入型号', trigger: 'blur' }],
    length: [{ required: true, message: '请输入长度', trigger: 'blur' }],
    weight: [{ required: true, message: '请输入重量', trigger: 'blur' }],
    maxSpeed: [{ required: true, message: '请输入最高航速', trigger: 'blur' }],
    functions: [{ required: true, message: '请输入功能模块', trigger: 'blur' }]
  }

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
      columnsFactory: (() => [
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
          formatter: (row: DroneItem) => {
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
          formatter: (row: DroneItem) =>
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
      ]) as any
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
    resetForm()
    addDialogVisible.value = true
  }

  /**
   * 重置表单
   */
  const resetForm = () => {
    formRef.value?.resetFields()
    formData.value = {
      shipType: '',
      model: '',
      length: 0,
      weight: 0,
      maxSpeed: 0,
      functions: ''
    }
  }

  /**
   * 提交添加设备
   */
  const submitAddDevice = async () => {
    if (!formRef.value) return

    try {
      await formRef.value.validate()
      submitting.value = true

      // 调用后端 API 创建设备
      const response = (await createDrone({
        shipType: formData.value.shipType,
        model: formData.value.model,
        length: formData.value.length,
        weight: formData.value.weight,
        maxSpeed: formData.value.maxSpeed,
        functions: formData.value.functions,
        status: 'offline'
      })) as any

      // createDrone 返回的是 { id: "..." } 对象
      // 如果没有异常，说明创建成功
      ElMessage.success('设备添加成功')
      addDialogVisible.value = false
      // 刷新设备列表
      await refreshData()
    } catch (e) {
      console.error('添加设备异常:', e)
      // HttpError 包含 message 属性
      const errorMsg = (e as any)?.message || '添加设备失败，请重试'
      ElMessage.error(errorMsg)
    } finally {
      submitting.value = false
    }
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
