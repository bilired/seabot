import { AppRouteRecord } from '@/types/router'
import { analysisRoute, consoleRoute, videoStreamMonitorRoute } from './dashboard'
import {
  changePasswordRoute,
  droneRoute,
  imageTransferHistoryRoute,
  userCenterRoute,
  userRoute
} from './system'
import { templateRoutes } from './template'

/**
 * 导出所有模块化路由
 */
export const routeModules: AppRouteRecord[] = [
  consoleRoute,
  analysisRoute,
  videoStreamMonitorRoute,
  templateRoutes,
  droneRoute,
  imageTransferHistoryRoute,
  userRoute,
  userCenterRoute,
  changePasswordRoute
]
