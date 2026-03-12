<!-- 阿里云视频播放器组件 -->
<template>
  <div :id="playerId" class="aliyun-player-container" />
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'

defineOptions({ name: 'ArtAliyunVideoPlayer' })

interface Props {
  /** 播放器容器 ID */
  playerId: string
  /** 视频源URL */
  videoUrl: string
  /** 视频封面图URL */
  posterUrl?: string
  /** 是否自动播放 */
  autoplay?: boolean
  /** 音量大小(0-1) */
  volume?: number
  /** 可选的播放速率 */
  playbackRates?: number[]
  /** 是否循环播放 */
  loop?: boolean
  /** 是否静音 */
  muted?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  playerId: 'aliyun-player',
  videoUrl: '',
  posterUrl: '',
  autoplay: false,
  volume: 1,
  loop: false,
  muted: false,
  playbackRates: () => [0.5, 1, 1.5, 2]
})

// 播放器实例引用
const playerInstance = ref<any>(null)

// 初始化播放器
onMounted(() => {
  // 动态加载阿里云播放器脚本和样式
  const scriptId = 'aliplayer-script'
  const styleId = 'aliplayer-style'

  // 检查脚本是否已加载
  if (!document.getElementById(scriptId)) {
    // 加载样式
    const link = document.createElement('link')
    link.id = styleId
    link.rel = 'stylesheet'
    link.href = 'https://g.alicdn.com/aliyun/aliplayer/7.10.7/aliplayer-min.css'
    document.head.appendChild(link)

    // 加载脚本
    const script = document.createElement('script')
    script.id = scriptId
    script.src = 'https://g.alicdn.com/aliyun/aliplayer/7.10.7/aliplayer-min.js'
    script.onload = () => {
      initPlayer()
    }
    document.head.appendChild(script)
  } else {
    initPlayer()
  }
})

// 初始化播放器实例
const initPlayer = () => {
  // 等待 Aliplayer 全局对象可用
  if (typeof (window as any).Aliplayer === 'undefined') {
    setTimeout(initPlayer, 100)
    return
  }

  const Aliplayer = (window as any).Aliplayer

  try {
    playerInstance.value = new Aliplayer(
      {
        id: props.playerId,
        source: props.videoUrl, // 视频源
        width: '100%',
        height: '100%',
        autoplay: props.autoplay,
        preload: true,
        controlBarVisibility: 'hover',
        useH5Prism: true,
        isLive: false,
        rePlay: false,
        playsinline: true,
        aspectRatio: '16:9',
        poster: props.posterUrl || '',
        volume: props.volume,
        muted: props.muted,
        loop: props.loop,
        qualitySort: 'desc',
        // 如果是直播流 RTSP 地址，需要通过代理或转码
        plugins: []
      },
      (player: any) => {
        console.log('Aliplayer 初始化成功')

        // 设置音量
        if (player.setVolume) {
          player.setVolume(props.volume)
        }

        // 监听播放事件
        player.on('play', () => {
          console.log('视频开始播放')
        })

        // 监听暂停事件
        player.on('pause', () => {
          console.log('视频已暂停')
        })

        // 监听错误事件
        player.on('error', (error: any) => {
          console.error('播放器错误:', error)
        })

        // 监听时间更新
        player.on('timeupdate', () => {
          // 可以用来获取实时统计信息
          const currentTime = player.getCurrentTime?.()
          const duration = player.getDuration?.()
          const bufferDuration = player.getPlayedPercent?.()
          console.log(`当前时间: ${currentTime}s, 总时长: ${duration}s, 缓冲: ${bufferDuration}%`)
        })

        // 监听流统计信息（用于视频流监测）
        if (player.on) {
          player.on('play', () => {
            // 获取播放统计信息
            if (player.mp4Instance?.mediaElement?.video?.getVideoPlaybackQuality) {
              const stats = player.mp4Instance.mediaElement.video.getVideoPlaybackQuality()
              console.log('视频播放质量:', stats)
            }
          })
        }
      }
    )
  } catch (error) {
    console.error('Aliplayer 初始化失败:', error)
  }
}

// 获取播放统计信息（用于上报视频流监测指标）
const getPlaybackStats = () => {
  if (!playerInstance.value) return null

  try {
    const player = playerInstance.value

    return {
      currentTime: player.getCurrentTime?.() || 0,
      duration: player.getDuration?.() || 0,
      bufferedPercent: player.getPlayedPercent?.() || 0,
      volume: player.getVolume?.() || 0,
      paused: player.paused || false,
      ended: player.ended || false
    }
  } catch (error) {
    console.error('获取统计信息失败:', error)
    return null
  }
}

// 暴露获取统计信息的方法
defineExpose({
  getPlaybackStats,
  getPlayerInstance: () => playerInstance.value
})

// 组件卸载时清理
onBeforeUnmount(() => {
  if (playerInstance.value && playerInstance.value.dispose) {
    playerInstance.value.dispose()
    playerInstance.value = null
  }
})
</script>

<style scoped lang="scss">
.aliyun-player-container {
  width: 100%;
  height: 100%;
  background: #000;
}
</style>
