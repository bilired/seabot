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

export const imageTransferHistoryRoute: AppRouteRecord = {
  path: '/image-transfer-history',
  name: 'ImageTransferHistory',
  component: '/system/image-transfer-history',
  meta: {
    title: 'menus.system.imageTransferHistory',
    icon: 'ri:image-2-line',
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

export const changePasswordRoute: AppRouteRecord = {
  path: '/change-password',
  name: 'ChangePassword',
  component: '/system/change-password',
  meta: {
    title: 'menus.system.changePassword',
    icon: 'ri:lock-password-line',
    isHide: true,
    keepAlive: true,
    isHideTab: true,
    roles: ['R_SUPER', 'R_ADMIN', 'R_USER']
  }
}
