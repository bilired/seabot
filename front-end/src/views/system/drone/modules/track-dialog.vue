<template>
  <ElDialog
    v-model="dialogVisible"
    title="轨迹查询"
    width="1400px"
    :close-on-click-modal="false"
    destroy-on-close
    class="track-dialog"
  >
    <div class="track-container">
      <!-- 左侧：时间选择列表 -->
      <div class="time-list-section">
        <div class="time-list-header">
          <h4>{{ deviceData?.id || '11' }}</h4>
        </div>
        <div class="time-list">
          <div
            v-for="(item, index) in trackHistory"
            :key="index"
            class="time-item"
            :class="{ active: selectedTrackIndex === index }"
            @click="selectTrack(index)"
          >
            <Icon icon="ri:download-line" class="time-icon" />
            <span class="time-text">{{ item.time }}</span>
          </div>
        </div>
      </div>

      <!-- 右侧：地图显示 -->
      <div class="map-section">
        <div id="track-map" class="track-map"></div>
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
  import mapboxgl from 'mapbox-gl'
  import 'mapbox-gl/dist/mapbox-gl.css'

  interface Props {
    visible: boolean
    deviceData?: any
  }

  interface TrackHistoryItem {
    time: string
    coordinates: [number, number][]
  }

  const props = defineProps<Props>()
  const emit = defineEmits(['update:visible'])

  const dialogVisible = computed({
    get: () => props.visible,
    set: (val) => emit('update:visible', val)
  })

  // Mapbox access token - 请替换为你自己的token
  const MAPBOX_TOKEN = 'pk.eyJ1IjoiaGFua3NnYW8yMjExIiwiYSI6ImNtZzQzN3Q4cTFob3IycnEydGc1a2hmMmYifQ.Iys4mJ4-5OHRNeyFmWCOfw'

  // 地图实例
  let map: mapboxgl.Map | null = null
  let trackLine: mapboxgl.Marker[] = []

  // 选中的轨迹索引
  const selectedTrackIndex = ref(0)

  // 模拟轨迹历史数据
  const trackHistory = ref<TrackHistoryItem[]>([
    {
      time: '2024-08-02 15:00',
      coordinates: [
        [119.5, 26.0],
        [119.52, 26.02],
        [119.54, 26.04],
        [119.56, 26.06],
        [119.58, 26.08]
      ]
    },
    {
      time: '2024-08-04 12:00',
      coordinates: [
        [119.6, 26.1],
        [119.62, 26.12],
        [119.64, 26.14],
        [119.66, 26.16]
      ]
    },
    {
      time: '2024-09-06 17:00',
      coordinates: [
        [119.7, 26.2],
        [119.72, 26.22],
        [119.74, 26.24],
        [119.76, 26.26],
        [119.78, 26.28]
      ]
    },
    {
      time: '2024-09-10 15:00',
      coordinates: [
        [119.8, 26.3],
        [119.82, 26.32],
        [119.84, 26.34]
      ]
    }
  ])

  /**
   * 初始化地图
   */
  const initMap = () => {
    try {
      mapboxgl.accessToken = MAPBOX_TOKEN

      map = new mapboxgl.Map({
        container: 'track-map',
        style: 'mapbox://styles/mapbox/streets-v12', // 可以改为 satellite-v9 卫星图
        center: [119.3, 26.08], // 福清市附近坐标
        zoom: 10
      })

      // 添加导航控件
      map.addControl(new mapboxgl.NavigationControl(), 'top-right')

      // 地图加载完成后绘制轨迹
      map.on('load', () => {
        drawTrack(selectedTrackIndex.value)
      })
    } catch (error) {
      console.error('地图初始化失败:', error)
      // 如果Mapbox token无效，显示提示信息
      const mapElement = document.getElementById('track-map')
      if (mapElement) {
        mapElement.innerHTML = `
          <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; background: #f5f5f5; color: #666;">
            <p style="font-size: 16px; margin-bottom: 10px;">地图加载失败</p>
            <p style="font-size: 14px;">请配置有效的 Mapbox Access Token</p>
            <p style="font-size: 12px; margin-top: 10px; color: #999;">获取地址: https://account.mapbox.com/access-tokens/</p>
          </div>
        `
      }
    }
  }

  /**
   * 绘制轨迹
   */
  const drawTrack = (index: number) => {
    if (!map) return

    const track = trackHistory.value[index]
    if (!track) return

    // 清除之前的轨迹
    clearTrack()

    // 添加轨迹线
    if (map.getSource('route')) {
      map.removeLayer('route')
      map.removeSource('route')
    }

    map.addSource('route', {
      type: 'geojson',
      data: {
        type: 'Feature',
        properties: {},
        geometry: {
          type: 'LineString',
          coordinates: track.coordinates
        }
      }
    })

    map.addLayer({
      id: 'route',
      type: 'line',
      source: 'route',
      layout: {
        'line-join': 'round',
        'line-cap': 'round'
      },
      paint: {
        'line-color': '#1890ff',
        'line-width': 4
      }
    })

    // 添加起点和终点标记
    const startMarker = new mapboxgl.Marker({ color: '#52c41a' })
      .setLngLat(track.coordinates[0])
      .setPopup(new mapboxgl.Popup().setHTML('<strong>起点</strong>'))
      .addTo(map)

    const endMarker = new mapboxgl.Marker({ color: '#f5222d' })
      .setLngLat(track.coordinates[track.coordinates.length - 1])
      .setPopup(new mapboxgl.Popup().setHTML('<strong>终点</strong>'))
      .addTo(map)

    trackLine.push(startMarker, endMarker)

    // 调整地图视图以适应轨迹
    const bounds = new mapboxgl.LngLatBounds()
    track.coordinates.forEach((coord) => bounds.extend(coord as [number, number]))
    map.fitBounds(bounds, { padding: 50 })
  }

  /**
   * 清除轨迹
   */
  const clearTrack = () => {
    trackLine.forEach((marker) => marker.remove())
    trackLine = []
  }

  /**
   * 选择轨迹
   */
  const selectTrack = (index: number) => {
    selectedTrackIndex.value = index
    drawTrack(index)
  }

  /**
   * 关闭对话框
   */
  const handleClose = () => {
    dialogVisible.value = false
  }

  /**
   * 监听对话框打开
   */
  watch(dialogVisible, (val) => {
    if (val) {
      nextTick(() => {
        initMap()
      })
    } else {
      // 清理地图实例
      if (map) {
        map.remove()
        map = null
      }
      trackLine = []
    }
  })

  /**
   * 组件卸载时清理
   */
  onUnmounted(() => {
    if (map) {
      map.remove()
      map = null
    }
  })
</script>

<style scoped lang="scss">
  .track-container {
    display: flex;
    gap: 20px;
    height: 700px;
  }

  .time-list-section {
    width: 200px;
    display: flex;
    flex-direction: column;
    border-right: 1px solid #e8e8e8;
  }

  .time-list-header {
    padding: 15px;
    border-bottom: 1px solid #e8e8e8;

    h4 {
      font-size: 18px;
      font-weight: 600;
      color: #333;
      margin: 0;
    }
  }

  .time-list {
    flex: 1;
    overflow-y: auto;
    padding: 10px 0;
  }

  .time-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 15px;
    cursor: pointer;
    transition: all 0.3s;
    border-left: 3px solid transparent;

    &:hover {
      background-color: #f5f5f5;
    }

    &.active {
      background-color: #e6f7ff;
      border-left-color: #1890ff;

      .time-text {
        color: #1890ff;
        font-weight: 500;
      }

      .time-icon {
        color: #1890ff;
      }
    }

    .time-icon {
      font-size: 16px;
      color: #666;
    }

    .time-text {
      font-size: 14px;
      color: #333;
    }
  }

  .map-section {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .track-map {
    width: 100%;
    height: 100%;
    border-radius: 4px;
    overflow: hidden;
  }

  .dialog-footer {
    display: flex;
    justify-content: flex-end;
  }

  // 调整对话框样式
  :deep(.track-dialog) {
    .el-dialog__body {
      padding: 20px;
    }
  }

  // 自定义滚动条
  .time-list::-webkit-scrollbar {
    width: 6px;
  }

  .time-list::-webkit-scrollbar-thumb {
    background-color: #d9d9d9;
    border-radius: 3px;

    &:hover {
      background-color: #bfbfbf;
    }
  }

  .time-list::-webkit-scrollbar-track {
    background-color: #f5f5f5;
  }
</style>
