<template>
  <div class="home-page">
    <div class="hero">
      <div class="hero-top">
        <div class="greet">
          <div class="greet-hi">{{ greeting }}，{{ nickname }}</div>
          <div class="greet-sub">{{ dateText }}</div>
        </div>
        <div class="hero-actions">
          <van-icon name="setting-o" size="22" @click="goMe" />
        </div>
      </div>

      <div class="search-wrap">
        <van-search
          v-model="searchKeyword"
          placeholder="搜索功能"
          shape="round"
          background="transparent"
        />
      </div>
    </div>

    <div class="body">
      <div v-if="frequentMenus.length" class="panel frequent-panel">
        <div class="panel-title">
          <span class="title-dot"></span>
          常用功能
        </div>
        <div class="frequent-scroll">
          <div
            v-for="menu in frequentMenus"
            :key="menu.id"
            class="frequent-item"
            @click="openMenu(menu)"
          >
            <div class="frequent-icon">
              <span class="icon-emoji">{{ menu.icon || '📦' }}</span>
            </div>
            <div class="frequent-name">{{ menu.name }}</div>
          </div>
        </div>
      </div>

      <div class="panel">
        <van-tabs
          v-model:active="activeCategory"
          swipeable
          scrollspy
          animated
          line-width="24px"
          line-height="3px"
          color="#1677ff"
          inactive-color="#8a8f99"
          @change="onCategoryChange"
        >
          <van-tab v-for="cat in categories" :key="cat.id" :title="cat.name">
            <div class="menu-grid">
              <template v-if="!searchKeyword">
                <div
                  v-for="menu in getMenusByCategory(cat.id)"
                  :key="menu.id"
                  class="menu-item"
                  @click="openMenu(menu)"
                >
                  <div class="menu-icon-wrap" :class="getIconBgClass(menu)">
                    <span class="icon-emoji">{{ menu.icon || '📦' }}</span>
                    <span v-if="menu.external === 1" class="external-tag">外链</span>
                  </div>
                  <div class="menu-name">{{ menu.name }}</div>
                </div>
              </template>
              <template v-else>
                <div
                  v-for="menu in getFilteredMenus(cat.id)"
                  :key="menu.id"
                  class="menu-item"
                  @click="openMenu(menu)"
                >
                  <div class="menu-icon-wrap" :class="getIconBgClass(menu)">
                    <span class="icon-emoji">{{ menu.icon || '📦' }}</span>
                    <span v-if="menu.external === 1" class="external-tag">外链</span>
                  </div>
                  <div class="menu-name">{{ menu.name }}</div>
                </div>
                <van-empty
                  v-if="getFilteredMenus(cat.id).length === 0 && cat === categories[activeCategory]"
                  description="未找到匹配的功能"
                />
              </template>
            </div>
          </van-tab>
        </van-tabs>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { store, setMenuData } from '@/store'
import { getMyMenus, recordMenuClick } from '@/api/user'
import { buildMenuUrl } from '@/config/domain'
import storage, { KEY } from '@/utils/storage'

const ICON_BGS = [
  'bg-blue', 'bg-orange', 'bg-green', 'bg-purple',
  'bg-pink', 'bg-teal', 'bg-amber', 'bg-indigo',
]

const router = useRouter()
const activeCategory = ref(0)
const searchKeyword = ref('')

const nickname = computed(() => store.user?.nickname || store.user?.username || '用户')
const categories = computed(() => store.categories || [])
const menus = computed(() => store.menus || [])
const frequentMenus = computed(() => store.frequentMenus || [])

const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 6) return '夜深了'
  if (h < 12) return '早上好'
  if (h < 14) return '中午好'
  if (h < 18) return '下午好'
  return '晚上好'
})

const dateText = computed(() => {
  const d = new Date()
  const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
  return `${d.getMonth() + 1}月${d.getDate()}日 ${weekdays[d.getDay()]}`
})

const goMe = () => router.push('/me')

const getIconBgClass = (menu) => {
  const idx = Math.abs(hashStr(menu.name)) % ICON_BGS.length
  return ICON_BGS[idx]
}

function hashStr(s) {
  let h = 0
  for (let i = 0; i < s.length; i++) {
    h = ((h << 5) - h) + s.charCodeAt(i)
    h |= 0
  }
  return h
}

const getMenusByCategory = (catId) => {
  return menus.value.filter((m) => String(m.category_id) === String(catId))
}

const getFilteredMenus = (catId) => {
  const kw = searchKeyword.value.trim().toLowerCase()
  return getMenusByCategory(catId).filter((m) => m.name.toLowerCase().includes(kw))
}

const isAppEnv = () => !!(window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.Browser)

const appendSessionToUrl = (url) => {
  const sid = storage.get(KEY.sessionId) || ''
  if (!sid) return url
  const sep = url.includes('?') ? '&' : '?'
  return `${url}${sep}_sid=${encodeURIComponent(sid)}`
}

const openMenu = async (menu) => {
  try {
    await recordMenuClick(menu.id)
  } catch { /* ignore */ }

  const baseUrl = buildMenuUrl(menu.url, menu.external)
  const fullUrl = menu.external === 0 ? appendSessionToUrl(baseUrl) : baseUrl

  if (isAppEnv()) {
    try {
      await window.Capacitor.Plugins.Browser.open({
        url: fullUrl,
        presentationStyle: 'fullscreen',
        toolbarColor: '#1677ff',
      })
    } catch (e) {
      console.error('Capacitor Browser 打开失败', e)
      router.push({ name: 'WebView', query: { url: fullUrl, name: menu.name, external: menu.external } })
    }
  } else {
    router.push({
      name: 'WebView',
      query: {
        url: fullUrl,
        name: menu.name,
        external: menu.external,
      },
    })
  }
}

const onCategoryChange = () => { /* swipe handled automatically */ }

const loadMenus = async () => {
  try {
    const res = await getMyMenus()
    setMenuData(res)
  } catch (e) {
    console.error('加载菜单失败', e)
  }
}

onMounted(async () => {
  await loadMenus()
})
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  padding-bottom: 80px;
  background: #f5f6f8;
}

.hero {
  padding: 52px 20px 24px;
  background: linear-gradient(135deg, #1677ff 0%, #4096ff 50%, #69b1ff 100%);
  color: #fff;
  border-radius: 0 0 28px 28px;
  position: relative;
}

.hero-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.greet-hi {
  font-size: 20px;
  font-weight: 600;
  line-height: 1.3;
}

.greet-sub {
  font-size: 13px;
  opacity: 0.8;
  margin-top: 4px;
}

.hero-actions {
  padding-top: 4px;
  color: #fff;
}

.search-wrap {
  margin-top: 20px;
}

.search-wrap :deep(.van-search) {
  background: rgba(255, 255, 255, 0.22);
  border-radius: 20px;
  padding: 4px 14px;
}

.search-wrap :deep(.van-search__input-wrap) {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  height: 36px;
}

.search-wrap :deep(.van-search__input) {
  color: #323233;
  font-size: 14px;
}

.search-wrap :deep(.van-search__placeholder) {
  color: #a4a9b0;
}

.body {
  margin-top: -8px;
  padding: 0 14px;
  position: relative;
  z-index: 1;
}

.panel {
  background: #fff;
  border-radius: 16px;
  padding: 14px 10px 8px;
  margin-bottom: 14px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.panel-title {
  font-size: 15px;
  font-weight: 600;
  color: #1f2329;
  padding: 4px 6px 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-dot {
  width: 4px;
  height: 16px;
  border-radius: 2px;
  background: #1677ff;
}

.frequent-scroll {
  display: flex;
  overflow-x: auto;
  padding: 4px 4px 8px;
  gap: 6px;
  scrollbar-width: none;
}

.frequent-scroll::-webkit-scrollbar {
  display: none;
}

.frequent-item {
  flex-shrink: 0;
  width: 58px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.frequent-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: linear-gradient(135deg, #e8f3ff, #f0f7ff);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.frequent-name {
  font-size: 12px;
  color: #4e5969;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 58px;
  text-align: center;
}

.menu-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 6px 0;
  padding: 8px 2px 12px;
}

.menu-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 8px 2px;
}

.menu-icon-wrap {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  position: relative;
}

.icon-emoji {
  line-height: 1;
}

.external-tag {
  position: absolute;
  top: -4px;
  right: -6px;
  font-size: 9px;
  color: #fff;
  background: #ff7d00;
  padding: 1px 5px;
  border-radius: 8px;
  line-height: 1.3;
  font-weight: 500;
}

.bg-blue   { background: linear-gradient(135deg, #e6f4ff, #bae0ff); }
.bg-orange { background: linear-gradient(135deg, #fff7e6, #ffd591); }
.bg-green  { background: linear-gradient(135deg, #f6ffed, #d9f7be); }
.bg-purple { background: linear-gradient(135deg, #f9f0ff, #efdbff); }
.bg-pink   { background: linear-gradient(135deg, #fff0f6, #ffd6e7); }
.bg-teal   { background: linear-gradient(135deg, #e6fffb, #b5f5ec); }
.bg-amber  { background: linear-gradient(135deg, #fffbe6, #ffe58f); }
.bg-indigo { background: linear-gradient(135deg, #eef0ff, #d4d8ff); }

.menu-name {
  font-size: 12px;
  color: #4e5969;
  white-space: nowrap;
  max-width: 64px;
  overflow: hidden;
  text-overflow: ellipsis;
  text-align: center;
}

.panel :deep(.van-tabs) {
  background: transparent;
}

.panel :deep(.van-tabs__wrap) {
  padding: 0 4px;
}

.panel :deep(.van-tab) {
  font-size: 14px;
  color: #8a8f99;
  padding: 10px 14px;
}

.panel :deep(.van-tab--active) {
  font-weight: 600;
}
</style>