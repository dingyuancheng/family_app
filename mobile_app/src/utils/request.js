import axios from 'axios'
import { showToast } from 'vant'
import storage, { KEY } from '@/utils/storage'
import { getActiveDomain } from '@/config/domain'
import { store } from '@/store'

const isInternalUrl = (url) => {
  if (!url) return false
  return !url.startsWith('http://') && !url.startsWith('https://')
}

const getEffectiveBaseURL = () => {
  if (window.Capacitor) {
    const domain = getActiveDomain()
    if (domain) return domain
    return 'http://localhost:8000'
  }
  return ''
}

const request = axios.create({
  timeout: 15000,
})

request.interceptors.request.use((config) => {
  const sessionId = store.sessionId || storage.get(KEY.sessionId)
  if (sessionId) {
    config.headers['X-Session-Id'] = sessionId
  }

  if (isInternalUrl(config.url)) {
    config.baseURL = getEffectiveBaseURL()
  }

  return config
})

request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const status = error.response?.status
    const detail = error.response?.data?.detail
    const msg = error.message || ''

    console.error('[Request Error]', {
      url: error.config?.url,
      status,
      detail,
      msg,
      code: error.code,
    })

    if (error.code === 'ERR_NETWORK' || !error.response) {
      showToast('网络无法连接到服务器，请检查域名或网络')
    } else if (status === 401 && !error.config?.url?.includes('/login')) {
      store.sessionId = ''
      store.user = null
      storage.remove(KEY.sessionId)
      storage.remove(KEY.userInfo)
      showToast('登录已过期，请重新登录')
      if (window.Capacitor) {
        window.location.hash = '#/login'
      } else {
        window.location.hash = '#/login'
      }
    } else if (detail) {
      showToast(detail)
    } else {
      showToast(`请求失败 (${status || '无响应'})`)
    }

    return Promise.reject(error)
  }
)

export default request