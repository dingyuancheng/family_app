const KEY = {
  defaultDomain: 'family_app_default_domain',
  sessionId: 'session_id',
  userInfo: 'user_info',
}

const storage = {
  set(key, value) {
    if (typeof value === 'object') {
      localStorage.setItem(key, JSON.stringify(value))
    } else {
      localStorage.setItem(key, value)
    }
  },
  get(key, defaultValue = null) {
    const raw = localStorage.getItem(key)
    if (raw === null || raw === undefined) return defaultValue
    try {
      return JSON.parse(raw)
    } catch {
      return raw
    }
  },
  remove(key) {
    localStorage.removeItem(key)
  },
  clear() {
    Object.values(KEY).forEach((k) => localStorage.removeItem(k))
  },
}

export { KEY }
export default storage