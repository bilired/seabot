<template>
  <div class="art-card p-5 h-128 overflow-hidden mb-5 max-sm:mb-4">
    <div class="art-card-header">
      <div class="title">
        <h4>设备位置</h4>
      </div>
      <div class="flex gap-2">
        <ElButton @click="toggleFullscreen" type="primary" size="small">全屏</ElButton>
        <ElButton @click="resetView" type="default" size="small">重置视图</ElButton>
      </div>
    </div>
    <div ref="mapContainer" class="mapbox-container" style="height: 90%"></div>
  </div>
</template>

<script setup lang="ts">
  import { ElMessage } from 'element-plus'
  import mapboxgl from 'mapbox-gl'
  import { fetchShipGatewayStatus } from '@/api/drone'

  const MAPBOX_TOKEN =
    import.meta.env.VITE_MAPBOX_TOKEN ||
    import.meta.env.VITE_MAPBOX_ACCESS_TOKEN ||
    ''

  const mapContainer = ref<HTMLElement>()
  let map: mapboxgl.Map | null = null
  const markers = new Map<string, mapboxgl.Marker>()
  let pollingTimer: number | null = null

  onMounted(() => {
    if (mapContainer.value) {
      try {
        if (!MAPBOX_TOKEN) {
          ElMessage.error('未配置 Mapbox Token，请在 .env 中设置 VITE_MAPBOX_TOKEN')
          return
        }

        mapboxgl.accessToken = MAPBOX_TOKEN

        map = new mapboxgl.Map({
          container: mapContainer.value,
          style: 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json',
          center: [114.3, 30.5],
          zoom: 10,
          pitch: 0,
          bearing: 0
        })

        // 添加导航控件
        map.addControl(new mapboxgl.NavigationControl(), 'top-right')
        
        // 添加缩放级别显示
        map.addControl(new mapboxgl.ScaleControl(), 'bottom-left')

        map.on('load', async () => {
          await refreshBoatMarkers()
          startPolling()
        })
      } catch (error) {
        console.error('地图初始化失败:', error)
        ElMessage.error('地图加载失败')
      }
    }
  })

  onBeforeUnmount(() => {
    if (pollingTimer) {
      clearInterval(pollingTimer)
      pollingTimer = null
    }
    markers.forEach((marker) => marker.remove())
    markers.clear()
    if (map) {
      map.remove()
    }
  })

  const startPolling = () => {
    if (pollingTimer) clearInterval(pollingTimer)
    pollingTimer = window.setInterval(() => {
      refreshBoatMarkers()
    }, 3000)
  }

  const refreshBoatMarkers = async () => {
    if (!map) return

    const status = await fetchShipGatewayStatus()
    const packets = status?.last_boat_packets || {}
    const activePorts = new Set<string>()
    const points: [number, number][] = []

    Object.entries(packets).forEach(([port, packet]) => {
      const lng = packet.longitude
      const lat = packet.latitude
      if (lng == null || lat == null) return

      activePorts.add(port)
      points.push([lng, lat])

      const popupHtml = `
        <div>
          <div><strong>${packet.ship_model || `船体-${port}`}</strong></div>
          <div>端口: ${port}</div>
          <div>经纬度: ${lat.toFixed(6)}, ${lng.toFixed(6)}</div>
          <div>速度: ${packet.speed ?? '-'} 节</div>
          <div>航向: ${packet.direction ?? '-'}°</div>
        </div>
      `

      if (markers.has(port)) {
        markers.get(port)!.setLngLat([lng, lat]).setPopup(new mapboxgl.Popup({ offset: 20 }).setHTML(popupHtml))
      } else {
        const el = document.createElement('div')
        el.className = 'ship-marker'
        el.textContent = '⛵'
        el.style.transform = `rotate(${packet.direction || 0}deg)`

        const marker = new mapboxgl.Marker({ element: el })
          .setLngLat([lng, lat])
          .setPopup(new mapboxgl.Popup({ offset: 20 }).setHTML(popupHtml))
          .addTo(map!)

        markers.set(port, marker)
      }
    })

    Array.from(markers.keys()).forEach((port) => {
      if (!activePorts.has(port)) {
        markers.get(port)?.remove()
        markers.delete(port)
      }
    })

    if (points.length > 0) {
      const bounds = points.reduce(
        (b, p) => b.extend(p),
        new mapboxgl.LngLatBounds(points[0], points[0])
      )
      map.fitBounds(bounds, { padding: 40, maxZoom: 14, duration: 800 })
    }
  }

  const toggleFullscreen = () => {
    if (!mapContainer.value) return

    if (!document.fullscreenElement) {
      mapContainer.value.requestFullscreen?.()
    } else {
      document.exitFullscreen?.()
    }
  }

  const resetView = () => {
    if (!map) return

    map.flyTo({
      center: [114.3, 30.5],
      zoom: 10,
      duration: 1500
    })
  }
</script>

<style lang="scss" scoped>
  .mapbox-container {
    width: 100%;
    height: 100%;
    border-radius: 4px;
    overflow: hidden;
  }

  .ship-marker {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: rgba(24, 144, 255, 0.18);
    border: 2px solid #1890ff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    cursor: pointer;
  }

  :deep(.mapboxgl-popup-content) {
    background: rgba(0, 0, 0, 0.75);
    color: white;
    padding: 8px 12px;
    border-radius: 4px;
    font-size: 14px;
  }

  :deep(.mapboxgl-popup-close-button) {
    color: white;
  }

  :deep(.mapboxgl-ctrl) {
    background: white;
    border-radius: 4px;
    margin: 10px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  :deep(.mapboxgl-ctrl-bottom-left) {
    display: flex;
    align-items: center;
    padding: 8px;
  }
</style>
