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

export interface ImageTransferItem {
  id: string
  shipModel: string
  imageUid: string
  timestamp: string
  imageFormat: string
  resolution: string
  fileSizeMB: number
  imageUrl: string
}

export interface ImageTransferListData {
  records: ImageTransferItem[]
  current: number
  size: number
  total: number
}

export interface ImageTransferListParams {
  current: number
  size: number
  model?: string
  imageUid?: string
  imageFormat?: string
  startTime?: string
  endTime?: string
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

export function uploadDroneImage(file: File, shipModel?: string) {
  const formData = new FormData()
  formData.append('file', file)
  if (shipModel) {
    formData.append('shipModel', shipModel)
  }

  return request.post<{ url: string; imageUid: string }>({
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

export function fetchImageTransferHistory(params: ImageTransferListParams) {
  return request.get<ImageTransferListData>({
    url: '/api/drone/image-history/list/',
    params
  })
}

export function deleteImageTransferRecord(data: { id: string }) {
  return request.post({
    url: '/api/drone/image-history/delete/',
    data
  })
}

export function batchDeleteImageTransferRecords(data: { ids: string[] }) {
  return request.post<{ deleted: number }>({
    url: '/api/drone/image-history/batch-delete/',
    data
  })
}
