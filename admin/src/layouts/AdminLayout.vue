<template>
  <el-container class="layout">
    <el-aside width="220px" class="aside">
      <div class="brand">
        <img class="brand-logo" :src="`${base}brand.png`" alt="天天聚" />
        <div class="brand-text">
          <div class="brand-name">天天俱乐部</div>
          <div class="brand-sub">管理后台</div>
        </div>
      </div>
      <el-menu :default-active="route.path" router background-color="#111827" text-color="#cbd5e1" active-text-color="#fff">
        <el-menu-item v-for="item in menus" :key="item.path" :index="item.path">
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.title }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container class="body">
      <el-header class="header">
        <div class="title">{{ route.meta.title || '后台' }}</div>
        <div class="right">
          <span class="user">{{ username }}</span>
          <el-button link type="danger" @click="logout">退出</el-button>
        </div>
      </el-header>
      <el-main class="main">
        <router-view v-slot="{ Component }">
          <keep-alive>
            <component :is="Component" />
          </keep-alive>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const base = import.meta.env.BASE_URL
const username = computed(() => localStorage.getItem('gather_admin_user') || 'admin')

const menus = [
  { path: '/dashboard', title: '概览', icon: 'Odometer' },
  { path: '/banners', title: '首页轮播', icon: 'Picture' },
  { path: '/stores', title: '门店管理', icon: 'Shop' },
  { path: '/gather', title: '去哪聚', icon: 'Grid' },
  { path: '/nye', title: '宴会专题', icon: 'Food' },
  { path: '/mall', title: '积分商城', icon: 'Goods' },
  { path: '/recommend', title: '订酒店', icon: 'OfficeBuilding' },
  { path: '/content', title: '内容配置', icon: 'Document' },
  { path: '/orders', title: '订单管理', icon: 'List' },
  { path: '/verify', title: '到店核销', icon: 'CircleCheck' },
  { path: '/rooms', title: '包房库存', icon: 'Calendar' },
  { path: '/coupons', title: '优惠券', icon: 'Ticket' },
  { path: '/users', title: '用户', icon: 'User' },
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
  overflow: hidden;
}
.body {
  min-height: 0;
  overflow: hidden;
}
.aside {
  background: #111827;
  color: #fff;
  overflow: auto;
}
.brand {
  min-height: 72px;
  padding: 12px 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
.brand-logo {
  width: 44px;
  height: 44px;
  object-fit: contain;
  flex-shrink: 0;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.06);
}
.brand-text {
  min-width: 0;
}
.brand-name {
  font-weight: 700;
  font-size: 15px;
  letter-spacing: 0.5px;
  line-height: 1.2;
}
.brand-sub {
  margin-top: 2px;
  font-size: 12px;
  color: #94a3b8;
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
  min-height: 0;
  overflow: auto;
  display: flex;
  flex-direction: column;
}
.el-menu {
  border-right: none;
  padding: 8px 0;
}
.el-menu :deep(.el-menu-item) {
  margin: 2px 10px;
  height: 44px;
  line-height: 44px;
  border-radius: 8px;
}
.el-menu :deep(.el-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.06) !important;
}
.el-menu :deep(.el-menu-item.is-active) {
  background-color: rgba(229, 65, 72, 0.18) !important;
  color: #fff !important;
  font-weight: 600;
}
.el-menu :deep(.el-menu-item.is-active .el-icon) {
  color: #ff8a8f;
}
</style>
