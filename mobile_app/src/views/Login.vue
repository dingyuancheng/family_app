<template>
  <div class="login-page">
    <div class="grid"></div>
    <div class="header">
      <h1>重生系统</h1>
      <div class="sub">
        欢迎回来
        <span class="dot-sep"></span>
        Reborn System
      </div>
    </div>

    <div class="container">
      <form @submit.prevent="onSubmit">
        <div class="form-item">
          <div class="input-wrap" :class="{ focused: focusedField === 'username' }">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
            <input
              v-model="form.username"
              type="text"
              placeholder="用户名"
              @focus="focusedField = 'username'"
              @blur="focusedField = ''"
            />
          </div>
        </div>

        <div class="form-item">
          <div class="input-wrap" :class="{ focused: focusedField === 'password' }">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="11" width="18" height="11" rx="2"/>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
            </svg>
            <input
              v-model="form.password"
              type="password"
              placeholder="密码"
              @focus="focusedField = 'password'"
              @blur="focusedField = ''"
            />
          </div>
        </div>

        <button type="submit" class="btn-login" :disabled="loading">
          {{ loading ? '登录中...' : '登 录' }}
        </button>
      </form>

      <div class="divider">
        <div class="line"></div>
        <span class="txt">settings</span>
        <div class="line"></div>
      </div>

      <button type="button" class="btn-domain" @click="openDomainDialog">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="3"/>
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.6 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.6a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
        </svg>
        设置域名
        <span v-if="displayDomain" class="domain-hint">{{ displayDomain }}</span>
      </button>
    </div>

    <div class="footer">REBORN · SYSTEM</div>

    <Teleport to="body">
      <div v-if="showDomainDialog" class="dlg-mask" @click.self="showDomainDialog = false">
        <div class="dlg-card">
          <div class="dlg-header">
            <div class="dlg-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
                <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
              </svg>
            </div>
            <div class="dlg-title">服务域名配置</div>
            <div class="dlg-sub">首次使用请配置后端服务地址</div>
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
            <div class="dlg-tip">配置后 App 将通过此地址连接后端服务</div>
          </div>

          <div class="dlg-footer">
            <button type="button" class="dlg-btn dlg-btn-cancel" @click="showDomainDialog = false">取消</button>
            <button type="button" class="dlg-btn dlg-btn-confirm" @click="saveDomain">保存</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { login } from '@/api/auth'
import { setAuth } from '@/store'
import { getActiveDomain, hasActiveDomain, setActiveDomain } from '@/config/domain'

const router = useRouter()
const loading = ref(false)
const showDomainDialog = ref(false)
const focusedField = ref('')

const form = reactive({ username: '', password: '' })
const domainForm = reactive({ domain: 'http://192.168.0.6:8000' })

const displayDomain = computed(() => {
  const d = getActiveDomain()
  if (!d) return ''
  if (d.length > 20) return d.slice(0, 17) + '...'
  return d
})

onMounted(() => {
  if (!hasActiveDomain()) {
    showDomainDialog.value = true
  }
})

const openDomainDialog = () => {
  domainForm.domain = getActiveDomain() || 'http://192.168.0.6:8000'
  showDomainDialog.value = true
}

const saveDomain = () => {
  if (!domainForm.domain.trim()) {
    showToast('请输入服务域名')
    return
  }
  setActiveDomain(domainForm.domain.trim())
  showToast('域名已保存')
  showDomainDialog.value = false
}

const onSubmit = async () => {
  if (!form.username.trim()) {
    showToast('请输入用户名')
    return
  }
  if (!form.password) {
    showToast('请输入密码')
    return
  }
  if (!hasActiveDomain()) {
    showToast('请先配置服务域名')
    showDomainDialog.value = true
    return
  }
  loading.value = true
  try {
    const res = await login({ username: form.username, password: form.password })
    setAuth(res.session_id, res.user)
    showToast('登录成功')
    router.push('/home')
  } catch (err) {
    console.error('登录失败:', err)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f5f4;
  color: #1c1c1e;
  position: relative;
  overflow: hidden;
  -webkit-font-smoothing: antialiased;
}

.grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(0, 0, 0, 0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 0, 0, 0.04) 1px, transparent 1px);
  background-size: 32px 32px;
  mask-image: radial-gradient(ellipse at center, black 30%, transparent 75%);
  -webkit-mask-image: radial-gradient(ellipse at center, black 30%, transparent 75%);
  z-index: 0;
}

.header {
  position: relative;
  z-index: 2;
  padding: 72px 32px 40px;
}

.header h1 {
  font-size: 28px;
  font-weight: 600;
  letter-spacing: -0.5px;
  color: #1c1c1e;
  margin-bottom: 6px;
}

.header .sub {
  font-size: 13px;
  color: #8a8a8e;
  font-weight: 400;
}

.header .sub .dot-sep {
  display: inline-block;
  width: 3px;
  height: 3px;
  background: #0ea5e9;
  border-radius: 50%;
  margin: 0 8px;
  vertical-align: middle;
}

.container {
  position: relative;
  z-index: 2;
  flex: 1;
  padding: 0 32px;
}

.form-item {
  margin-bottom: 14px;
}

.input-wrap {
  display: flex;
  align-items: center;
  height: 52px;
  padding: 0 16px;
  background: #ffffff;
  border: 1px solid #e7e5e4;
  border-radius: 12px;
  transition: all 0.2s ease;
  position: relative;
}
.input-wrap::before {
  content: "";
  position: absolute;
  left: 0;
  top: 12px;
  bottom: 12px;
  width: 2px;
  background: transparent;
  border-radius: 2px;
  transition: background 0.2s ease;
}
.input-wrap.focused {
  border-color: #0ea5e9;
  box-shadow: 0 0 0 4px rgba(14, 165, 233, 0.1);
}
.input-wrap.focused::before {
  background: #0ea5e9;
}

.input-wrap .icon {
  width: 16px;
  height: 16px;
  margin-right: 12px;
  color: #a8a29e;
  flex-shrink: 0;
  transition: color 0.2s;
}
.input-wrap.focused .icon {
  color: #0ea5e9;
}

.input-wrap input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 14px;
  font-weight: 500;
  color: #1c1c1e;
  height: 100%;
  letter-spacing: 0.3px;
}
.input-wrap input::placeholder {
  color: #b8b5b0;
  font-weight: 400;
}

.btn-login {
  width: 100%;
  height: 52px;
  margin-top: 20px;
  background: #0ea5e9;
  color: #ffffff;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
}
.btn-login:active {
  transform: scale(0.99);
  background: #0284c7;
}
.btn-login:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.divider {
  display: flex;
  align-items: center;
  margin: 28px 0 20px;
  gap: 12px;
}
.divider .line {
  flex: 1;
  height: 1px;
  background: #e7e5e4;
}
.divider .txt {
  font-size: 11px;
  color: #b8b5b0;
  letter-spacing: 2px;
  text-transform: uppercase;
}

.btn-domain {
  width: 100%;
  height: 44px;
  background: #ffffff;
  border: 1px solid #e7e5e4;
  border-radius: 12px;
  color: #78716c;
  font-size: 13px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s ease;
}
.btn-domain svg {
  width: 14px;
  height: 14px;
}
.btn-domain:active {
  border-color: #0ea5e9;
  color: #0ea5e9;
  background: #f0f9ff;
}

.domain-hint {
  font-size: 11px;
  opacity: 0.6;
}

.footer {
  position: relative;
  z-index: 2;
  text-align: center;
  padding: 24px 32px 32px;
  color: #d6d3d1;
  font-size: 11px;
  letter-spacing: 3px;
  text-transform: uppercase;
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

.dlg-tip {
  font-size: 11px;
  color: #b8b5b0;
  margin-top: 10px;
  padding: 0 2px;
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