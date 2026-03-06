import request from '@/utils/http'
import { AppRouteRecord } from '@/types/router'

// 获取用户列表
export function fetchGetUserList(params: Api.SystemManage.UserSearchParams) {
  return request.get<Api.SystemManage.UserList>({
    url: '/api/user/list/',
    params
  })
}

export function fetchCreateUser(data: Api.SystemManage.UserSubmitParams) {
  return request.post<{ id: number }>({
    url: '/api/user/create/',
    data
  })
}

export function fetchUpdateUser(data: Api.SystemManage.UserSubmitParams & { id: number }) {
  return request.post<{ id: number }>({
    url: '/api/user/update/',
    data
  })
}

export function fetchDeleteUser(data: { id: number }) {
  return request.post({
    url: '/api/user/delete/',
    data
  })
}

// 获取角色列表
export function fetchGetRoleList(params: Api.SystemManage.RoleSearchParams) {
  return request.get<Api.SystemManage.RoleList>({
    url: '/api/role/list',
    params
  })
}

// 获取菜单列表
export function fetchGetMenuList() {
  return request.get<AppRouteRecord[]>({
    url: '/api/v3/system/menus'
  })
}
