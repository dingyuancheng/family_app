import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue')
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const sessionId = localStorage.getItem('session_id')
  if (to.meta.requiresAuth && !sessionId) {
    next('/login')
  } else if (to.path === '/login' && sessionId) {
    next('/home')
  } else {
    next()
  }
})

export default router