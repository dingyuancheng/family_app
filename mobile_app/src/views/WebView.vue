<template>
  <div class="webview-page">
    <van-nav-bar
      :title="menuName"
      left-icon="arrow-left"
      @click-left="goBack"
      right-icon="replay"
      @click-right-icon="refresh"
    />
    <div class="iframe-wrap">
      <iframe
        v-if="fullUrl"
        ref="iframeRef"
        :src="fullUrl"
        frameborder="0"
        allowfullscreen
        allow="camera; microphone; geolocation"
        class="webframe"
      />
      <div v-else class="loading-placeholder">加载中...</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const iframeRef = ref(null)

const menuName = computed(() => route.query.name || '功能')
const fullUrl = computed(() => route.query.url || '')

const goBack = () => {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.replace('/home')
  }
}

const refresh = () => {
  if (iframeRef.value) {
    iframeRef.value.src = iframeRef.value.src
  }
}
</script>

<style scoped>
.webview-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.iframe-wrap {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.webframe {
  width: 100%;
  height: 100%;
  border: 0;
}

.loading-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #969799;
}
</style>