import { AppRouteRecord } from '@/types/router'

export const consoleRoute: AppRouteRecord = {
  name: 'Console',
  path: '/console',
  component: '/dashboard/console',
  meta: {
    title: 'menus.dashboard.console',
    icon: 'ri:home-smile-2-line',
    keepAlive: false,
    fixedTab: true,
    roles: ['R_SUPER', 'R_ADMIN']
  }
}

export const analysisRoute: AppRouteRecord = {
  name: 'Analysis',
  path: '/analysis',
  component: '/dashboard/analysis',
  meta: {
    title: 'menus.dashboard.analysis',
    icon: 'ri:align-item-bottom-line',
    keepAlive: false,
    roles: ['R_SUPER', 'R_ADMIN']
  }
}
