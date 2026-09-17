import storage, { KEY } from '@/utils/storage'
import { reactive } from 'vue'

export const store = reactive({
  user: null,
  sessionId: '',
  menus: [],
  categories: [],
  frequentMenus: [],
  serverConfig: null,
})

export function initStore() {
  store.sessionId = storage.get(KEY.sessionId, '') || ''
  const userInfo = storage.get(KEY.userInfo)
  if (userInfo) {
    store.user = userInfo
  }
}

export function setAuth(sessionId, user) {
  store.sessionId = sessionId
  store.user = user
  storage.set(KEY.sessionId, sessionId)
  storage.set(KEY.userInfo, user)
}

export function clearAuth() {
  store.sessionId = ''
  store.user = null
  storage.remove(KEY.sessionId)
  storage.remove(KEY.userInfo)
}

export function setMenuData(data) {
  store.menus = data.menus || []
  store.categories = data.categories || []
  store.frequentMenus = data.frequent_menus || []
}

export function isLoggedIn() {
  return !!store.sessionId
}