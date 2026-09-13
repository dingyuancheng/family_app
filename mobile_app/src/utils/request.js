import axios from 'axios'
import { showToast } from 'vant'

const getBaseURL = () => {
  if (window.Capacitor) {
    return 'http://192.168.0.6:8000'
  }
  return ''
}

const request = axios.create({
  baseURL: getBaseURL(),
  timeout: 10000
})

request.interceptors.request.use((config) => {
  const sessionId = localStorage.getItem('session_id')
  if (sessionId) {
    config.headers['X-Session-Id'] = sessionId
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
      code: error.code
    })

    if (error.code === 'ERR_NETWORK' || !error.response) {
      showToast('网络无法连接到服务器，请检查地址或网络')
    } else if (status === 401 && !error.config?.url?.includes('/login')) {
      localStorage.removeItem('session_id')
      localStorage.removeItem('user_info')
      showToast('登录已过期，请重新登录')
      window.location.hash = '#/login'
    } else if (detail) {
      showToast(detail)
    } else {
      showToast(`请求失败 (${status || '无响应'})`)
    }

    return Promise.reject(error)
  }
)

export default request