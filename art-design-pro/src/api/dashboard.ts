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
      shipModel: string
      temperature: number
      ph: number
      chlorophyll: number
      salinity: number
      dissolvedOxygen: number
      conductivity: number
      turbidity: number
      algae: number
      warningCode: string
      collectionTime: string
      connectionStatus: string
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
      shipModel: string
      phosphate: number
      phosphateTime: string
      ammonia: number
      ammoniaTime: string
      nitrate: number
      nitrateTime: string
      nitrite: number
      nitriteTime: string
      errorCode1: string
      errorCode2: string
      instrumentStatus: string
      collectionTime: string
      connectionStatus: string
    }>
  >({
    url: '/api/analysis/nutrient/'
  })
}
