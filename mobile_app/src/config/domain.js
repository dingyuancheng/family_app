import storage, { KEY } from '@/utils/storage'

let domains = null

export function initDomains(serverConfig) {
  if (!serverConfig) return
  storage.set(KEY.defaultDomain, serverConfig.default_domain)
  storage.set(KEY.backupDomain, serverConfig.backup_domain)
}

export function getActiveDomain() {
  const custom = storage.get(KEY.customDomain)
  if (custom) return custom
  return storage.get(KEY.defaultDomain) || ''
}

export function getBackupDomain() {
  const custom = storage.get(KEY.customBackupDomain)
  if (custom) return custom
  return storage.get(KEY.backupDomain) || ''
}

export function setCustomDomain(domain) {
  storage.set(KEY.customDomain, domain)
}

export function setCustomBackupDomain(domain) {
  storage.set(KEY.customBackupDomain, domain)
}

export function clearCustomDomain() {
  storage.remove(KEY.customDomain)
  storage.remove(KEY.customBackupDomain)
}

export function buildMenuUrl(url, external) {
  if (!url) return 'about:blank'
  if (external === 1 || url.startsWith('http')) {
    return url
  }
  const base = getActiveDomain()
  if (!base) return url
  return base.replace(/\/$/, '') + url
}