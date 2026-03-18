<template>
  <div class="art-card h-128 p-5 mb-5 max-sm:mb-4">
    <div class="art-card-header">
      <div class="title">
        <h4>代办事项</h4>
        <p>待处理<span class="text-danger">{{ pendingCount }}</span></p>
      </div>
      <ElButton type="primary" link @click="openCalendarDialog">查看</ElButton>
    </div>

    <div class="h-[calc(100%-40px)] overflow-auto">
      <ElScrollbar>
        <div
          class="flex-cb h-17.5 border-b border-g-300 text-sm last:border-b-0"
          v-for="event in calendarEvents"
          :key="event.id"
        >
          <div>
            <p class="text-sm">{{ event.title }}</p>
            <p class="text-g-500 mt-1">{{ event.date }} {{ event.time }}</p>
          </div>
          <ElCheckbox v-model="event.complate" />
        </div>
      </ElScrollbar>
    </div>
  </div>

  <ElDialog v-model="calendarDialogVisible" title="日历总览" width="900px" destroy-on-close>
    <ElCalendar v-model="calendarCurrentDate">
      <template #date-cell="{ data }">
        <div class="h-full p-1 cursor-pointer" @click="openDayEvents(data.day)">
          <p class="text-xs text-right mb-1">{{ data.day.split('-')[2] }}</p>
          <div class="space-y-1">
            <p
              v-for="event in getEventsByDate(data.day).slice(0, 2)"
              :key="`${event.date}-${event.title}`"
              class="text-xs truncate px-1 py-0.5 rounded bg-theme/12 text-theme"
            >
              {{ event.title }}
            </p>
          </div>
        </div>
      </template>
    </ElCalendar>

    <template #footer>
      <ElButton @click="calendarDialogVisible = false">关闭</ElButton>
      <ElButton type="primary" @click="openCreateEventDialog">新增事项</ElButton>
    </template>
  </ElDialog>

  <ElDialog v-model="dayEventsDialogVisible" :title="`${selectedDay} 当日事项`" width="520px" destroy-on-close>
    <ElEmpty v-if="selectedDayEvents.length === 0" description="当天暂无事项" />
    <ElTimeline v-else>
      <ElTimelineItem
        v-for="event in selectedDayEvents"
        :key="event.id"
        :timestamp="event.time"
      >
        <span class="cursor-pointer hover:text-theme" @click="openEditEventDialog(event)">{{ event.title }}</span>
      </ElTimelineItem>
    </ElTimeline>
    <template #footer>
      <ElButton @click="dayEventsDialogVisible = false">关闭</ElButton>
      <ElButton type="primary" @click="openCreateEventDialog">新增事项</ElButton>
    </template>
  </ElDialog>

  <ElDialog v-model="eventFormDialogVisible" :title="isEditingEvent ? '修改事项' : '新增日程'" width="520px" destroy-on-close>
    <ElForm :model="eventForm" label-width="80px">
      <ElFormItem label="标题">
        <ElInput v-model="eventForm.title" placeholder="请输入事项标题" />
      </ElFormItem>
      <ElFormItem label="日期">
        <ElDatePicker
          v-model="eventForm.date"
          type="date"
          value-format="YYYY-MM-DD"
          format="YYYY-MM-DD"
          style="width: 100%"
        />
      </ElFormItem>
      <ElFormItem label="时间">
        <ElTimePicker v-model="eventForm.time" format="HH:mm" value-format="HH:mm" style="width: 100%" />
      </ElFormItem>
    </ElForm>
    <template #footer>
      <ElButton v-if="isEditingEvent" type="danger" @click="deleteEvent">删除事项</ElButton>
      <ElButton @click="eventFormDialogVisible = false">取消</ElButton>
      <ElButton type="primary" @click="saveEvent">保存</ElButton>
    </template>
  </ElDialog>
</template>

<script setup lang="ts">
  import { computed, reactive, ref, watch } from 'vue'
  import { ElMessage } from 'element-plus'
  import { useUserStore } from '@/store/modules/user'

  interface CalendarEvent {
    id: number
    title: string
    date: string
    time: string
    complate: boolean
  }

  interface CalendarEventForm {
    title: string
    date: string
    time: string
  }

  const calendarDialogVisible = ref(false)
  const dayEventsDialogVisible = ref(false)
  const eventFormDialogVisible = ref(false)
  const calendarCurrentDate = ref(new Date())
  const selectedDay = ref('')
  const editingEventId = ref<number | null>(null)
  const userStore = useUserStore()
  const currentUserId = computed(() => userStore.getUserInfo.userId || 'guest')

  const getStorageKey = () => `seabot_calendar_events_${String(currentUserId.value)}`

  const loadEvents = (): CalendarEvent[] => {
    try {
      return JSON.parse(localStorage.getItem(getStorageKey()) || '[]')
    } catch {
      return []
    }
  }
  const replaceCalendarEvents = (events: CalendarEvent[]) => {
    calendarEvents.splice(0, calendarEvents.length, ...events)
  }

  const storedEvents = loadEvents()
  const eventIdSeed = ref(storedEvents.length > 0 ? Math.max(...storedEvents.map((e) => e.id)) + 1 : 1)

  const isEditingEvent = computed(() => editingEventId.value !== null)

  const calendarEvents = reactive<CalendarEvent[]>(storedEvents)

  watch(calendarEvents, (val) => {
    localStorage.setItem(getStorageKey(), JSON.stringify(val))
  }, { deep: true })

  watch(currentUserId, () => {
    const nextEvents = loadEvents()
    replaceCalendarEvents(nextEvents)
    eventIdSeed.value = nextEvents.length > 0 ? Math.max(...nextEvents.map((e) => e.id)) + 1 : 1
    editingEventId.value = null
    eventFormDialogVisible.value = false
    dayEventsDialogVisible.value = false
  })

  const pendingCount = computed(() => calendarEvents.filter((e) => !e.complate).length)

  const eventForm = reactive<CalendarEventForm>({
    title: '',
    date: '',
    time: '09:00'
  })

  const selectedDayEvents = computed(() => {
    return calendarEvents.filter((item) => item.date === selectedDay.value)
  })

  const getEventsByDate = (date: string) => {
    return calendarEvents.filter((item) => item.date === date)
  }

  const openCalendarDialog = () => {
    calendarDialogVisible.value = true
  }

  const openDayEvents = (date: string) => {
    selectedDay.value = date
    dayEventsDialogVisible.value = true
  }

  const formatDateKey = (date: Date) => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }

  const openCreateEventDialog = () => {
    const now = calendarCurrentDate.value
    editingEventId.value = null
    eventForm.title = ''
    eventForm.date = selectedDay.value || formatDateKey(now)
    eventForm.time = '09:00'
    eventFormDialogVisible.value = true
  }

  const openEditEventDialog = (event: CalendarEvent) => {
    editingEventId.value = event.id
    eventForm.title = event.title
    eventForm.date = event.date
    eventForm.time = event.time
    eventFormDialogVisible.value = true
  }

  const deleteEvent = () => {
    const index = calendarEvents.findIndex((item) => item.id === editingEventId.value)
    if (index >= 0) calendarEvents.splice(index, 1)
    ElMessage.success('事项已删除')
    eventFormDialogVisible.value = false
    editingEventId.value = null
  }

  const saveEvent = () => {
    if (!eventForm.title.trim() || !eventForm.date) {
      ElMessage.warning('请填写标题和日期')
      return
    }

    if (editingEventId.value !== null) {
      const index = calendarEvents.findIndex((item) => item.id === editingEventId.value)
      if (index >= 0) {
        calendarEvents[index] = {
          ...calendarEvents[index],
          title: eventForm.title.trim(),
          date: eventForm.date,
          time: eventForm.time || '09:00'
        }
      }
      ElMessage.success('事项已更新')
    } else {
      calendarEvents.unshift({
        id: eventIdSeed.value++,
        title: eventForm.title.trim(),
        date: eventForm.date,
        time: eventForm.time || '09:00',
        complate: false
      })
      ElMessage.success('日程已添加')
    }

    eventFormDialogVisible.value = false
    editingEventId.value = null
  }


</script>
