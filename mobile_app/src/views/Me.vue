<template>
  <div class="me-page">
    <van-nav-bar title="我的" />

    <div class="user-card">
      <div class="avatar">
        {{ (store.user?.nickname || store.user?.username || 'U').charAt(0).toUpperCase() }}
      </div>
      <div class="user-info">
        <div class="user-name">
          {{ store.user?.nickname || store.user?.username || '用户' }}
          <van-icon v-if="store.user?.admin_flag" name="manager-o" class="admin-badge" />
        </div>
        <div class="user-sub">{{ store.user?.username }}</div>
      </div>
    </div>

    <van-cell-group inset class="mt-16">
      <van-cell title="登录账号" :value="store.user?.username" />
      <van-cell title="昵称" :value="store.user?.nickname || '未设置'" />
      <van-cell title="手机号" :value="store.user?.phone || '未设置'" />
      <van-cell title="邮箱" :value="store.user?.email || '未设置'" />
    </van-cell-group>

    <van-cell-group inset class="mt-16">
      <van-cell title="域名设置" :value="displayDomainShort" is-link @click="openDomainDialog = true" />
      <van-cell title="版本信息" value="0.1.0" />
    </van-cell-group>

    <div class="logout-wrapper">
      <van-button round block type="danger" @click="onLogout">
        退出登录
      </van-button>
    </div>

    <van-dialog v-model:show="openDomainDialog" title="域名配置" show-cancel-button>
      <div class="domain-form">
        <van-field v-model="domainForm.domain" label="服务域名" placeholder="例如 https://family.example.com" />
      </div>
      <template #footer>
        <van-button @click="openDomainDialog = false">取消</van-button>
        <van-button type="primary" @click="saveDomain">保存</van-button>
      </template>
    </van-dialog>
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
const domainForm = reactive({ domain: '' })

const displayDomainShort = computed(() => {
  const d = getActiveDomain()
  if (!d) return '未配置'
  if (d.length > 28) return d.slice(0, 25) + '...'
  return d
})

const onLogout = async () => {
  try {
    await showConfirmDialog({ title: '提示', message: '确定要退出登录吗？' })
    try { await logout() } catch { /* ignore */ }
    clearAuth()
    showToast('已退出登录')
    router.push('/login')
  } catch { /* cancel */ }
}

const saveDomain = () => {
  if (domainForm.domain.trim()) setActiveDomain(domainForm.domain.trim())
  showToast('域名已保存')
  openDomainDialog.value = false
}
</script>

<style scoped>
.me-page { min-height: 100vh; padding-bottom: 64px; }

.user-card {
  display: flex;
  align-items: center;
  padding: 24px 16px;
  gap: 16px;
}

.avatar {
  width: 64px; height: 64px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1677ff 0%, #69b1ff 100%);
  color: #fff;
  font-size: 28px;
  font-weight: bold;
  display: flex; align-items: center; justify-content: center;
}

.user-info { flex: 1; }
.user-name { font-size: 18px; font-weight: 600; color: #323233; display: flex; align-items: center; gap: 4px; }
.user-sub { font-size: 13px; color: #969799; margin-top: 4px; }
.admin-badge { color: #ff976a; font-size: 16px; }

.mt-16 { margin-top: 16px; }

.logout-wrapper { padding: 24px 16px; }

.domain-form { padding: 16px 0; }
</style>