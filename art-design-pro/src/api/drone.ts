import request from '@/utils/http'
import type { BaseResponse } from '@/types'

export interface DroneItem {
  id: string
  shipType: string
  length: number
  model: string
  weight: number
  functions: string
  image?: string
  streamUrl?: string
  status: 'online' | 'offline'
  maxSpeed: number
}

export interface DroneListData {
  records: DroneItem[]
  current: number
  size: number
  total: number
}

export interface DroneListResponse extends BaseResponse {
  data: DroneListData
}

export interface ShipActionParams {
  cmd: string
  shipPort: number
  controlPort: number
}

export interface ShipActionResult {
  cmd: string
  packet_hex: string
  delivered_ports: number[]
  failed_ports: number[]
}

export function fetchDroneList(params: { current: number; size: number; keyword?: string }) {
  return request.get<DroneListResponse>({
    url: '/api/drone/list/',
    params
  }) as Promise<any>
}

export function createDrone(data: Omit<DroneItem, 'id'>) {
  return request.post<{ id: string }>({
    url: '/api/drone/create/',
    data
  })
}

export function updateDrone(data: DroneItem) {
  return request.post<{ id: string }>({
    url: '/api/drone/update/',
    data
  })
}

export function deleteDrone(data: { id: string }) {
  return request.post({
    url: '/api/drone/delete/',
    data
  })
}

export function batchDeleteDrone(data: { ids: string[] }) {
  return request.post<{ deleted: number }>({
    url: '/api/drone/batch-delete/',
    data
  })
}

export function uploadDroneImage(file: File) {
  const formData = new FormData()
  formData.append('file', file)

  return request.post<{ url: string }>({
    url: '/api/drone/upload-image/',
    data: formData
  })
}

export function sendShipAction(data: ShipActionParams) {
  return request.post<ShipActionResult>({
    url: '/api/ship/action/',
    data
  })
}
