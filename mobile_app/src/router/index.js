import { createRouter, createWebHashHistory } from 'vue-router'
import { store } from '@/store'

const routes = [
  { path: '/', redirect: '/home' },
  { path: '/login', name: 'Login', component: () => import('@/views/Login.vue') },
  { path: '/home', name: 'Home', component: () => import('@/views/Home.vue'), meta: { requiresAuth: true, tab: 'home' } },
  { path: '/me', name: 'Me', component: () => import('@/views/Me.vue'), meta: { requiresAuth: true, tab: 'me' } },
  { path: '/webview', name: 'WebView', component: () => import('@/views/WebView.vue'), meta: { requiresAuth: true } },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const loggedIn = !!store.sessionId
  if (to.meta.requiresAuth && !loggedIn) {
    next('/login')
  } else if (to.path === '/login' && loggedIn) {
    next('/home')
  } else {
    next()
  }
})

export default router