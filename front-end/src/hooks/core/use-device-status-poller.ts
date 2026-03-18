import { fetchDeviceStatus, type DeviceStatus } from '@/api/drone'

type DeviceStatusListener = (statuses: DeviceStatus[]) => void

const listeners = new Set<DeviceStatusListener>()
let latestStatuses: DeviceStatus[] = []
let timer: ReturnType<typeof setInterval> | null = null
let inFlight = false

const DEVICE_STATUS_POLL_MS = 3000

function notifyAll() {
  listeners.forEach((listener) => {
    listener(latestStatuses)
  })
}

async function refreshDeviceStatuses() {
  if (inFlight) return
  inFlight = true
  try {
    const statuses = await fetchDeviceStatus()
    latestStatuses = Array.isArray(statuses) ? statuses : []
    notifyAll()
  } catch {
    // Keep previous snapshot on transient network errors.
  } finally {
    inFlight = false
  }
}

function ensurePolling() {
  if (timer) return
  timer = setInterval(() => {
    void refreshDeviceStatuses()
  }, DEVICE_STATUS_POLL_MS)
}

function stopPollingIfIdle() {
  if (listeners.size > 0) return
  if (!timer) return
  clearInterval(timer)
  timer = null
}

export function subscribeDeviceStatus(listener: DeviceStatusListener) {
  listeners.add(listener)

  if (latestStatuses.length > 0) {
    listener(latestStatuses)
  } else {
    void refreshDeviceStatuses()
  }

  ensurePolling()

  return () => {
    listeners.delete(listener)
    stopPollingIfIdle()
  }
}
