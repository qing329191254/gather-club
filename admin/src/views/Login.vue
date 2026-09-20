<template>
  <div class="login-page">
    <el-card class="card">
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
const loading = ref(false)
const form = reactive({ username: '', password: '' })

async function onLogin() {
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
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1f2937, #7f1d1d 55%, #b45309);
}
.card {
  width: 380px;
  border-radius: 16px;
}
h2 {
  margin: 0 0 4px;
}
.tip {
  margin: 0 0 20px;
  color: #64748b;
}
</style>
