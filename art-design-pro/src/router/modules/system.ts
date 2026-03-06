import { AppRouteRecord } from '@/types/router'

export const droneRoute: AppRouteRecord = {
  path: '/drone',
  name: 'DroneManage',
  component: '/system/drone',
  meta: {
    title: 'menus.system.drone',
    icon: 'ri:ship-line',
    keepAlive: true,
    roles: ['R_SUPER', 'R_ADMIN']
  }
}

export const userRoute: AppRouteRecord = {
  path: '/user',
  name: 'User',
  component: '/system/user',
  meta: {
    title: 'menus.system.user',
    icon: 'ri:user-line',
    keepAlive: true,
    roles: ['R_SUPER', 'R_ADMIN']
  }
}

export const userCenterRoute: AppRouteRecord = {
  path: '/user-center',
  name: 'UserCenter',
  component: '/system/user-center',
  meta: {
    title: 'menus.system.userCenter',
    icon: 'ri:user-line',
    isHide: true,
    keepAlive: true,
    isHideTab: true,
    roles: ['R_SUPER', 'R_ADMIN', 'R_USER']
  }
}
