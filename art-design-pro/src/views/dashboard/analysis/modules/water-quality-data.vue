<template>
  <div class="art-card h-120 p-5 mb-5 max-sm:mb-4">
    <div class="art-card-header mb-4">
      <div class="title">
        <h4>实时监测数据</h4>
        <p>无人船上传数据</p>
      </div>
    </div>
    
    <ElTabs v-model="activeTab" class="mb-4">
      <ElTabPane label="水质数据" name="water">
        <ElTable 
          :data="waterQualityDataList" 
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
          <ElTableColumn prop="warningCode" label="警告码" width="120" align="center">
            <template #default="{ row }">
              <span :class="row.warningCode === '正常' ? 'text-success' : 'text-warning'">
                {{ row.warningCode }}
              </span>
            </template>
          </ElTableColumn>
          <ElTableColumn prop="collectionTime" label="采集时间" width="180" fixed="right" align="center" />
          <ElTableColumn prop="connectionStatus" label="连接状态" width="120" fixed="right" align="center">
            <template #default="{ row }">
              <span :class="row.connectionStatus === '在线' ? 'text-success' : 'text-danger'">
                {{ row.connectionStatus }}
              </span>
            </template>
          </ElTableColumn>
        </ElTable>
      </ElTabPane>
      
      <ElTabPane label="营养盐数据" name="nutrients">
        <ElTable 
          :data="nutrientDataList" 
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
          <ElTableColumn prop="errorCode1" label="错误码1" width="120" align="center" />
          <ElTableColumn prop="errorCode2" label="错误码2" width="120" align="center" />
          <ElTableColumn prop="instrumentStatus" label="营养盐仪器状态" width="150" align="center">
            <template #default="{ row }">
              <span :class="row.instrumentStatus === '正常' ? 'text-success' : 'text-danger'">
                {{ row.instrumentStatus }}
              </span>
            </template>
          </ElTableColumn>
          <ElTableColumn prop="collectionTime" label="采集时间" width="180" fixed="right" align="center" />
          <ElTableColumn prop="connectionStatus" label="连接状态" width="120" fixed="right" align="center">
            <template #default="{ row }">
              <span :class="row.connectionStatus === '在线' ? 'text-success' : 'text-danger'">
                {{ row.connectionStatus }}
              </span>
            </template>
          </ElTableColumn>
        </ElTable>
      </ElTabPane>
    </ElTabs>
  </div>
</template>

<script setup lang="ts">
  import { onMounted, ref } from 'vue'
  import { fetchWaterQualityData, fetchNutrientData } from '@/api/dashboard'

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
    warningCode: string
    collectionTime: string
    connectionStatus: string
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
    errorCode1: string
    errorCode2: string
    instrumentStatus: string
    collectionTime: string
    connectionStatus: string
  }

  const activeTab = ref('water')

  /**
   * 无人船水质数据列表
   * 显示各船舶上传的实时水质监测数据
   */
  const waterQualityDataList = ref<WaterQualityDataItem[]>([
    {
      shipModel: 'DL-3026',
      temperature: 22.5,
      ph: 7.2,
      chlorophyll: 15.3,
      salinity: 32.1,
      dissolvedOxygen: 8.2,
      conductivity: 450,
      turbidity: 2.5,
      algae: 850,
      warningCode: '正常',
      collectionTime: '2026-01-29 10:30:00',
      connectionStatus: '在线'
    },
    {
      shipModel: 'DL-3022',
      temperature: 21.8,
      ph: 7.1,
      chlorophyll: 12.8,
      salinity: 31.9,
      dissolvedOxygen: 8.5,
      conductivity: 455,
      turbidity: 2.2,
      algae: 650,
      warningCode: '正常',
      collectionTime: '2026-01-29 10:25:00',
      connectionStatus: '在线'
    },
    {
      shipModel: 'DL-3020',
      temperature: 23.2,
      ph: 7.3,
      chlorophyll: 18.5,
      salinity: 32.3,
      dissolvedOxygen: 7.9,
      conductivity: 440,
      turbidity: 3.8,
      algae: 1200,
      warningCode: '警告',
      collectionTime: '2026-01-29 10:20:00',
      connectionStatus: '在线'
    },
    {
      shipModel: 'DL-3018',
      temperature: 22.1,
      ph: 7.0,
      chlorophyll: 14.2,
      salinity: 31.8,
      dissolvedOxygen: 8.3,
      conductivity: 460,
      turbidity: 2.8,
      algae: 950,
      warningCode: '正常',
      collectionTime: '2026-01-29 10:15:00',
      connectionStatus: '在线'
    },
    {
      shipModel: 'DL-3016',
      temperature: 20.5,
      ph: 6.9,
      chlorophyll: 11.5,
      salinity: 31.5,
      dissolvedOxygen: 8.7,
      conductivity: 445,
      turbidity: 2.0,
      algae: 500,
      warningCode: '正常',
      collectionTime: '2026-01-29 10:10:00',
      connectionStatus: '在线'
    }

  ])

  /**
   * 营养盐数据列表
   * 显示各船舶上传的营养盐监测数据
   */
  const nutrientDataList = ref<NutrientDataItem[]>([
    {
      shipModel: 'DL-3026',
      phosphate: 0.45,
      phosphateTime: '2026-01-29 10:30:00',
      ammonia: 0.28,
      ammoniaTime: '2026-01-29 10:30:00',
      nitrate: 1.52,
      nitrateTime: '2026-01-29 10:30:00',
      nitrite: 0.08,
      nitriteTime: '2026-01-29 10:30:00',
      errorCode1: '00',
      errorCode2: '00',
      instrumentStatus: '正常',
      collectionTime: '2026-01-29 10:30:00',
      connectionStatus: '在线'
    },
    {
      shipModel: 'DL-3022',
      phosphate: 0.38,
      phosphateTime: '2026-01-29 10:25:00',
      ammonia: 0.22,
      ammoniaTime: '2026-01-29 10:25:00',
      nitrate: 1.35,
      nitrateTime: '2026-01-29 10:25:00',
      nitrite: 0.06,
      nitriteTime: '2026-01-29 10:25:00',
      errorCode1: '00',
      errorCode2: '00',
      instrumentStatus: '正常',
      collectionTime: '2026-01-29 10:25:00',
      connectionStatus: '在线'
    },
    {
      shipModel: 'DL-3020',
      phosphate: 0.58,
      phosphateTime: '2026-01-29 10:20:00',
      ammonia: 0.42,
      ammoniaTime: '2026-01-29 10:20:00',
      nitrate: 1.78,
      nitrateTime: '2026-01-29 10:20:00',
      nitrite: 0.12,
      nitriteTime: '2026-01-29 10:20:00',
      errorCode1: '00',
      errorCode2: '00',
      instrumentStatus: '正常',
      collectionTime: '2026-01-29 10:20:00',
      connectionStatus: '在线'
    },
    {
      shipModel: 'DL-3018',
      phosphate: 0.42,
      phosphateTime: '2026-01-29 10:15:00',
      ammonia: 0.25,
      ammoniaTime: '2026-01-29 10:15:00',
      nitrate: 1.48,
      nitrateTime: '2026-01-29 10:15:00',
      nitrite: 0.07,
      nitriteTime: '2026-01-29 10:15:00',
      errorCode1: '00',
      errorCode2: '00',
      instrumentStatus: '正常',
      collectionTime: '2026-01-29 10:15:00',
      connectionStatus: '在线'
    },
    {
      shipModel: 'DL-3016',
      phosphate: 0.32,
      phosphateTime: '2026-01-29 10:10:00',
      ammonia: 0.18,
      ammoniaTime: '2026-01-29 10:10:00',
      nitrate: 1.22,
      nitrateTime: '2026-01-29 10:10:00',
      nitrite: 0.05,
      nitriteTime: '2026-01-29 10:10:00',
      errorCode1: '00',
      errorCode2: '00',
      instrumentStatus: '正常',
      collectionTime: '2026-01-29 10:10:00',
      connectionStatus: '在线'
    }
  ])

  /**
   * 从后端加载水质数据
   */
  const loadWaterQualityData = async () => {
    try {
      const response = await fetchWaterQualityData()
      if (response.code === 200 && response.data.length > 0) {
        waterQualityDataList.value = response.data
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
      const response = await fetchNutrientData()
      if (response.code === 200 && response.data.length > 0) {
        nutrientDataList.value = response.data
      }
    } catch (error) {
      console.error('加载营养盐数据失败:', error)
    }
  }

  onMounted(() => {
    loadWaterQualityData()
    loadNutrientData()
  })
</script>
