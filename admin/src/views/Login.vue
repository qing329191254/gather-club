<template>
  <div class="login-page">
    <el-card class="card">
      <div class="brand-wrap">
        <img class="logo" :src="`${base}brand.png`" alt="天天聚" />
      </div>
      <h2>天天俱乐部后台</h2>
      <p class="tip">管理小程序内容、订单与库存</p>
      <el-form :model="form" @submit.prevent>
        <el-form-item label="账号">
          <el-input v-model="form.username" placeholder="请输入账号" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" show-password placeholder="请输入密码" @keyup.enter="onLogin" />
        </el-form-item>
        <el-button type="primary" style="width: 100%" :loading="loading" @click="onLogin">登录</el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import http from '../api/http'

const router = useRouter()
const base = import.meta.env.BASE_URL
const loading = ref(false)
const form = reactive({ username: '', password: '' })

async function onLogin() {
  if (loading.value) return
  loading.value = true
  try {
    const data = await http.post('/login', form)
    localStorage.setItem('gather_admin_token', data.access_token)
    localStorage.setItem('gather_admin_user', data.username)
    ElMessage.success('登录成功')
    router.push('/dashboard')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background:
    radial-gradient(ellipse 70% 55% at 12% 18%, rgba(185, 28, 28, 0.16), transparent 58%),
    radial-gradient(ellipse 65% 50% at 88% 82%, rgba(180, 83, 9, 0.12), transparent 55%),
    radial-gradient(ellipse 50% 40% at 70% 20%, rgba(148, 163, 184, 0.18), transparent 60%),
    linear-gradient(165deg, #f4f5f7 0%, #eef0f3 48%, #f2ebe6 100%);
}
.login-page::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image: radial-gradient(rgba(15, 23, 42, 0.04) 1px, transparent 1px);
  background-size: 22px 22px;
  pointer-events: none;
}
.card {
  position: relative;
  z-index: 1;
  width: 380px;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.7);
  box-shadow:
    0 1px 2px rgba(15, 23, 42, 0.04),
    0 18px 40px rgba(15, 23, 42, 0.08);
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(10px);
}
.brand-wrap {
  display: flex;
  justify-content: center;
  margin-bottom: 12px;
}
.logo {
  width: 96px;
  height: 96px;
  object-fit: contain;
}
h2 {
  margin: 0 0 4px;
  text-align: center;
  color: #0f172a;
}
.tip {
  margin: 0 0 20px;
  color: #64748b;
  text-align: center;
}
</style>
