<template>
  <el-container class="layout">
    <el-aside width="220px" class="aside">
      <div class="brand">天天俱乐部</div>
      <el-menu :default-active="route.path" router background-color="#111827" text-color="#cbd5e1" active-text-color="#fff">
        <el-menu-item v-for="item in menus" :key="item.path" :index="item.path">
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.title }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="title">{{ route.meta.title || '后台' }}</div>
        <div class="right">
          <span class="user">{{ username }}</span>
          <el-button link type="danger" @click="logout">退出</el-button>
        </div>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const username = computed(() => localStorage.getItem('gather_admin_user') || 'admin')

const menus = [
  { path: '/dashboard', title: '概览', icon: 'Odometer' },
  { path: '/banners', title: '首页轮播', icon: 'Picture' },
  { path: '/stores', title: '门店管理', icon: 'Shop' },
  { path: '/gather', title: '去哪聚', icon: 'Grid' },
  { path: '/nye', title: '年夜饭', icon: 'Food' },
  { path: '/mall', title: '积分商城', icon: 'Goods' },
  { path: '/recommend', title: '推荐位', icon: 'Star' },
  { path: '/content', title: '内容配置', icon: 'Document' },
  { path: '/orders', title: '订单管理', icon: 'List' },
  { path: '/rooms', title: '包房库存', icon: 'Calendar' },
  { path: '/coupons', title: '优惠券', icon: 'Ticket' },
  { path: '/users', title: '用户积分', icon: 'User' },
  { path: '/video', title: '视频号', icon: 'VideoCamera' },
  { path: '/settings', title: '站点配置', icon: 'Setting' }
]

function logout() {
  localStorage.removeItem('gather_admin_token')
  localStorage.removeItem('gather_admin_user')
  router.push('/login')
}
</script>

<style scoped>
.layout {
  height: 100vh;
}
.aside {
  background: #111827;
  color: #fff;
}
.brand {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  letter-spacing: 1px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
.header {
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #eef0f3;
}
.title {
  font-size: 18px;
  font-weight: 600;
}
.right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.user {
  color: #64748b;
}
.main {
  padding: 16px;
}
.el-menu {
  border-right: none;
}
</style>
