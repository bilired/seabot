<template>
  <div class="art-card p-5 mb-5 max-sm:mb-4">
    <div class="art-card-header">
      <div class="title">
        <h4>无人船状态</h4>
      </div>
    </div>

    <div class="ship-status-grid">
      <div v-for="item in shipStatusList" :key="item.ship_model" class="ship-status-item">
        <!-- 标题行 -->
        <div class="ship-status-header">
          <h5>{{ item.ship_model }}</h5>
          <ElTag :type="item.online ? 'success' : 'info'" effect="dark" round>
            {{ item.online ? '在线' : '离线' }}
          </ElTag>
        </div>

        <!-- 数据字段双列布局 -->
        <div class="ship-fields">
          <div class="ship-field">
            <span class="field-label">纬度</span>
            <strong>{{ item.latitude != null ? item.latitude.toFixed(6) : '--' }}</strong>
          </div>
          <div class="ship-field">
            <span class="field-label">经度</span>
            <strong>{{ item.longitude != null ? item.longitude.toFixed(6) : '--' }}</strong>
          </div>
          <div class="ship-field">
            <span class="field-label">航向</span>
            <strong>{{ item.course != null ? item.course + '°' : '--' }}</strong>
          </div>
          <div class="ship-field">
            <span class="field-label">速度</span>
            <strong>{{ item.speed != null ? item.speed + ' m/s' : '--' }}</strong>
          </div>
          <div class="ship-field">
            <span class="field-label">电池电压</span>
            <strong>{{ item.battery_level || '--' }}</strong>
          </div>
          <div class="ship-field">
            <span class="field-label">采水状态</span>
            <strong>{{ item.water_extraction || '--' }}</strong>
          </div>
          <div class="ship-field ship-field--full">
            <span class="field-label">设备时间</span>
            <strong>{{ formatDeviceTime(item.boat_timestamp) }}</strong>
          </div>
          <div v-if="!item.online" class="ship-field ship-field--full ship-field--offline">
            <span class="field-label">最后更新</span>
            <strong>{{ item.recorded_at || '--' }}</strong>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { onBeforeUnmount, onMounted, ref } from 'vue'

  interface ShipStatusItem {
    ship_model: string
    online: boolean
    latitude?: number | null
    longitude?: number | null
    course?: number | null
    speed?: number | null
    battery_level?: string | null
    water_extraction?: string | null
    boat_timestamp?: string | null
    recorded_at?: string | null
  }

  const TARGET_SHIPS = ['DL-3022', 'DL-3026']
  const shipStatusList = ref<ShipStatusItem[]>(
    TARGET_SHIPS.map((ship) => ({
      ship_model: ship,
      online: false,
      latitude: null,
      longitude: null,
      course: null,
      speed: null,
      battery_level: null,
      water_extraction: null,
      boat_timestamp: null,
      recorded_at: null
    }))
  )

  let statusStream: EventSource | null = null

  function formatDeviceTime(raw?: string | null): string {
    if (!raw) return '--'
    // Device timestamp is reported in UTC; convert it to local time for display.
    const m = raw.match(/^(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})$/)
    if (!m) return raw

    const utcDate = new Date(Date.UTC(
      Number(m[1]),
      Number(m[2]) - 1,
      Number(m[3]),
      Number(m[4]),
      Number(m[5]),
      Number(m[6])
    ))

    const year = utcDate.getFullYear()
    const month = String(utcDate.getMonth() + 1).padStart(2, '0')
    const day = String(utcDate.getDate()).padStart(2, '0')
    const hour = String(utcDate.getHours()).padStart(2, '0')
    const minute = String(utcDate.getMinutes()).padStart(2, '0')
    const second = String(utcDate.getSeconds()).padStart(2, '0')

    return `${year}-${month}-${day} ${hour}:${minute}:${second}`
  }

  function pickShipLocation(locations: any[], shipModel: string) {
    const exact = locations.find((item) => (item?.ship_model || '').toUpperCase() === shipModel)
    if (exact) return exact
    return locations.find((item) => (item?.ship_model || '').toUpperCase().includes(shipModel))
  }

  function applyShipStatus(statuses: any[]) {
    shipStatusList.value = TARGET_SHIPS.map((ship) => {
      const loc = pickShipLocation(statuses, ship)
      if (!loc) {
        return {
          ship_model: ship,
          online: false,
          latitude: null,
          longitude: null,
          course: null,
          speed: null,
          battery_level: null,
          water_extraction: null,
          boat_timestamp: null,
          recorded_at: null
        }
      }

      return {
        ship_model: ship,
        online: !!loc.online,
        latitude: loc.latitude ?? null,
        longitude: loc.longitude ?? null,
        course: loc.course ?? null,
        speed: loc.speed ?? null,
        battery_level: loc.battery_level ?? null,
        water_extraction: loc.water_extraction ?? null,
        boat_timestamp: loc.boat_timestamp ?? null,
        recorded_at: loc.recorded_at ?? null
      }
    })
  }

  function startStatusStream() {
    if (statusStream) {
      statusStream.close()
      statusStream = null
    }

    statusStream = new EventSource('/api/ship/device-status/?stream=1')

    statusStream.addEventListener('device-status', (evt: Event) => {
      const message = evt as MessageEvent
      try {
        const statuses = JSON.parse(message.data)
        if (Array.isArray(statuses)) {
          applyShipStatus(statuses)
        }
      } catch (error) {
        console.warn('解析船状态推送失败:', error)
      }
    })

    statusStream.onerror = () => {
      // EventSource 默认会自动重连，这里保持静默避免频繁提示。
    }
  }

  onMounted(() => {
    startStatusStream()
  })

  onBeforeUnmount(() => {
    if (statusStream) {
      statusStream.close()
      statusStream = null
    }
  })
</script>

<style scoped>
  .ship-status-grid {
    margin-top: 14px;
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }

  @media (max-width: 640px) {
    .ship-status-grid {
      grid-template-columns: 1fr;
    }
  }

  .ship-status-item {
    border: 1px solid var(--el-border-color);
    border-radius: 10px;
    padding: 14px 16px;
    background: var(--art-main-bg-color);
  }

  .ship-status-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }

  .ship-status-header h5 {
    margin: 0;
    font-size: 15px;
    font-weight: 700;
  }

  .ship-fields {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 6px 12px;
  }

  .ship-field {
    display: flex;
    flex-direction: column;
    font-size: 13px;
  }

  .ship-field--full {
    grid-column: 1 / -1;
  }

  .ship-field--offline strong {
    color: var(--el-text-color-secondary);
  }

  .field-label {
    font-size: 11px;
    color: var(--el-text-color-secondary);
    margin-bottom: 1px;
  }

  .ship-field strong {
    color: var(--art-text-gray-900);
    font-weight: 600;
  }
</style>
