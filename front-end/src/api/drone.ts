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
  ship_model: string
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

export interface ShipGatewayStatusData {
  running: boolean
  host: string
  port_start: number
  ship_count: number
  online_ports: number[]
  reported_models?: Record<string, string>
  last_boat_packets?: Record<string, {
    ship_model: string
    boat_timestamp?: string | null
    latitude?: number | null
    longitude?: number | null
    course?: number | null
    speed?: number | null
    battery_level?: string | null
    water_extraction?: string | null
    raw: string
  }>
  last_depth_packets?: Record<string, {
    timestamp: string | null
    depth: number
  }>
  last_rtk_packets?: Record<string, {
    depth?: number | null
    rtk_latitude?: number | null
    rtk_latitude_direction?: string | null
    rtk_longitude?: number | null
    rtk_longitude_direction?: string | null
    temperature?: number | null
    rtk_elevation?: number | null
    raw: string
  }>
}

export interface ShipTrackHistoryParams {
  ship_model?: string
  shipPort?: number
  days?: number
  startDate?: string
  endDate?: string
}

export interface ShipTrackHistoryItem {
  id: number
  ship_model: string
  shipPort?: number | null
  boatTimestamp?: string | null
  deviceTime?: string | null
  latitude: number
  longitude: number
  course?: number | null
  speed?: number | null
  battery_level?: string | null
  water_extraction?: string | null
  recordedAt: string
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

export function uploadDroneImage(file: File, ship_model?: string) {
  const formData = new FormData()
  formData.append('file', file)
  if (ship_model) {
    formData.append('ship_model', ship_model)
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

export function fetchShipGatewayStatus() {
  return request.get<ShipGatewayStatusData>({
    url: '/api/ship/gateway/status/'
  })
}

export interface DeviceLocation {
  ship_model: string
  latitude: number
  longitude: number
}

export interface DeviceStatus {
  ship_model: string
  latitude: number
  longitude: number
  course?: number | null
  speed?: number | null
  battery_level?: string | null
  water_extraction?: string | null
  boat_timestamp?: string | null
  online: boolean
  source_port?: string
  recorded_at?: string
}

export function fetchDeviceLocations() {
  return request.get<DeviceLocation[]>({
    url: '/api/ship/device-locations/'
  })
}

export function fetchDeviceStatus() {
  return request.get<DeviceStatus[]>({
    url: '/api/ship/device-status/'
  })
}

export function fetchShipTrackHistory(params: ShipTrackHistoryParams) {
  return request.get<ShipTrackHistoryItem[]>({
    url: '/api/ship/track/history/',
    params
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
