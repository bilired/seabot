<!-- 系统logo -->
<template>
  <div class="flex-cc">
    <img :style="logoStyle" src="@imgs/common/Ship.png" alt="logo" class="w-full h-full" />
  </div>
</template>

<script setup lang="ts">
  import { useSettingStore } from '@/store/modules/setting'

  defineOptions({ name: 'ArtLogo' })

  interface Props {
    /** logo 大小 */
    size?: number | string
  }

  const props = withDefaults(defineProps<Props>(), {
    size: 36
  })

  const { isDark } = storeToRefs(useSettingStore())

  const logoStyle = computed(() => ({
    width: `${props.size}px`,
    // Convert PNG to monochrome: light mode -> black, dark mode -> white.
    filter: isDark.value ? 'grayscale(1) brightness(0) invert(1)' : 'grayscale(1) brightness(0)'
  }))
</script>
