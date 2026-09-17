import storage, { KEY } from '@/utils/storage'

export function setActiveDomain(domain) {
  storage.set(KEY.defaultDomain, domain)
}

export function getActiveDomain() {
  return storage.get(KEY.defaultDomain) || ''
}

export function hasActiveDomain() {
  return !!getActiveDomain()
}

export function clearActiveDomain() {
  storage.remove(KEY.defaultDomain)
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