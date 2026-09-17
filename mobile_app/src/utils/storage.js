const KEY = {
  customDomain: 'family_app_custom_domain',
  customBackupDomain: 'family_app_custom_backup_domain',
  defaultDomain: 'family_app_default_domain',
  backupDomain: 'family_app_backup_domain',
  sessionId: 'session_id',
  userInfo: 'user_info',
  theme: 'family_app_theme',
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