import request from '@/utils/http'

interface DashboardStatsData {
  onlineDevices: number
  systemUptime: number
  monthlyNewDevices: number
  todayActivities: number
  updatedAt: string
}

/**
 * 获取仪表板统计数据
 * @returns 仪表板统计数据
 */
export function fetchDashboardStats() {
  return request.get<DashboardStatsData>({
    url: '/api/dashboard/stats/'
  })
}

/**
 * 获取用户活动日志
 * @param limit 返回的记录数
 * @returns 用户活动列表
 */
export function fetchUserActivity(limit: number = 10) {
  return request.get<
    Array<{
      id: number
      activityType: string
      description: string
      createdAt: string
    }>
  >({
    url: '/api/dashboard/activity/',
    params: {
      limit
    }
  })
}

/**
 * 获取销售数据
 * @returns 销售数据列表
 */
export function fetchSalesData() {
  return request.get<
    Array<{
      month: string
      sales: number
    }>
  >({
    url: '/api/dashboard/sales/'
  })
}

/**
 * 获取用户增长数据
 * @returns 用户增长数据列表
 */
export function fetchUserGrowth() {
  return request.get<
    Array<{
      date: string
      newUsers: number
      activeUsers: number
    }>
  >({
    url: '/api/dashboard/growth/'
  })
}

/**
 * 获取水质监测数据
 * @returns 水质数据列表
 */
export function fetchWaterQualityData() {
  return request.get<
    Array<{
      ship_model: string
      timestamp: string
      warn: string
      temperature: number
      pH: number
      chlorophyll: number
      salinity: number
      dissolved_oxygen: number
      conductivity: number
      turbidity: number
      'blue-green': number
    }>
  >({
    url: '/api/analysis/water-quality/'
  })
}

/**
 * 获取营养盐数据
 * @returns 营养盐数据列表
 */
export function fetchNutrientData() {
  return request.get<
    Array<{
      data_id: string
      timestamp: string | null
      status: number
      ammonia_nitrogen: number
      ammonia_nitrogen_timestamp: string
      nitrate: number
      nitrate_timestamp: string
      sub_nitrate: number
      sub_nitrate_timestamp: string
      phosphates: number
      phosphates_timestamp: string
      warn: string
    }>
  >({
    url: '/api/analysis/nutrient/'
  })
}

/**
 * 获取视频流传输记录
 * @returns 视频流传输记录列表
 */
export function fetchVideoStreamData() {
  return request.get<
    Array<{
      ship_model: string
      timestamp: string
      stream_protocol: string
      video_codec: string
      transport_protocol: string
      source_ip: string
      source_port: number | null
      target_ip: string
      target_port: number | null
      stream_url: string
      resolution: string
      fps: number | null
      bitrate_kbps: number | null
      packet_size: number | null
      packet_count: number
      frame_count: number
      loss_rate: number
      latency_ms: number | null
      jitter_ms: number | null
      status: string
      warn: string
    }>
  >({
    url: '/api/analysis/video-stream/'
  })
}
