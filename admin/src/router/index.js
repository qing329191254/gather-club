import { createRouter, createWebHistory } from 'vue-router'
import AdminLayout from '../layouts/AdminLayout.vue'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/',
    component: AdminLayout,
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', name: 'dashboard', meta: { title: '概览' }, component: () => import('../views/Dashboard.vue') },
      { path: 'banners', name: 'banners', meta: { title: '首页轮播' }, component: () => import('../views/Banners.vue') },
      { path: 'stores', name: 'stores', meta: { title: '门店管理' }, component: () => import('../views/Stores.vue') },
      { path: 'gather', name: 'gather', meta: { title: '去哪聚' }, component: () => import('../views/Gather.vue') },
      { path: 'nye', name: 'nye', meta: { title: '宴会专题' }, component: () => import('../views/Nye.vue') },
      { path: 'mall', name: 'mall', meta: { title: '积分商城' }, component: () => import('../views/Mall.vue') },
      { path: 'recommend', name: 'recommend', meta: { title: '精选推荐' }, component: () => import('../views/Recommend.vue') },
      { path: 'content', name: 'content', meta: { title: '内容配置' }, component: () => import('../views/Content.vue') },
      { path: 'orders', name: 'orders', meta: { title: '订单管理' }, component: () => import('../views/Orders.vue') },
      { path: 'rooms', name: 'rooms', meta: { title: '包房库存' }, component: () => import('../views/Rooms.vue') },
      { path: 'coupons', name: 'coupons', meta: { title: '优惠券' }, component: () => import('../views/Coupons.vue') },
      { path: 'users', name: 'users', meta: { title: '用户' }, component: () => import('../views/Users.vue') },
      { path: 'video', name: 'video', meta: { title: '视频号' }, component: () => import('../views/Video.vue') },
      { path: 'settings', name: 'settings', meta: { title: '站点配置' }, component: () => import('../views/Settings.vue') }
    ]
  }
]

const router = createRouter({
  history: createWebHistory('/admin/'),
  routes
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('gather_admin_token')
  if (to.path !== '/login' && !token) {
    next('/login')
    return
  }
  if (to.path === '/login' && token) {
    next('/dashboard')
    return
  }
  next()
})

export default router
