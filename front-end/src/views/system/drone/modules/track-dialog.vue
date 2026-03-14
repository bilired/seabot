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
      <div class="time-list-section">
        <div class="time-list-header">
          <h4>{{ deviceData?.model || deviceData?.id || '设备轨迹' }}</h4>
        </div>
        <div class="time-list">
          <div
            v-for="(item, index) in dailyTracks"
            :key="item.date"
            class="time-item"
            :class="{ active: selectedTrackIndex === index }"
            @click="selectTrack(index)"
          >
            <Icon icon="ri:download-line" class="time-icon" />
            <span class="time-text">{{ item.date }}</span>
            <span class="time-count">{{ item.points.length }}点</span>
          </div>
        </div>
      </div>

      <div class="map-section">
        <div id="track-map" class="track-map"></div>

        <div v-if="currentDayTrack && currentDayTrack.points.length" class="timeline-panel">
          <div class="timeline-meta">
            <span>{{ currentDayTrack.date }}</span>
            <span>{{ progressValue + 1 }} / {{ currentDayTrack.points.length }}</span>
          </div>

          <div class="timeline-controls">
            <ElButton size="small" type="primary" @click="togglePlayback">
              {{ isPlaying ? '暂停回放' : '播放回放' }}
            </ElButton>
            <ElButton size="small" @click="resetPlayback">回到起点</ElButton>
          </div>

          <div class="timeline-ruler" v-if="timelineMarks.length">
            <div
              v-for="(mark, idx) in timelineMarks"
              :key="`${mark.index}-${mark.label}`"
              class="timeline-ruler-item"
              :class="{ first: idx === 0, last: idx === timelineMarks.length - 1 }"
              :style="{ left: `${mark.left}%` }"
            >
              <span class="tick"></span>
              <span class="label">{{ mark.label }}</span>
            </div>
          </div>

          <ElSlider
            v-model="progressValue"
            :min="0"
            :max="progressMax"
            :step="1"
            :show-tooltip="false"
          />

          <div class="timeline-time">{{ currentPoint?.time || '-' }}</div>
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
  import mapboxgl from 'mapbox-gl'
  import 'mapbox-gl/dist/mapbox-gl.css'
  import { fetchShipGatewayStatus, fetchShipTrackHistory } from '@/api/drone'
  import { ElMessage } from 'element-plus'

  const MAPBOX_TOKEN =
    import.meta.env.VITE_MAPBOX_TOKEN ||
    import.meta.env.VITE_MAPBOX_ACCESS_TOKEN ||
    ''

  interface Props {
    visible: boolean
    deviceData?: any
  }

  interface TrackPoint {
    date: string
    time: string
    timestamp: number
    coordinate: [number, number]
    speed?: number | null
    course?: number | null
  }

  interface DailyTrack {
    date: string
    points: TrackPoint[]
  }

  interface TimelineMark {
    index: number
    left: number
    label: string
  }

  const props = defineProps<Props>()
  const emit = defineEmits(['update:visible'])

  const dialogVisible = computed({
    get: () => props.visible,
    set: (val) => emit('update:visible', val)
  })

  let map: mapboxgl.Map | null = null
  let markers: mapboxgl.Marker[] = []
  let gatewayStream: EventSource | null = null
  let playbackTimer: number | null = null
  let fittedDate = ''

  const selectedTrackIndex = ref(0)
  const progressValue = ref(0)
  const isPlaying = ref(false)
  const dailyTracks = ref<DailyTrack[]>([])

  const deviceModel = computed(() => props.deviceData?.model || '')
  const currentDayTrack = computed(() => dailyTracks.value[selectedTrackIndex.value])
  const progressMax = computed(() => Math.max((currentDayTrack.value?.points.length || 1) - 1, 0))
  const currentPoint = computed(() => currentDayTrack.value?.points[progressValue.value])

  const formatTickTime = (timestamp: number) => {
    const date = new Date(timestamp)
    const hh = String(date.getHours()).padStart(2, '0')
    const mm = String(date.getMinutes()).padStart(2, '0')
    const ss = String(date.getSeconds()).padStart(2, '0')
    return `${hh}:${mm}:${ss}`
  }

  const timelineMarks = computed<TimelineMark[]>(() => {
    const points = currentDayTrack.value?.points || []
    const total = points.length
    if (!total) return []

    if (total === 1) {
      return [
        {
          index: 0,
          left: 0,
          label: formatTickTime(points[0].timestamp)
        }
      ]
    }

    const tickCount = Math.min(6, total)
    const indices = new Set<number>()
    for (let i = 0; i < tickCount; i += 1) {
      indices.add(Math.round((i * (total - 1)) / (tickCount - 1)))
    }

    return Array.from(indices)
      .sort((a, b) => a - b)
      .map((idx) => ({
        index: idx,
        left: (idx / (total - 1)) * 100,
        label: formatTickTime(points[idx].timestamp)
      }))
  })

  const formatDateKey = (date: Date) => {
    const y = date.getFullYear()
    const m = String(date.getMonth() + 1).padStart(2, '0')
    const d = String(date.getDate()).padStart(2, '0')
    return `${y}-${m}-${d}`
  }

  const parseDateTime = (value?: string | null) => {
    if (!value) return null
    const normalized = value.includes('T') ? value : value.replace(' ', 'T')
    const ts = Date.parse(normalized)
    return Number.isNaN(ts) ? null : ts
  }

  const loadTrackHistory = async () => {
    const params: { ship_model?: string; days: number } = {
      days: 30
    }

    if (deviceModel.value) {
      params.ship_model = deviceModel.value
    }

    const history = await fetchShipTrackHistory(params)
    const grouped = new Map<string, TrackPoint[]>()

    history.forEach((item) => {
      if (item.longitude == null || item.latitude == null) return

      const timestamp = parseDateTime(item.recordedAt) ?? Date.now()
      const dateKey = formatDateKey(new Date(timestamp))
      const datePoints = grouped.get(dateKey) || []

      datePoints.push({
        date: dateKey,
        time: item.deviceTime || item.recordedAt,
        timestamp,
        coordinate: [item.longitude, item.latitude],
        speed: item.speed,
        course: item.course
      })

      grouped.set(dateKey, datePoints)
    })

    dailyTracks.value = Array.from(grouped.entries())
      .sort((a, b) => a[0].localeCompare(b[0]))
      .map(([date, points]) => ({
        date,
        points: points.sort((a, b) => a.timestamp - b.timestamp).slice(-2000)
      }))

    if (dailyTracks.value.length > 0) {
      selectedTrackIndex.value = dailyTracks.value.length - 1
      progressValue.value = Math.max(currentDayTrack.value?.points.length || 1, 1) - 1
    }
  }

  const clearTrackMarkers = () => {
    markers.forEach((marker) => marker.remove())
    markers = []
  }

  const initMap = () => {
    try {
      if (!MAPBOX_TOKEN) {
        ElMessage.error('未配置 Mapbox Token，请在 .env 中设置 VITE_MAPBOX_TOKEN')
        return
      }

      mapboxgl.accessToken = MAPBOX_TOKEN

      map = new mapboxgl.Map({
        container: 'track-map',
        style: 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json',
        center: [114.3, 30.5],
        zoom: 10
      })

      map.addControl(new mapboxgl.NavigationControl(), 'top-right')

      map.on('load', async () => {
        try {
          await loadTrackHistory()
          drawTrack()
        } catch (error) {
          console.error('加载轨迹历史失败:', error)
          ElMessage.warning('加载历史轨迹失败，已切换实时轨迹')
        }

        await pollTrack()
        startGatewayStream()
      })
    } catch (error) {
      console.error('地图初始化失败:', error)
      ElMessage.error('轨迹地图加载失败')
    }
  }

  const drawTrack = () => {
    if (!map) return

    const dayTrack = currentDayTrack.value
    if (!dayTrack || dayTrack.points.length === 0) return

    const points = dayTrack.points.map((item) => item.coordinate)

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
          coordinates: points
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

    clearTrackMarkers()

    const startMarker = new mapboxgl.Marker({ color: '#52c41a' })
      .setLngLat(points[0])
      .setPopup(new mapboxgl.Popup().setHTML('<strong>起点</strong>'))
      .addTo(map)

    const endMarker = new mapboxgl.Marker({ color: '#f5222d' })
      .setLngLat(points[points.length - 1])
      .setPopup(new mapboxgl.Popup().setHTML('<strong>终点</strong>'))
      .addTo(map)

    markers.push(startMarker, endMarker)

    const selected = dayTrack.points[progressValue.value]
    if (selected) {
      const selectedMarker = new mapboxgl.Marker({ color: '#1890ff' })
        .setLngLat(selected.coordinate)
        .setPopup(
          new mapboxgl.Popup().setHTML(
            `<strong>${selected.time}</strong><br/>速度: ${selected.speed ?? '-'} 节<br/>航向: ${selected.course ?? '-'}°`
          )
        )
        .addTo(map)
      markers.push(selectedMarker)
    }

    if (fittedDate !== dayTrack.date && points.length > 1) {
      const bounds = points.reduce(
        (b, p) => b.extend(p),
        new mapboxgl.LngLatBounds(points[0], points[0])
      )
      map.fitBounds(bounds, { padding: 50 })
      fittedDate = dayTrack.date
    }
  }

  const selectTrack = (index: number) => {
    selectedTrackIndex.value = index
    progressValue.value = Math.max((dailyTracks.value[index]?.points.length || 1) - 1, 0)
    drawTrack()
  }

  const startGatewayStream = () => {
    if (gatewayStream) {
      gatewayStream.close()
      gatewayStream = null
    }

    gatewayStream = new EventSource('/api/ship/gateway/status/?stream=1')
    gatewayStream.addEventListener('gateway-status', (evt: Event) => {
      const msg = evt as MessageEvent
      try {
        const status = JSON.parse(msg.data)
        void pollTrack(status)
      } catch (error) {
        console.warn('解析网关状态流失败:', error)
      }
    })
    gatewayStream.onerror = () => {
      // EventSource will auto-reconnect by default.
    }
  }

  const stopGatewayStream = () => {
    if (gatewayStream) {
      gatewayStream.close()
      gatewayStream = null
    }
  }

  const stopPlayback = () => {
    if (playbackTimer) {
      clearInterval(playbackTimer)
      playbackTimer = null
    }
    isPlaying.value = false
  }

  const togglePlayback = () => {
    const track = currentDayTrack.value
    if (!track || track.points.length <= 1) return

    if (isPlaying.value) {
      stopPlayback()
      return
    }

    isPlaying.value = true
    playbackTimer = window.setInterval(() => {
      if (progressValue.value >= progressMax.value) {
        stopPlayback()
        return
      }
      progressValue.value += 1
    }, 700)
  }

  const resetPlayback = () => {
    stopPlayback()
    progressValue.value = 0
    drawTrack()
  }

  const pollTrack = async (statusPayload?: Awaited<ReturnType<typeof fetchShipGatewayStatus>>) => {
    const status = statusPayload ?? (await fetchShipGatewayStatus())
    const packets = status?.last_boat_packets || {}
    const packet = Object.values(packets).find((item) => {
      if (deviceModel.value) {
        return (item.ship_model || '').toLowerCase() === String(deviceModel.value).toLowerCase()
      }
      return true
    })

    if (!packet || packet.longitude == null || packet.latitude == null) return

    const now = new Date()
    const dateKey = formatDateKey(now)
    const nextPoint: [number, number] = [packet.longitude, packet.latitude]

    let dayIndex = dailyTracks.value.findIndex((item) => item.date === dateKey)
    if (dayIndex < 0) {
      dailyTracks.value.push({ date: dateKey, points: [] })
      dayIndex = dailyTracks.value.length - 1
    }

    const dayPoints = dailyTracks.value[dayIndex].points
    const last = dayPoints[dayPoints.length - 1]
    const isSame = last && last.coordinate[0] === nextPoint[0] && last.coordinate[1] === nextPoint[1]
    if (isSame) return

    dayPoints.push({
      date: dateKey,
      time: now.toLocaleString(),
      timestamp: now.getTime(),
      coordinate: nextPoint,
      speed: packet.speed,
      course: packet.course
    })

    if (dayPoints.length > 2000) {
      dayPoints.shift()
    }

    selectedTrackIndex.value = dayIndex
    progressValue.value = Math.max(dayPoints.length - 1, 0)
    drawTrack()

  }

  const loadPersistedTracks = async () => {
    const records = await fetchShipTrackHistory({
      ship_model: deviceModel.value || undefined,
      days: 7
    })

    if (!records || records.length === 0) return

    const grouped = new Map<string, TrackPoint[]>()
    for (const item of records) {
      const ts = new Date(item.recordedAt.replace(' ', 'T')).getTime()
      if (!Number.isFinite(ts)) continue

      const dateKey = formatDateKey(new Date(ts))
      const points = grouped.get(dateKey) || []
      points.push({
        date: dateKey,
        time: item.recordedAt,
        timestamp: ts,
        coordinate: [item.longitude, item.latitude],
        speed: item.speed,
        course: item.course
      })
      grouped.set(dateKey, points)
    }

    dailyTracks.value = Array.from(grouped.entries())
      .sort((a, b) => a[0].localeCompare(b[0]))
      .map(([date, points]) => ({
        date,
        points: points.sort((p1, p2) => p1.timestamp - p2.timestamp)
      }))

    if (dailyTracks.value.length > 0) {
      selectedTrackIndex.value = dailyTracks.value.length - 1
      progressValue.value = Math.max((currentDayTrack.value?.points.length || 1) - 1, 0)
      drawTrack()
    }
  }

  const handleClose = () => {
    dialogVisible.value = false
  }

  watch(dialogVisible, (val) => {
    if (val) {
      dailyTracks.value = []
      selectedTrackIndex.value = 0
      progressValue.value = 0
      fittedDate = ''
      stopPlayback()
      nextTick(() => {
        initMap()
      })
    } else {
      stopPlayback()
      stopGatewayStream()
      if (map) {
        map.remove()
        map = null
      }
      markers = []
    }
  })

  watch(progressValue, () => {
    drawTrack()
  })

  watch(selectedTrackIndex, () => {
    stopPlayback()
  })

  onUnmounted(() => {
    stopPlayback()
    stopGatewayStream()
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
    width: 220px;
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
      flex: 1;
    }

    .time-count {
      font-size: 12px;
      color: #999;
    }
  }

  .map-section {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .track-map {
    width: 100%;
    height: calc(100% - 86px);
    border-radius: 4px;
    overflow: hidden;
  }

  .timeline-panel {
    padding: 10px 12px 2px;
    border-top: 1px solid #e8e8e8;

    .timeline-meta {
      display: flex;
      justify-content: space-between;
      color: #666;
      font-size: 12px;
      margin-bottom: 6px;
    }

    .timeline-controls {
      display: flex;
      gap: 8px;
      margin-bottom: 8px;
    }

    .timeline-ruler {
      position: relative;
      height: 28px;
      margin-bottom: 2px;

      .timeline-ruler-item {
        position: absolute;
        top: 0;
        transform: translateX(-50%);
        display: flex;
        flex-direction: column;
        align-items: center;
        color: #909399;
        font-size: 11px;
        line-height: 1;

        &.first {
          transform: translateX(0);
          align-items: flex-start;
        }

        &.last {
          transform: translateX(-100%);
          align-items: flex-end;
        }

        .tick {
          width: 1px;
          height: 7px;
          background: #c0c4cc;
          margin-bottom: 3px;
        }

        .label {
          white-space: nowrap;
          letter-spacing: 0;
        }
      }
    }

    .timeline-time {
      color: #333;
      font-size: 13px;
      margin-top: 4px;
      line-height: 1;
    }
  }

  .dialog-footer {
    display: flex;
    justify-content: flex-end;
  }

  :deep(.track-dialog) {
    .el-dialog__body {
      padding: 20px;
    }
  }

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
