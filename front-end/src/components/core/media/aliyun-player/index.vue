<template>
  <div class="aliyun-player-wrap">
    <div :id="playerId" class="prism-player aliyun-player-container" />
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

defineOptions({ name: 'AliyunPlayer' })

interface Props {
  playerId: string
  videoUrl: string
  autoplay?: boolean
  muted?: boolean
  volume?: number
  loop?: boolean
}

type AliplayerCtor = new (
  options: Record<string, unknown>,
  ready?: (player: AliplayerInstance) => void
) => AliplayerInstance

interface AliplayerInstance {
  on: (event: string, cb: (...args: any[]) => void) => void
  dispose?: () => void
  setVolume?: (val: number) => void
  getCurrentTime?: () => number
  getDuration?: () => number
  getPlayedPercent?: () => number
}

interface AliplayerWindow extends Window {
  Aliplayer?: AliplayerCtor
}

const props = withDefaults(defineProps<Props>(), {
  playerId: 'player-con',
  videoUrl: '',
  autoplay: true,
  muted: true,
  volume: 0,
  loop: true
})

const playerInstance = ref<AliplayerInstance | null>(null)
const STYLE_ID = 'aliyun-imp-player-style'
const SCRIPT_ID = 'aliyun-imp-player-script'
const ALI_STYLE_URL =
  'https://g.alicdn.com/apsara-media-box/imp-web-player/2.36.1/skins/default/aliplayer-min.css'
const ALI_SCRIPT_URL =
  'https://g.alicdn.com/apsara-media-box/imp-web-player/2.36.1/aliplayer-min.js'

const ensureSdkLoaded = async () => {
  if (!document.getElementById(STYLE_ID)) {
    const link = document.createElement('link')
    link.id = STYLE_ID
    link.rel = 'stylesheet'
    link.href = ALI_STYLE_URL
    document.head.appendChild(link)
  }

  if ((window as AliplayerWindow).Aliplayer) {
    return
  }

  await new Promise<void>((resolve, reject) => {
    const existing = document.getElementById(SCRIPT_ID) as HTMLScriptElement | null
    if (existing) {
      existing.addEventListener('load', () => resolve(), { once: true })
      existing.addEventListener('error', () => reject(new Error('阿里云播放器脚本加载失败')), {
        once: true
      })
      return
    }

    const script = document.createElement('script')
    script.id = SCRIPT_ID
    script.src = ALI_SCRIPT_URL
    script.async = true
    script.onload = () => resolve()
    script.onerror = () => reject(new Error('阿里云播放器脚本加载失败'))
    document.head.appendChild(script)
  })
}

const disposePlayer = () => {
  if (playerInstance.value?.dispose) {
    playerInstance.value.dispose()
  }
  playerInstance.value = null
}

const initPlayer = async () => {
  if (!props.videoUrl) {
    return
  }

  try {
    await ensureSdkLoaded()
    disposePlayer()

    const Aliplayer = (window as AliplayerWindow).Aliplayer
    if (!Aliplayer) {
      throw new Error('Aliplayer 未加载')
    }

    playerInstance.value = new Aliplayer(
      {
        id: props.playerId,
        source: props.videoUrl,
        width: '100%',
        height: '100%',
        autoplay: props.autoplay,
        muted: props.muted,
        isLive: true,
        isVBR: true,
        enableH265: true,
        extraInfo: {
          crossOrigin: 'anonymous'
        },
        flvConfig: {
          cors: true,
          withCredentials: false
        },
        skinLayout: [
          { name: 'bigPlayButton', align: 'blabs', x: 30, y: 80 },
          { name: 'errorDisplay', align: 'tlabs', x: 0, y: 0 },
          { name: 'infoDisplay' },
          {
            name: 'controlBar',
            align: 'blabs',
            x: 0,
            y: 0,
            children: [
              { name: 'liveDisplay', align: 'tlabs', x: 15, y: 6 },
              { name: 'fullScreenButton', align: 'tr', x: 10, y: 10 },
              { name: 'setting', align: 'tr', x: 15, y: 12 },
              { name: 'volume', align: 'tr', x: 5, y: 10 },
              { name: 'snapshot', align: 'tr', x: 10, y: 12 }
            ]
          }
        ],
        watermark: {
          enable: false,
          text: '无人船管理系统',
          mode: 'GHOST'
        },
        license: {
          key: 'SPGV6VIaQ5weoF2DM9ed29bbf379e4f3b96a83829c79aba0a',
          domain: 'yunpingtai.cc'
        }
      },
      (player: AliplayerInstance) => {
        player.setVolume?.(props.volume)
        player.on('error', (err: unknown) => {
          console.error('阿里云播放器播放出错:', err)
        })

        player.on('snapshoted', (data: any) => {
          const pictureData = data?.paramData?.base64
          if (!pictureData) {
            return
          }

          const downloadElement = document.createElement('a')
          downloadElement.setAttribute('href', pictureData)
          downloadElement.setAttribute('download', `直播截图_${Date.now()}.png`)
          downloadElement.click()
        })
      }
    )
  } catch (error) {
    console.error('阿里云播放器初始化失败:', error)
  }
}

const getPlaybackStats = () => {
  const player = playerInstance.value
  if (!player) {
    return null
  }

  return {
    currentTime: player.getCurrentTime?.() || 0,
    duration: player.getDuration?.() || 0,
    bufferedPercent: player.getPlayedPercent?.() || 0
  }
}

defineExpose({
  getPlaybackStats,
  getPlayerInstance: () => playerInstance.value
})

watch(
  () => props.videoUrl,
  () => {
    void initPlayer()
  }
)

onMounted(() => {
  void initPlayer()
})

onBeforeUnmount(() => {
  disposePlayer()
})
</script>

<style scoped lang="scss">
.aliyun-player-wrap {
  width: 100%;
  height: 100%;
  min-height: 360px;
  background: #000;
}

.aliyun-player-container {
  width: 100%;
  height: 100%;
}
</style>
