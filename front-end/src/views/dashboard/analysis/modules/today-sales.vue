<template>
  <div class="art-card h-82 p-5 mb-5 overflow-hidden max-lg:h-auto max-sm:mb-4">
    <div class="art-card-header pr-0">
      <div class="title">
        <h4>实时水质监测</h4>
        <p>今日监测数据</p>
      </div>
      <div class="flex-cc h-7.5 min-w-17 border border-g-300 rounded-lg text-g-500 c-p">
        <ArtSvgIcon icon="ri:arrow-up-line" class="text-base mr-1.5" />
        <span class="text-xs">导出</span>
      </div>
    </div>

    <div class="mt-2">
      <ElRow :gutter="20">
        <ElCol :span="6" :xs="24" v-for="(item, index) in waterQualityData" :key="index">
          <div
            class="flex px-5 flex-col justify-center h-55 border border-g-300/85 rounded-xl max-lg:mb-4 max-sm:flex-row max-sm:justify-between max-sm:items-center max-sm:h-40"
          >
            <div class="size-12 rounded-lg flex-cc bg-theme/10">
              <ArtSvgIcon :icon="item.icon" class="text-xl text-theme" />
            </div>

            <div class="max-sm:ml-4 mt-3.5 max-sm:mt-0 max-sm:text-end">
              <div class="text-2xl font-medium">{{ item.value }}<span class="text-sm text-g-600">{{ item.unit }}</span></div>
              <p class="mt-2 text-base text-g-600 max-sm:mt-1">{{ item.label }}</p>
              <small class="text-g-500 mt-1 max-sm:mt-0.5">
                标准范围
                <span
                  class="font-medium"
                  :class="[item.status === '正常' ? 'text-success' : 'text-warning']"
                  >{{ item.status }}</span
                >
              </small>
            </div>
          </div>
        </ElCol>
      </ElRow>
    </div>
  </div>
</template>

<script setup lang="ts">
  interface WaterQualityItem {
    label: string
    value: number
    unit: string
    status: string
    icon: string
  }

  /**
   * 实时水质监测数据
   * 包含水温、PH值、叶绿素浓度等关键水质指标
   */
  const waterQualityData = ref<WaterQualityItem[]>([
    {
      label: '水温',
      value: 22.5,
      unit: '°C',
      status: '正常',
      icon: 'ri:temperature-line'
    },
    {
      label: 'PH值',
      value: 7.2,
      unit: '',
      status: '正常',
      icon: 'ri:flask-line'
    },
    {
      label: '叶绿素浓度',
      value: 15,
      unit: 'μg/L',
      status: '正常',
      icon: 'ri:plant-line'
    },
    {
      label: '盐度',
      value: 32,
      unit: 'PSU',
      status: '正常',
      icon: 'ri:water-flash-line'
    }
  ])
</script>
