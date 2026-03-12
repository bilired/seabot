<template>
  <div class="image-transfer-history-page art-full-height">
    <ElCard class="art-table-card" shadow="never">
      <ElForm :inline="true" :model="searchForm" class="mb-4">
        <ElFormItem label="型号">
          <ElSelect v-model="searchForm.model" placeholder="全部型号" clearable filterable style="width: 180px">
            <ElOption v-for="model in modelOptions" :key="model" :label="model" :value="model" />
          </ElSelect>
        </ElFormItem>
        <ElFormItem label="图片唯一标识">
          <ElInput v-model="searchForm.imageUid" placeholder="请输入唯一标识" clearable style="width: 220px" />
        </ElFormItem>
        <ElFormItem label="图片格式">
          <ElSelect v-model="searchForm.format" placeholder="全部" clearable style="width: 140px">
            <ElOption v-for="item in formatOptions" :key="item" :label="item.toUpperCase()" :value="item" />
          </ElSelect>
        </ElFormItem>
        <ElFormItem label="时间范围">
          <ElDatePicker
            v-model="searchForm.timeRange"
            type="datetimerange"
            value-format="YYYY-MM-DD HH:mm:ss"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            style="width: 360px"
          />
        </ElFormItem>
        <ElFormItem>
          <ElSpace>
            <ElButton type="primary" @click="handleSearch" v-ripple>查询</ElButton>
            <ElButton @click="handleReset" v-ripple>刷新</ElButton>
          </ElSpace>
        </ElFormItem>
      </ElForm>

      <ArtTableHeader v-model:columns="columnChecks" :loading="loading" @refresh="refreshData">
        <template #left>
          <ElSpace wrap>
            <ElButton type="danger" :disabled="selectedRows.length === 0" @click="handleBatchDelete" v-ripple>
              批量删除 {{ selectedRows.length > 0 ? `(${selectedRows.length})` : '' }}
            </ElButton>
          </ElSpace>
        </template>
      </ArtTableHeader>

      <ArtTable
        :loading="loading"
        :data="(data as Record<string, unknown>[])"
        :columns="columns"
        :pagination="pagination"
        @selection-change="handleSelectionChange"
        @pagination:size-change="handleSizeChange"
        @pagination:current-change="handleCurrentChange"
      />

      <ElImageViewer
        v-if="previewVisible"
        :url-list="previewUrl ? [previewUrl] : []"
        :initial-index="0"
        @close="previewVisible = false"
      />
    </ElCard>
  </div>
</template>

<script setup lang="ts">
  import { ref, reactive, h, onMounted } from 'vue'
  import { ElButton, ElImageViewer, ElMessage, ElMessageBox, ElTag } from 'element-plus'
  import ArtButtonTable from '@/components/core/forms/art-button-table/index.vue'
  import { useTable } from '@/hooks/core/useTable'
  import {
    fetchDroneList,
    fetchImageTransferHistory,
    deleteImageTransferRecord,
    batchDeleteImageTransferRecords,
    type ImageTransferItem
  } from '@/api/drone'

  defineOptions({ name: 'ImageTransferHistory' })

  const formatOptions = ['jpg', 'png', 'webp', 'tif']
  const modelOptions = ref<string[]>([])

  const selectedRows = ref<ImageTransferItem[]>([])
  const previewVisible = ref(false)
  const previewUrl = ref('')

  const searchForm = reactive({
    model: '',
    imageUid: '',
    format: '',
    timeRange: [] as string[]
  })

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
    core: {
      apiFn: fetchImageTransferHistory,
      apiParams: {
        current: 1,
        size: 10,
        model: undefined,
        imageUid: undefined,
        imageFormat: undefined,
        startTime: undefined,
        endTime: undefined
      },
      columnsFactory: () => [
        { type: 'selection', width: 50 },
        { type: 'index', width: 60, label: '序号' },
        { prop: 'id', label: 'ID', width: 90 },
        { prop: 'ship_model', label: '型号', minWidth: 120 },
        { prop: 'imageUid', label: '图片唯一标识', minWidth: 190 },
        { prop: 'timestamp', label: '时间戳', minWidth: 180 },
        {
          prop: 'imageFormat',
          label: '图片格式',
          width: 120,
          formatter: (row: ImageTransferItem) =>
            h(ElTag, { type: 'info' }, () => row.imageFormat.toUpperCase())
        },
        { prop: 'resolution', label: '分辨率', width: 130 },
        {
          prop: 'fileSizeMB',
          label: '文件大小(MB)',
          width: 140,
          formatter: (row: ImageTransferItem) => row.fileSizeMB.toFixed(2)
        },
        {
          prop: 'operation',
          label: '操作',
          fixed: 'right',
          width: 140,
          formatter: (row: ImageTransferItem) =>
            h('div', { class: 'flex items-center gap-1' }, [
              h(
                ElButton,
                {
                  type: 'primary',
                  plain: true,
                  size: 'small',
                  onClick: () => handleView(row)
                },
                () => '查看'
              ),
              h(ArtButtonTable, {
                type: 'delete',
                onClick: () => handleDelete(row)
              })
            ])
        }
      ]
    }
  })

  const handleSelectionChange = (selection: ImageTransferItem[]) => {
    selectedRows.value = selection
  }

  const loadModelOptions = async () => {
    try {
      const response = await fetchDroneList({ current: 1, size: 100 })
      const records = response?.records ?? response?.data?.records
      const models = Array.isArray(records) ? records.map((item: { model?: string }) => item.model) : []
      modelOptions.value = [...new Set(models.filter((model): model is string => Boolean(model)))]
    } catch (error) {
      console.error('加载设备型号列表失败:', error)
    }
  }

  const handleSearch = () => {
    const [startTime, endTime] = searchForm.timeRange.length === 2 ? searchForm.timeRange : [undefined, undefined]

    Object.assign(searchParams, {
      current: 1,
      model: searchForm.model || undefined,
      imageUid: searchForm.imageUid || undefined,
      imageFormat: searchForm.format || undefined,
      startTime,
      endTime
    })
    getData()
  }

  const handleReset = () => {
    searchForm.model = ''
    searchForm.imageUid = ''
    searchForm.format = ''
    searchForm.timeRange = []
    resetSearchParams()
    getData()
  }

  const handleView = (row: ImageTransferItem) => {
    previewUrl.value = row.imageUrl
    previewVisible.value = true
  }

  const handleDelete = (row: ImageTransferItem) => {
    ElMessageBox.confirm(`确认删除记录 ${row.imageUid} 吗？`, '删除确认', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    }).then(async () => {
      await deleteImageTransferRecord({ id: row.id })
      ElMessage.success('删除成功')
      refreshData()
    })
  }

  const handleBatchDelete = () => {
    const ids = selectedRows.value.map((item) => item.id)
    ElMessageBox.confirm(`确认删除已选中的 ${ids.length} 条记录吗？`, '批量删除确认', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    }).then(async () => {
      await batchDeleteImageTransferRecords({ ids })
      selectedRows.value = []
      ElMessage.success('批量删除成功')
      refreshData()
    })
  }

  onMounted(() => {
    loadModelOptions()
  })
</script>

<style scoped></style>
