<template>
  <div class="art-card p-5 h-128 overflow-hidden mb-5 max-sm:mb-4">
    <div class="art-card-header">
      <div class="title">
        <h4>设备位置</h4>
      </div>
      <div class="flex gap-2 items-center">
        <span class="legend-item"><span class="legend-dot" style="background:#e53e3e"></span>DL-3022 在线</span>
        <span class="legend-item"><span class="legend-dot" style="background:#2b6cb0"></span>DL-3026 在线</span>
        <span class="legend-item"><span class="legend-dot" style="background:#888"></span>离线</span>
        <ElButton @click="toggleFullscreen" type="primary" size="small">全屏</ElButton>
        <ElButton @click="resetView" type="default" size="small">重置视图</ElButton>
      </div>
    </div>
    <div ref="mapContainer" class="mapbox-container" style="height: 85%"></div>
  </div>
</template>

<script setup lang="ts">
  import { ElMessage } from 'element-plus'
  import mapboxgl from 'mapbox-gl'
  import type { DeviceLocation } from '@/api/drone'
  import { fetchDeviceLocations } from '@/api/drone'

  const MAPBOX_TOKEN =
    import.meta.env.VITE_MAPBOX_TOKEN ||
    import.meta.env.VITE_MAPBOX_ACCESS_TOKEN ||
    ''

  const mapContainer = ref<HTMLElement>()
  let map: mapboxgl.Map | null = null
  // key = ship_model
  const markers = new Map<string, mapboxgl.Marker>()
  let pollingTimer: number | null = null
  let initialFitDone = false

  /** Resolve marker color by model + online status */
  function markerColor(loc: DeviceLocation): string {
    if (!loc.online) return '#888888'
    const m = (loc.ship_model || '').toUpperCase()
    if (m.includes('DL-3022')) return '#e53e3e'
    if (m.includes('DL-3026')) return '#2b6cb0'
    return '#1890ff'
  }

  function buildMarkerEl(loc: DeviceLocation): HTMLElement {
    const color = markerColor(loc)
    const el = document.createElement('div')
    el.className = 'ship-marker'
    el.style.borderColor = color
    el.style.background = `${color}22`
    // Arrow svg rotated to course
    const course = loc.course ?? 0
    el.innerHTML = `<svg viewBox="0 0 24 24" width="38" height="38" style="transform:rotate(${course}deg);display:block">
      <path d="M12 2 L19 20 L12 15 L5 20 Z" fill="${color}" stroke="white" stroke-width="1"/>
    </svg>`
    el.style.opacity = loc.online ? '1' : '0.55'
    return el
  }

  function buildPopup(loc: DeviceLocation): mapboxgl.Popup {
    const statusLabel = loc.online
      ? '<span style="color:#68d391">● 在线</span>'
      : `<span style="color:#aaa">● 离线（最后位置 ${loc.recorded_at ?? ''}）</span>`
    const html = `
      <div>
        <div><strong>${loc.ship_model}</strong> &nbsp; ${statusLabel}</div>
        <div>经纬度: ${loc.latitude.toFixed(6)}, ${loc.longitude.toFixed(6)}</div>
        <div>速度: ${loc.speed ?? '-'} 节 &nbsp; 航向: ${loc.course ?? '-'}°</div>
        ${loc.battery_level ? `<div>电量: ${loc.battery_level}</div>` : ''}
      </div>
    `
    return new mapboxgl.Popup({ offset: 20 }).setHTML(html)
  }

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

        map.addControl(new mapboxgl.NavigationControl(), 'top-right')
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

    let locations: DeviceLocation[] = []
    try {
      const res = await fetchDeviceLocations()
      locations = Array.isArray(res) ? res : ((res as any)?.data ?? [])
    } catch {
      return
    }

    const activeModels = new Set<string>()
    const points: [number, number][] = []

    locations.forEach((loc) => {
      const key = loc.ship_model
      if (loc.latitude == null || loc.longitude == null) return

      activeModels.add(key)
      if (loc.online) points.push([loc.longitude, loc.latitude])

      if (markers.has(key)) {
        const marker = markers.get(key)!
        // Update position
        marker.setLngLat([loc.longitude, loc.latitude])
        // Update popup
        marker.setPopup(buildPopup(loc))
        // Update visual: target the .ship-marker div inside Mapbox's wrapper
        const wrapper = marker.getElement()
        const el = (wrapper.querySelector('.ship-marker') as HTMLElement) ?? wrapper
        const color = markerColor(loc)
        el.style.borderColor = color
        el.style.background = `${color}22`
        el.style.opacity = loc.online ? '1' : '0.55'
        el.innerHTML = `<svg viewBox="0 0 24 24" width="28" height="28" style="transform:rotate(${loc.course ?? 0}deg);display:block">
          <path d="M12 2 L19 20 L12 15 L5 20 Z" fill="${color}" stroke="white" stroke-width="1"/>
        </svg>`
      } else {
        const el = buildMarkerEl(loc)
        const marker = new mapboxgl.Marker({ element: el })
          .setLngLat([loc.longitude, loc.latitude])
          .setPopup(buildPopup(loc))
          .addTo(map!)
        markers.set(key, marker)
      }
    })

    // Remove markers for models no longer in any response
    Array.from(markers.keys()).forEach((key) => {
      if (!activeModels.has(key)) {
        markers.get(key)?.remove()
        markers.delete(key)
      }
    })

    // Auto-fit only on the very first load; never interrupt user pan/zoom after that
    if (!initialFitDone && points.length > 0) {
      const bounds = points.reduce(
        (b, p) => b.extend(p),
        new mapboxgl.LngLatBounds(points[0], points[0])
      )
      map.fitBounds(bounds, { padding: 60, maxZoom: 14, duration: 800 })
      initialFitDone = true
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
    map.flyTo({ center: [114.3, 30.5], zoom: 10, duration: 1500 })
  }
</script>

<style lang="scss" scoped>
  .mapbox-container {
    width: 100%;
    height: 100%;
    border-radius: 4px;
    overflow: hidden;
  }

  .legend-item {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 12px;
    color: var(--art-text-gray-600);
    white-space: nowrap;
  }

  .legend-dot {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .ship-marker {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    border: 2.5px solid #1890ff;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: opacity 0.3s;
  }

  :deep(.mapboxgl-popup-content) {
    background: rgba(0, 0, 0, 0.75);
    color: white;
    padding: 8px 12px;
    border-radius: 4px;
    font-size: 14px;
    min-width: 200px;
  }

  :deep(.mapboxgl-popup-close-button) {
    color: white;
  }

  :deep(.mapboxgl-ctrl) {
    background: white;
  }

  /* Remove any background/border Mapbox may inject into the marker wrapper div */
  :deep(.mapboxgl-marker) {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
  }
</style>
