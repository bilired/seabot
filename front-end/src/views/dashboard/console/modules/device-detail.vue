<template>
  <ElDialog
    v-model="visibleLocal"
    title="设备详情"
    width="980px"
    :close-on-click-modal="false"
    destroy-on-close
    class="device-detail-dialog"
  >
    <div v-if="device" class="detail-layout">
      <div class="media-panel">
        <ElImage
          v-if="device.image"
          :src="device.image"
          fit="cover"
          class="device-image"
          preview-teleported
        >
          <template #error>
            <div class="image-error">图片加载失败</div>
          </template>
        </ElImage>
        <ElEmpty v-else description="暂无设备照片" :image-size="90" />
      </div>

      <div class="info-panel">
        <div class="title-row">
          <div>
            <h3 class="model-name">{{ device.model || '--' }}</h3>
            <p class="device-id">设备ID：{{ device.id || '--' }}</p>
          </div>
          <ElTag :type="statusTagType" size="large">{{ statusText }}</ElTag>
        </div>

        <ElDescriptions :column="2" border>
          <ElDescriptionsItem label="船型">{{ device.shipType || '--' }}</ElDescriptionsItem>
          <ElDescriptionsItem label="长度">{{ device.length ?? '--' }} cm</ElDescriptionsItem>
          <ElDescriptionsItem label="重量">{{ device.weight ?? '--' }} kg</ElDescriptionsItem>
          <ElDescriptionsItem label="最高航速">{{ device.maxSpeed ?? '--' }} 节</ElDescriptionsItem>
          <ElDescriptionsItem label="功能模块" :span="2">
            <div class="functions-text">{{ device.functions || '--' }}</div>
          </ElDescriptionsItem>
        </ElDescriptions>
      </div>
    </div>

    <template #footer>
      <ElButton @click="close">关闭</ElButton>
    </template>
  </ElDialog>
</template>

<script setup lang="ts">
import { computed, ref, toRefs, watch } from 'vue'

interface DeviceItem {
  id?: string
  shipType: string
  length: number
  model: string
  weight: number
  functions: string
  streamUrl?: string
  status: string
  maxSpeed: number
  image?: string
}

const props = defineProps<{ visible?: boolean; modelValue?: boolean; device: DeviceItem | null }>()
const { device } = toRefs(props)

const visibleLocal = ref<boolean>(props.visible ?? props.modelValue ?? false)
const emit = defineEmits(['update:visible', 'update:modelValue'])

watch(
  () => (typeof props.visible !== 'undefined' ? props.visible : props.modelValue),
  (value) => {
    visibleLocal.value = !!value
  }
)

watch(visibleLocal, (value) => {
  if (typeof props.visible !== 'undefined') emit('update:visible', value)
  if (typeof props.modelValue !== 'undefined') emit('update:modelValue', value)
})

const statusText = computed(() => {
  if (!device.value) return '--'
  return device.value.status === 'online' ? '在线' : '离线'
})

const statusTagType = computed<'success' | 'danger'>(() => {
  return device.value?.status === 'online' ? 'success' : 'danger'
})

const close = () => {
  visibleLocal.value = false
}
</script>

<style scoped lang="scss">
.detail-layout {
  display: grid;
  grid-template-columns: 340px 1fr;
  gap: 20px;
}

.media-panel {
  min-height: 280px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--el-fill-color-lighter);
}

.device-image {
  width: 100%;
  height: 100%;
  min-height: 280px;
}

.image-error {
  width: 100%;
  height: 280px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--el-text-color-secondary);
}

.info-panel {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.model-name {
  margin: 0;
  font-size: 18px;
  color: var(--el-text-color-primary);
}

.device-id {
  margin: 6px 0 0;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.stream-link {
  color: var(--el-color-primary);
  text-decoration: none;
  word-break: break-all;

  &:hover {
    text-decoration: underline;
  }
}

.functions-text {
  white-space: pre-wrap;
  word-break: break-word;
}

@media (max-width: 900px) {
  .detail-layout {
    grid-template-columns: 1fr;
  }
}
</style>
