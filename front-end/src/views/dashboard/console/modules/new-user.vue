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
    <div ref="mapContainer" class="mapbox-container" style="height: 90%";></div>
  </div>
</template>

<script setup lang="ts">
  import mapboxgl from 'mapbox-gl'

  const mapContainer = ref<HTMLElement>()
  let map: mapboxgl.Map | null = null

  // 设置 Mapbox access token（需要替换为你的实际token）
  mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN || 'pk.eyJ1IjoiZXhhbXBsZSIsImEiOiJjbHZkMzZ0d3oifQ.fake'

  onMounted(() => {
    if (mapContainer.value) {
      try {
        map = new mapboxgl.Map({
          container: mapContainer.value,
          style: 'mapbox://styles/mapbox/streets-v12',
          center: [116.4074, 39.9042], // 北京坐标
          zoom: 10,
          pitch: 0,
          bearing: 0
        })

        // 添加导航控件
        map.addControl(new mapboxgl.NavigationControl(), 'top-right')
        
        // 添加地理位置控件
        map.addControl(new mapboxgl.GeolocateControl({
          positionOptions: {
            enableHighAccuracy: true
          },
          trackUserLocation: true
        }), 'top-right')

        // 添加缩放级别显示
        map.addControl(new mapboxgl.ScaleControl(), 'bottom-left')

        // 添加示例标记
        addMarkers()
      } catch (error) {
        console.error('地图初始化失败:', error)
        ElMessage.error('地图加载失败，请检查 Mapbox token')
      }
    }
  })

  onBeforeUnmount(() => {
    if (map) {
      map.remove()
    }
  })

  const addMarkers = () => {
    if (!map) return

    const locations = [
      { lng: 116.4074, lat: 39.9042, name: '北京' },
      { lng: 121.4737, lat: 31.2304, name: '上海' },
      { lng: 114.0579, lat: 22.5431, name: '深圳' }
    ]

    locations.forEach(location => {
      const el = document.createElement('div')
      el.className = 'marker'
      el.style.backgroundImage = 'url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0Ij48cGF0aCBkPSJNMTIgMkM2LjQ4IDIgMiA2LjQ4IDIgMTJjMCA1LjQ2IDUuNDUgMTAgMTAgMTAgNC4zNzcgMCA4LjAxLTMuMDk1IDguNjk2LTcuMDEzQzIyLjE3NiAxNi40NDQgMjIgMTYuNjYgMjIgMTYuODc0YzAtMS4xMDMtMC44OTctMi0yLTJoLS4wMWMtMS4xMjEgMC0yLjAzMyAwLjg5LTIuMDQgMi4wMDhDMTcuNzE3IDE3LjUxNiAxNS41MTYgMTkgMTMgMTljLTIuNzYgMC01LTIuMjQtNS01czIuMjQtNSA1LTVjMS43NzMgMCAzLjI5Ljg4IDQuMjgyIDIuMDAxTDEzIDExaDVWNi41YzAtMC4yNzcuMjIzLS41LjUtLjVoMS41YzEuOTMgMCAzLjUgMS41NyAzLjUgMy41djEuMTU0YzAtMi4wMDIgMS41NzctMy42NTQgMy41LTMuNjU0YzEuMTk3IDAgMi4yNDguNTMyIDIuOTYxIDEuMzY5QzIzLjIgOC41MjQgMjMuNjEgOC4yODkgMjMuNjEgNy43NTZDMjMuNjEgNy4zNDcgMjMuNDM0IDcuMDEyIDIzLjEzNCA2LjgyQzIzLjUyNCA1LjE1MSAyMS43NzQgMiAxMiAyek0xMiAxMHEtMS42NjUgMC0yLjgzNyAxLjE3MlQxNiAxMnExLjY2NSAwIDIuODM3LTEuMTcyVDEyIDEweiIgZmlsbD0iI0ZGMDAwMCIvPjwvc3ZnPg==)'
      el.style.backgroundSize = '100%'
      el.style.width = '32px'
      el.style.height = '32px'
      el.style.cursor = 'pointer'

      const popup = new mapboxgl.Popup({ offset: 25 }).setText(location.name)

      new mapboxgl.Marker(el)
        .setLngLat([location.lng, location.lat])
        .setPopup(popup)
        .addTo(map!)
    })
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
      center: [116.4074, 39.9042],
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
