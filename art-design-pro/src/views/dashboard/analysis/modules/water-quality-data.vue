<template>
  <div class="art-card h-140 p-5 mb-5 max-sm:mb-4">
    <div class="art-card-header mb-4">
      <div class="title">
        <h4>实时监测数据</h4>
        <p>无人船上传数据</p>
      </div>
    </div>
    
    <div class="mb-4" v-if="props.dataType === 'water'">
        <ElTable 
          :data="pagedWaterQualityData" 
          stripe 
          max-height="450px"
          size="small"
          style="width: 100%"
        >
          <ElTableColumn prop="shipModel" label="型号" width="120" align="center" />
          <ElTableColumn prop="temperature" label="水温(°C)" width="130" align="center" />
          <ElTableColumn prop="ph" label="pH值" width="120" align="center" />
          <ElTableColumn prop="chlorophyll" label="叶绿素(μg/L)" width="150" align="center" />
          <ElTableColumn prop="salinity" label="盐度" width="120" align="center" />
          <ElTableColumn prop="dissolvedOxygen" label="溶解氧(mg/L)" width="150" align="center" />
          <ElTableColumn prop="conductivity" label="电导率(μS/cm)" width="160" align="center" />
          <ElTableColumn prop="turbidity" label="浊度(NTU)" width="130" align="center" />
          <ElTableColumn prop="algae" label="蓝绿藻(cells/mL)" width="160" align="center" />
          <ElTableColumn prop="collectionTime" label="采集时间" width="180" fixed="right" align="center" />
        </ElTable>
        <div class="mt-3 flex justify-end">
          <ElPagination
            v-model:current-page="waterCurrentPage"
            :page-size="pageSize"
            :total="filteredWaterQualityDataList.length"
            layout="total, prev, pager, next, jumper"
            background
          />
        </div>
    </div>

    <div class="mb-4" v-else>
        <ElTable 
          :data="pagedNutrientData" 
          stripe 
          max-height="450px"
          size="small"
          style="width: 100%"
        >
          <ElTableColumn prop="shipModel" label="型号" width="120" align="center" />
          <ElTableColumn prop="phosphate" label="磷酸盐(mg/L)" width="150" align="center" />
          <ElTableColumn prop="phosphateTime" label="磷酸盐获取时间" width="180" align="center" />
          <ElTableColumn prop="ammonia" label="氨氮" width="120" align="center" />
          <ElTableColumn prop="ammoniaTime" label="氨氮获取时间" width="180" align="center" />
          <ElTableColumn prop="nitrate" label="硝酸盐" width="120" align="center" />
          <ElTableColumn prop="nitrateTime" label="硝酸盐获取时间" width="180" align="center" />
          <ElTableColumn prop="nitrite" label="亚硝酸盐" width="130" align="center" />
          <ElTableColumn prop="nitriteTime" label="亚硝酸盐获取时间" width="180" align="center" />
          <ElTableColumn prop="collectionTime" label="采集时间" width="180" fixed="right" align="center" />
        </ElTable>
        <div class="mt-3 flex justify-end">
          <ElPagination
            v-model:current-page="nutrientCurrentPage"
            :page-size="pageSize"
            :total="filteredNutrientDataList.length"
            layout="total, prev, pager, next, jumper"
            background
          />
        </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
  import { fetchWaterQualityData, fetchNutrientData } from '@/api/dashboard'

  const props = withDefaults(
    defineProps<{
      selectedModel?: string
      dataType?: 'water' | 'nutrients'
    }>(),
    {
      selectedModel: '',
      dataType: 'water'
    }
  )

  interface WaterQualityDataItem {
    shipModel: string
    temperature: number
    ph: number
    chlorophyll: number
    salinity: number
    dissolvedOxygen: number
    conductivity: number
    turbidity: number
    algae: number
    collectionTime: string
  }

  interface NutrientDataItem {
    shipModel: string
    phosphate: number
    phosphateTime: string
    ammonia: number
    ammoniaTime: string
    nitrate: number
    nitrateTime: string
    nitrite: number
    nitriteTime: string
    collectionTime: string
  }

  const pageSize = 10
  const waterCurrentPage = ref(1)
  const nutrientCurrentPage = ref(1)

  /**
   * 无人船水质数据列表
   * 显示各船舶上传的实时水质监测数据
   */
  const waterQualityDataList = ref<WaterQualityDataItem[]>([])

  const normalizeModel = (value?: string) => (value || '').trim().toLowerCase()

  const isModelMatched = (shipModel: string, selectedModel: string) => {
    const ship = normalizeModel(shipModel)
    const selected = normalizeModel(selectedModel)
    if (!selected) return true
    return ship === selected || ship.includes(selected) || selected.includes(ship)
  }

  const filteredWaterQualityDataList = computed(() => {
    if (!props.selectedModel) {
      return waterQualityDataList.value
    }

    return waterQualityDataList.value.filter((item) => isModelMatched(item.shipModel, props.selectedModel))
  })

  const pagedWaterQualityData = computed(() => {
    const start = (waterCurrentPage.value - 1) * pageSize
    return filteredWaterQualityDataList.value.slice(start, start + pageSize)
  })

  /**
   * 营养盐数据列表
   * 显示各船舶上传的营养盐监测数据
   */
  const nutrientDataList = ref<NutrientDataItem[]>([])

  const filteredNutrientDataList = computed(() => {
    if (!props.selectedModel) {
      return nutrientDataList.value
    }

    return nutrientDataList.value.filter((item) => isModelMatched(item.shipModel, props.selectedModel))
  })

  const refreshTimer = ref<number | null>(null)

  const pagedNutrientData = computed(() => {
    const start = (nutrientCurrentPage.value - 1) * pageSize
    return filteredNutrientDataList.value.slice(start, start + pageSize)
  })

  const clampPage = (currentPage: number, total: number) => {
    const maxPage = Math.max(1, Math.ceil(total / pageSize))
    return Math.min(Math.max(currentPage, 1), maxPage)
  }

  /**
   * 从后端加载水质数据
   */
  const loadWaterQualityData = async () => {
    try {
      const data = await fetchWaterQualityData()
      if (data && Array.isArray(data)) {
        const current = waterCurrentPage.value
        waterQualityDataList.value = data
        waterCurrentPage.value = clampPage(current, data.length)
      }
    } catch (error) {
      console.error('加载水质数据失败:', error)
    }
  }

  /**
   * 从后端加载营养盐数据
   */
  const loadNutrientData = async () => {
    try {
      const data = await fetchNutrientData()
      if (data && Array.isArray(data)) {
        const current = nutrientCurrentPage.value
        nutrientDataList.value = data
        nutrientCurrentPage.value = clampPage(current, data.length)
      }
    } catch (error) {
      console.error('加载营养盐数据失败:', error)
    }
  }

  onMounted(() => {
    loadWaterQualityData()
    loadNutrientData()

    refreshTimer.value = window.setInterval(() => {
      loadWaterQualityData()
      loadNutrientData()
    }, 5000)
  })

  onBeforeUnmount(() => {
    if (refreshTimer.value !== null) {
      window.clearInterval(refreshTimer.value)
      refreshTimer.value = null
    }
  })

  watch(
    () => [props.selectedModel, props.dataType],
    () => {
      waterCurrentPage.value = 1
      nutrientCurrentPage.value = 1
    }
  )
</script>
