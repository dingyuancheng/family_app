<template>
  <div class="me-page">
    <div class="grid-bg"></div>

    <div class="hero">
      <div class="hero-title">我的</div>
    </div>

    <div class="body">
      <div class="user-card">
        <div class="avatar">
          {{ (store.user?.nickname || store.user?.username || 'U').charAt(0).toUpperCase() }}
        </div>
        <div class="user-info">
          <div class="user-name">
            {{ store.user?.nickname || store.user?.username || '用户' }}
            <span v-if="store.user?.admin_flag" class="admin-badge">管理员</span>
          </div>
          <div class="user-sub">{{ store.user?.username }}</div>
        </div>
      </div>

      <div class="card">
        <div class="card-row">
          <span class="row-label">登录账号</span>
          <span class="row-value">{{ store.user?.username }}</span>
        </div>
        <div class="card-row">
          <span class="row-label">昵称</span>
          <span class="row-value">{{ store.user?.nickname || '未设置' }}</span>
        </div>
        <div class="card-row">
          <span class="row-label">手机号</span>
          <span class="row-value">{{ store.user?.phone || '未设置' }}</span>
        </div>
        <div class="card-row card-row-last">
          <span class="row-label">邮箱</span>
          <span class="row-value">{{ store.user?.email || '未设置' }}</span>
        </div>
      </div>

      <div class="card">
        <div class="card-row card-row-clickable" @click="openDomainDialog = true">
          <span class="row-label">域名设置</span>
          <div class="row-value-wrap">
            <span class="row-value row-value-trunc">{{ displayDomainShort }}</span>
            <svg class="row-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="9 18 15 12 9 6"/>
            </svg>
          </div>
        </div>
        <div class="card-row card-row-last">
          <span class="row-label">版本信息</span>
          <span class="row-value">0.1.0</span>
        </div>
      </div>

      <button type="button" class="btn-logout" @click="onLogout">
        退出登录
      </button>
    </div>

    <Teleport to="body">
      <div v-if="openDomainDialog" class="dlg-mask" @click.self="openDomainDialog = false">
        <div class="dlg-card">
          <div class="dlg-header">
            <div class="dlg-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
                <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
              </svg>
            </div>
            <div class="dlg-title">域名配置</div>
            <div class="dlg-sub">设置后端服务地址</div>
          </div>

          <div class="dlg-body">
            <div class="dlg-input-wrap" :class="{ focused: focusedField === 'domain' }">
              <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="2" y="3" width="20" height="14" rx="2"/>
                <line x1="8" y1="21" x2="16" y2="21"/>
                <line x1="12" y1="17" x2="12" y2="21"/>
              </svg>
              <input
                v-model="domainForm.domain"
                type="text"
                placeholder="例如 http://192.168.0.6:8000"
                @focus="focusedField = 'domain'"
                @blur="focusedField = ''"
              />
            </div>
          </div>

          <div class="dlg-footer">
            <button type="button" class="dlg-btn dlg-btn-cancel" @click="openDomainDialog = false">取消</button>
            <button type="button" class="dlg-btn dlg-btn-confirm" @click="saveDomain">保存</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { showConfirmDialog, showToast } from 'vant'
import { store, clearAuth } from '@/store'
import { logout } from '@/api/auth'
import { getActiveDomain, setActiveDomain } from '@/config/domain'

const router = useRouter()
const openDomainDialog = ref(false)
const focusedField = ref('')
const domainForm = reactive({ domain: getActiveDomain() || 'http://192.168.0.6:8000' })

const displayDomainShort = computed(() => {
  const d = getActiveDomain()
  if (!d) return '未配置'
  if (d.length > 22) return d.slice(0, 19) + '...'
  return d
})

const openDialog = () => {
  domainForm.domain = getActiveDomain() || 'http://192.168.0.6:8000'
  openDomainDialog.value = true
}

const saveDomain = () => {
  if (!domainForm.domain.trim()) {
    showToast('请输入服务域名')
    return
  }
  setActiveDomain(domainForm.domain.trim())
  showToast('域名已保存')
  openDomainDialog.value = false
}

const onLogout = async () => {
  try {
    await showConfirmDialog({ title: '提示', message: '确定要退出登录吗？' })
    try { await logout() } catch { /* ignore */ }
    clearAuth()
    showToast('已退出登录')
    router.push('/login')
  } catch { /* cancel */ }
}
</script>

<style scoped>
.me-page {
  min-height: 100vh;
  padding-bottom: 96px;
  background: #f5f5f4;
  position: relative;
}

.grid-bg {
  position: fixed;
  inset: 0;
  background-image:
    linear-gradient(rgba(0, 0, 0, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 0, 0, 0.03) 1px, transparent 1px);
  background-size: 28px 28px;
  mask-image: radial-gradient(ellipse at top, black 20%, transparent 70%);
  -webkit-mask-image: radial-gradient(ellipse at top, black 20%, transparent 70%);
  pointer-events: none;
  z-index: 0;
}

.hero {
  position: relative;
  z-index: 2;
  padding: 56px 28px 16px;
}

.hero-title {
  font-size: 28px;
  font-weight: 600;
  letter-spacing: -0.5px;
  color: #1c1c1e;
}

.body {
  position: relative;
  z-index: 2;
  padding: 0 20px;
}

.user-card {
  display: flex;
  align-items: center;
  padding: 20px;
  background: #ffffff;
  border: 1px solid #e7e5e4;
  border-radius: 16px;
  gap: 16px;
  margin-bottom: 14px;
}

.avatar {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: #f0f9ff;
  color: #0ea5e9;
  font-size: 22px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.user-info {
  flex: 1;
  min-width: 0;
}

.user-name {
  font-size: 16px;
  font-weight: 600;
  color: #1c1c1e;
  display: flex;
  align-items: center;
  gap: 8px;
}

.admin-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  font-size: 10px;
  font-weight: 600;
  color: #0ea5e9;
  background: #e0f2fe;
  border-radius: 6px;
  letter-spacing: 0.5px;
}

.user-sub {
  font-size: 12px;
  color: #a8a29e;
  margin-top: 4px;
}

.card {
  background: #ffffff;
  border: 1px solid #e7e5e4;
  border-radius: 16px;
  margin-bottom: 14px;
  overflow: hidden;
}

.card-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #f5f5f4;
}
.card-row-last {
  border-bottom: none;
}

.card-row-clickable {
  cursor: pointer;
  transition: background 0.15s ease;
}
.card-row-clickable:active {
  background: #fafaf9;
}

.row-label {
  font-size: 13px;
  color: #1c1c1e;
  font-weight: 500;
}

.row-value {
  font-size: 13px;
  color: #a8a29e;
  max-width: 180px;
  text-align: right;
}

.row-value-wrap {
  display: flex;
  align-items: center;
  gap: 4px;
  max-width: 180px;
}

.row-value-trunc {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.row-arrow {
  width: 14px;
  height: 14px;
  color: #d6d3d1;
  flex-shrink: 0;
}

.btn-logout {
  width: 100%;
  height: 48px;
  margin-top: 24px;
  background: #ffffff;
  border: 1px solid #fee2e2;
  border-radius: 12px;
  color: #ef4444;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}
.btn-logout:active {
  background: #fef2f2;
  transform: scale(0.99);
}

.dlg-mask {
  position: fixed;
  inset: 0;
  background: rgba(28, 28, 30, 0.4);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 32px;
  animation: dlg-fade-in 0.18s ease;
}

@keyframes dlg-fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

.dlg-card {
  width: 100%;
  max-width: 360px;
  background: #ffffff;
  border-radius: 20px;
  overflow: hidden;
  box-shadow:
    0 24px 48px -12px rgba(0, 0, 0, 0.18),
    0 2px 8px rgba(0, 0, 0, 0.06);
  animation: dlg-slide-up 0.22s cubic-bezier(0.2, 0.8, 0.2, 1);
}

@keyframes dlg-slide-up {
  from { opacity: 0; transform: translateY(16px) scale(0.97); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.dlg-header {
  padding: 28px 24px 8px;
  text-align: center;
}

.dlg-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background: #f0f9ff;
  border-radius: 12px;
  margin-bottom: 14px;
}
.dlg-icon svg {
  width: 20px;
  height: 20px;
  color: #0ea5e9;
}

.dlg-title {
  font-size: 17px;
  font-weight: 600;
  color: #1c1c1e;
  margin-bottom: 4px;
  letter-spacing: -0.3px;
}

.dlg-sub {
  font-size: 12px;
  color: #a8a29e;
}

.dlg-body {
  padding: 20px 24px 8px;
}

.dlg-input-wrap {
  display: flex;
  align-items: center;
  height: 48px;
  padding: 0 14px;
  background: #fafaf9;
  border: 1px solid #e7e5e4;
  border-radius: 10px;
  transition: all 0.2s ease;
  position: relative;
}
.dlg-input-wrap::before {
  content: "";
  position: absolute;
  left: 0;
  top: 10px;
  bottom: 10px;
  width: 2px;
  background: transparent;
  border-radius: 2px;
  transition: background 0.2s ease;
}
.dlg-input-wrap.focused {
  background: #ffffff;
  border-color: #0ea5e9;
  box-shadow: 0 0 0 4px rgba(14, 165, 233, 0.1);
}
.dlg-input-wrap.focused::before {
  background: #0ea5e9;
}

.dlg-input-wrap .icon {
  width: 15px;
  height: 15px;
  margin-right: 10px;
  color: #a8a29e;
  flex-shrink: 0;
  transition: color 0.2s;
}
.dlg-input-wrap.focused .icon {
  color: #0ea5e9;
}

.dlg-input-wrap input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 13px;
  font-weight: 500;
  color: #1c1c1e;
  height: 100%;
  min-width: 0;
}
.dlg-input-wrap input::placeholder {
  color: #b8b5b0;
  font-weight: 400;
}

.dlg-footer {
  display: flex;
  gap: 10px;
  padding: 16px 24px 24px;
}

.dlg-btn {
  flex: 1;
  height: 44px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
  border: none;
}

.dlg-btn-cancel {
  background: #f5f5f4;
  color: #57534e;
}
.dlg-btn-cancel:active {
  background: #e7e5e4;
}

.dlg-btn-confirm {
  background: #0ea5e9;
  color: #ffffff;
}
.dlg-btn-confirm:active {
  background: #0284c7;
  transform: scale(0.99);
}
</style>