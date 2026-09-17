import storage, { KEY } from '@/utils/storage'

export const THEMES = {
  LIGHT: 'light',
  DARK: 'dark',
  AUTO: 'auto',
}

function getAutoTheme() {
  const now = new Date()
  const h = now.getHours()
  return h >= 22 || h < 6 ? THEMES.DARK : THEMES.LIGHT
}

export function getTheme() {
  const saved = storage.get(KEY.theme, THEMES.AUTO)
  if (saved === THEMES.AUTO) return getAutoTheme()
  return saved
}

export function getRawTheme() {
  return storage.get(KEY.theme, THEMES.AUTO)
}

export function setTheme(mode) {
  storage.set(KEY.theme, mode)
  applyTheme()
}

export function applyTheme() {
  const effective = getTheme()
  if (effective === THEMES.DARK) {
    document.documentElement.classList.add('theme-dark')
  } else {
    document.documentElement.classList.remove('theme-dark')
  }
}

export function cycleTheme() {
  const current = getRawTheme()
  if (current === THEMES.LIGHT) {
    setTheme(THEMES.DARK)
  } else if (current === THEMES.DARK) {
    setTheme(THEMES.AUTO)
  } else {
    setTheme(THEMES.LIGHT)
  }
}