<template>
  <!-- Element Plus Dialog removed (fallback modal below is active) -->

  <!-- Fallback plain overlay/modal in case ElDialog is not visible due to CSS/teleport issues -->
  <div v-if="visibleLocal" style="position:fixed; inset:0; background:rgba(0,0,0,0.45); z-index:4000; display:flex; align-items:center; justify-content:center;">
    <div style="width:1000px; max-width:95%; background:#fff; border-radius:6px; overflow:hidden; box-shadow:0 12px 28px rgba(0,0,0,0.25);">
      <div style="padding:18px 22px;">
        <div style="display:flex; gap:16px;">
          <div style="flex:1; min-width:320px">
            <div style="height:360px; display:flex; align-items:center; justify-content:center; background:#f5f7fa;">
              <img v-if="device?.image" :src="device?.image" alt="设备图片" style="max-width:100%; max-height:100%; object-fit:cover" />
              <div v-else style="color:#999">图片预览</div>
            </div>
          </div>
          <div style="width:360px">
            <h4 style="margin:0 0 8px">船体基本信息</h4>
            <div v-if="device">
              <p style="margin:4px 0">船型：{{ device.shipType }}</p>
              <p style="margin:4px 0">型号：{{ device.model }}</p>
              <p style="margin:4px 0">长度：{{ device.length }} cm</p>
              <p style="margin:4px 0">主要功能：{{ device.functions }}</p>
              <p style="margin:4px 0">续航时间：12小时</p>
              <p style="margin:4px 0">通信距离：10km</p>
            </div>
            <div style="margin-top:12px" v-if="device">
              <p style="margin:4px 0">基本状态：<span :class="device.status === '在线' ? 'text-success' : 'text-danger'">{{ device.status }}</span></p>
              <p style="margin:4px 0">运行天数：5天</p>
              <p style="margin:4px 0">监测天数：5天</p>
            </div>
          </div>
        </div>
      </div>
      <div style="padding:12px 18px; text-align:right; background:#fafafa">
        <button @click="close" style="padding:6px 12px; border-radius:4px; border:1px solid #dcdfe6; background:#fff; cursor:pointer">关闭</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, toRefs, watch } from 'vue'

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

// support both v-model:visible and v-model (modelValue) in parent
const props = defineProps<{ visible?: boolean; modelValue?: boolean; device: DeviceItem | null }>()
const { device } = toRefs(props)

const visibleLocal = ref<boolean>(props.visible ?? props.modelValue ?? false)
const emit = defineEmits(['update:visible', 'update:modelValue'])

// sync parent -> local (respond to either prop)
watch(
  () => (typeof props.visible !== 'undefined' ? props.visible : props.modelValue),
  (v) => {
    visibleLocal.value = !!v
  }
)

// sync local -> parent for both possible bindings
watch(visibleLocal, (v) => {
  if (typeof props.visible !== 'undefined') emit('update:visible', v)
  if (typeof props.modelValue !== 'undefined') emit('update:modelValue', v)
})

// debug logs
watch(visibleLocal, (v) => console.log('DeviceDetail visibleLocal ->', v))
watch(() => device.value, (d) => console.log('DeviceDetail device ->', d))

console.log('DeviceDetail mounted, initial visibleLocal =', visibleLocal.value)

function close() {
  visibleLocal.value = false
}

function onClose() {
  visibleLocal.value = false
}
</script>
