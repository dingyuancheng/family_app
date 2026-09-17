<template>
  <div class="app-root">
    <router-view />

    <van-tabbar v-if="showTabbar" v-model="activeTab" route active-color="#1677ff" inactive-color="#969799">
      <van-tabbar-item icon="home-o" to="/home">首页</van-tabbar-item>
      <van-tabbar-item icon="user-o" to="/me">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { initStore } from '@/store'

const route = useRoute()
const activeTab = ref(0)

const showTabbar = ref(true)
watch(
  () => route.path,
  (path) => {
    showTabbar.value = !(path === '/login' || path === '/webview')
  },
  { immediate: true }
)

onMounted(() => {
  initStore()
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body,
#app {
  width: 100%;
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
    'Helvetica Neue', Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background-color: #f5f6f8;
  -webkit-tap-highlight-color: transparent;
}
</style>