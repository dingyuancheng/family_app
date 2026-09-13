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
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { login } from '@/api/auth'

const router = useRouter()
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const onSubmit = async () => {
  loading.value = true
  try {
    const res = await login({
      username: form.username,
      password: form.password
    })
    localStorage.setItem('session_id', res.session_id)
    localStorage.setItem('user_info', JSON.stringify(res.user))
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
  padding: 60px 20px;
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
</style>