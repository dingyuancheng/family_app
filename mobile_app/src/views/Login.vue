<template>
  <div class="login-page">
    <div class="login-header">
      <h1>家庭管理</h1>
      <p>欢迎登录</p>
    </div>

    <van-form @submit="onSubmit">
      <van-cell-group inset>
        <van-field
          v-model="form.username"
          name="username"
          label="用户名"
          placeholder="请输入用户名"
          :rules="[{ required: true, message: '请填写用户名' }]"
        />
        <van-field
          v-model="form.password"
          type="password"
          name="password"
          label="密码"
          placeholder="请输入密码"
          :rules="[{ required: true, message: '请填写密码' }]"
        />
      </van-cell-group>
      <div class="submit-wrapper">
        <van-button round block type="primary" native-type="submit" :loading="loading">
          登录
        </van-button>
      </div>
    </van-form>

    <div class="domain-btn" @click="showDomainDialog = true">
      <span>当前域名：{{ displayDomain }}</span>
      <van-icon name="arrow" />
    </div>

    <van-dialog v-model:show="showDomainDialog" title="域名配置" show-cancel-button>
      <div class="domain-form">
        <van-field
          v-model="domainForm.custom"
          label="自定义主域名"
          placeholder="例如 https://family.example.com"
        />
        <van-field
          v-model="domainForm.backup"
          label="备用域名"
          placeholder="选填，主域名不可用时使用"
        />
      </div>
      <template #footer>
        <van-button @click="showDomainDialog = false">取消</van-button>
        <van-button type="primary" @click="saveDomain">保存</van-button>
        <van-button @click="resetDomain">恢复默认</van-button>
      </template>
    </van-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { login, getServerConfig } from '@/api/auth'
import { store, setAuth } from '@/store'
import { initDomains, getActiveDomain, setCustomDomain, setCustomBackupDomain, clearCustomDomain } from '@/config/domain'

const router = useRouter()
const loading = ref(false)
const showDomainDialog = ref(false)

const form = reactive({ username: '', password: '' })
const domainForm = reactive({ custom: '', backup: '' })

const displayDomain = computed(() => {
  const d = getActiveDomain()
  return d || '(未配置，点击设置)'
})

const onSubmit = async () => {
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

const saveDomain = () => {
  if (domainForm.custom) setCustomDomain(domainForm.custom)
  if (domainForm.backup) setCustomBackupDomain(domainForm.backup)
  showToast('域名已保存')
  showDomainDialog.value = false
}

const resetDomain = async () => {
  clearCustomDomain()
  try {
    const cfg = await getServerConfig()
    if (cfg) initDomains(cfg)
  } catch { /* ignore */ }
  showToast('已恢复默认域名')
  showDomainDialog.value = false
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  padding: 60px 20px 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
  color: #fff;
}

.login-header h1 {
  font-size: 32px;
  margin-bottom: 8px;
}

.login-header p {
  font-size: 16px;
  opacity: 0.85;
}

.submit-wrapper {
  margin-top: 24px;
  padding: 0 16px;
}

.domain-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 32px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 13px;
  gap: 4px;
  cursor: pointer;
}

.domain-form {
  padding: 16px 0;
}
</style>