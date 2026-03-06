import { AppRouteRecord } from '@/types/router'
import { analysisRoute, consoleRoute } from './dashboard'
import { droneRoute, userCenterRoute, userRoute } from './system'

/**
 * 导出所有模块化路由
 */
export const routeModules: AppRouteRecord[] = [
  consoleRoute,
  analysisRoute,
  droneRoute,
  userRoute,
  userCenterRoute
]
