<template>
  <ElDialog
    v-model="dialogVisible"
    title="控制"
    width="1200px"
    :close-on-click-modal="false"
    destroy-on-close
    class="control-dialog"
  >
    <div class="control-container">
      <!-- 左侧：视频播放器 -->
      <div class="video-section">
        <div class="device-info">
          <h3>{{ deviceData?.model || 'DL-3026' }}</h3>
        </div>
        <div class="video-player">
          <div class="video-placeholder">
            <Icon icon="ri:live-line" class="video-icon" />
            <p class="video-text">播放出错误 (LICENSE ERROR)</p>
            <ElButton type="primary" size="small" @click="refreshStream">刷新</ElButton>
            <div class="error-info">
              <p>code: 4040</p>
              <p>uuid: 9E102A75-97D5-4930-878A-42DF06F73FBC</p>
              <p>requestId(playerc): FF01BE7C-AF3E-45ED-B67E-C3470A1565FB</p>
              <p>ver: 2.34.5</p>
              <p>播放时间: {{ currentTime }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：控制面板 -->
      <div class="control-panel">
        <!-- 载荷设备控制和参数修正 -->
        <div class="control-section">
          <h4>载荷设备控制和参数修正</h4>
          
          <div class="control-item">
            <label>采样装置:</label>
            <ElSwitch v-model="controls.sampling" active-text="开启" />
          </div>

          <div class="control-item">
            <label>环境监测仪器提起回收:</label>
            <ElSwitch v-model="controls.monitoring" active-text="开启" />
          </div>

          <div class="control-item">
            <label>环境仪器状态:</label>
            <ElSwitch v-model="controls.instrumentStatus" active-text="正常" />
          </div>

          <div class="control-item">
            <label>摄像头模式:</label>
            <ElButtonGroup>
              <ElButton 
                :type="controls.cameraMode === 'day' ? 'primary' : 'default'"
                @click="controls.cameraMode = 'day'"
              >
                白天
              </ElButton>
              <ElButton 
                :type="controls.cameraMode === 'night' ? 'primary' : 'default'"
                @click="controls.cameraMode = 'night'"
              >
                夜晚
              </ElButton>
            </ElButtonGroup>
          </div>
        </div>

        <!-- 船体航行修正 -->
        <div class="control-section">
          <h4>船体航行修正</h4>
          
          <div class="direction-control">
            <div class="direction-row">
              <ElButton class="direction-btn" @click="handleDirection('up')">
                <Icon icon="ri:arrow-up-line" />
                上转
              </ElButton>
            </div>
            <div class="direction-row">
              <ElButton class="direction-btn" @click="handleDirection('left')">
                <Icon icon="ri:arrow-left-line" />
                左转
              </ElButton>
              <ElButton class="direction-btn" @click="handleDirection('right')">
                <Icon icon="ri:arrow-right-line" />
                右转
              </ElButton>
            </div>
            <div class="direction-row">
              <ElButton class="direction-btn" @click="handleDirection('down')">
                <Icon icon="ri:arrow-down-line" />
                下转
              </ElButton>
            </div>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <ElButton @click="handleClose">关闭</ElButton>
      </div>
    </template>
  </ElDialog>
</template>

<script setup lang="ts">
  import { Icon } from '@iconify/vue'
  import { ElMessage } from 'element-plus'

  interface Props {
    visible: boolean
    deviceData?: any
  }

  interface Controls {
    sampling: boolean
    monitoring: boolean
    instrumentStatus: boolean
    cameraMode: 'day' | 'night'
  }

  const props = defineProps<Props>()
  const emit = defineEmits(['update:visible'])

  const dialogVisible = computed({
    get: () => props.visible,
    set: (val) => emit('update:visible', val)
  })

  // 控制状态
  const controls = reactive<Controls>({
    sampling: true,
    monitoring: true,
    instrumentStatus: true,
    cameraMode: 'night'
  })

  // 当前时间
  const currentTime = ref('2026-02-19 20:45:40')

  // 更新时间
  const updateTime = () => {
    const now = new Date()
    currentTime.value = now.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    }).replace(/\//g, '-')
  }

  // 定时器
  let timer: NodeJS.Timeout | null = null

  // 刷新视频流
  const refreshStream = () => {
    ElMessage.info('正在刷新视频流...')
  }

  // 处理方向控制
  const handleDirection = (direction: 'up' | 'down' | 'left' | 'right') => {
    const directionMap = {
      up: '前进',
      down: '后退',
      left: '左转',
      right: '右转'
    }
    ElMessage.success(`船体${directionMap[direction]}指令已发送`)
  }

  // 关闭对话框
  const handleClose = () => {
    dialogVisible.value = false
  }

  // 监听对话框打开
  watch(dialogVisible, (val) => {
    if (val) {
      updateTime()
      timer = setInterval(updateTime, 1000)
    } else {
      if (timer) {
        clearInterval(timer)
        timer = null
      }
    }
  })

  // 组件卸载时清理定时器
  onUnmounted(() => {
    if (timer) {
      clearInterval(timer)
    }
  })
</script>

<style scoped lang="scss">
  .control-container {
    display: flex;
    gap: 20px;
    min-height: 600px;
  }

  .video-section {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .device-info {
    margin-bottom: 10px;

    h3 {
      font-size: 16px;
      font-weight: 500;
      color: #333;
    }
  }

  .video-player {
    flex: 1;
    background: #000;
    border-radius: 4px;
    overflow: hidden;
  }

  .video-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #fff;
    padding: 40px;

    .video-icon {
      font-size: 60px;
      margin-bottom: 20px;
      opacity: 0.5;
    }

    .video-text {
      font-size: 18px;
      margin-bottom: 20px;
    }

    .error-info {
      margin-top: 30px;
      font-size: 12px;
      color: #999;
      text-align: left;
      width: 100%;
      max-width: 500px;
      font-family: monospace;

      p {
        margin: 5px 0;
      }
    }
  }

  .control-panel {
    width: 400px;
    display: flex;
    flex-direction: column;
    gap: 30px;
  }

  .control-section {
    h4 {
      font-size: 16px;
      font-weight: 500;
      margin-bottom: 20px;
      color: #333;
    }
  }

  .control-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;

    label {
      font-size: 14px;
      color: #666;
    }
  }

  .direction-control {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    padding: 20px;
  }

  .direction-row {
    display: flex;
    gap: 10px;
  }

  .direction-btn {
    min-width: 100px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 5px;

    :deep(.iconify) {
      font-size: 18px;
    }
  }

  .dialog-footer {
    display: flex;
    justify-content: flex-end;
  }

</style>
