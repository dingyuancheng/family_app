<template>
  <div class="home-page">
    <van-nav-bar title="首页" />

    <div class="content">
      <van-cell-group inset>
        <van-cell title="欢迎回来" :value="username" />
        <van-cell title="今天是" :value="currentDate" />
      </van-cell-group>

      <div class="welcome">
        <h2>欢迎使用家庭管理系统</h2>
        <p>这里是您的个人中心，您可以管理家庭成员、查看家庭日程等。</p>
      </div>

      <div class="action-wrapper">
        <van-button round block type="danger" @click="onLogout">
          退出登录
        </van-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showConfirmDialog, showToast } from 'vant'

const router = useRouter()
const username = ref('')
const currentDate = ref('')

const onLogout = async () => {
  try {
    await showConfirmDialog({
      title: '提示',
      message: '确定要退出登录吗？'
    })
    localStorage.removeItem('session_id')
    localStorage.removeItem('user_info')
    showToast('已退出登录')
    router.push('/login')
  } catch {
  }
}

onMounted(() => {
  const userInfo = localStorage.getItem('user_info')
  if (userInfo) {
    try {
      username.value = JSON.parse(userInfo).username || '用户'
    } catch {
      username.value = '用户'
    }
  }
  const now = new Date()
  currentDate.value = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
})
</script>

<style scoped>
.home-page {
  min-height: 100vh;
}

.content {
  padding: 20px 16px;
}

.welcome {
  margin-top: 32px;
  text-align: center;
  padding: 0 16px;
}

.welcome h2 {
  font-size: 22px;
  color: #323233;
  margin-bottom: 12px;
}

.welcome p {
  font-size: 14px;
  color: #969799;
  line-height: 1.6;
}

.action-wrapper {
  margin-top: 48px;
}
</style>