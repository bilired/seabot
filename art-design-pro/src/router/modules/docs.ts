import { AppRouteRecord } from '@/types/router'

export const docsRoutes: AppRouteRecord[] = [
  {
    name: 'DocsIndex',
    path: '/docs',
    component: '/docs/index',
    meta: {
      title: 'docs.title',
      icon: 'ri:book-2-line',
      keepAlive: false,
      requiresAuth: false
    }
  }
]
