<template>
  <div class="dash">
    <el-row :gutter="16">
      <el-col v-for="item in cards" :key="item.path" :xs="24" :sm="12" :md="8">
        <div class="stat" :class="item.tone" role="button" tabindex="0" @click="go(item)" @keyup.enter="go(item)">
          <div class="stat-main">
            <div class="label">{{ item.label }}</div>
            <div class="value">{{ item.value }}</div>
            <div class="hint">点击查看详情</div>
          </div>
          <div class="stat-icon">
            <el-icon :size="28"><component :is="item.icon" /></el-icon>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import http from '../api/http'

const router = useRouter()
const stats = ref({})

const cards = computed(() => [
  { label: '门店', value: stats.value.stores ?? '-', path: '/stores', icon: 'Shop', tone: 'tone-blue' },
  { label: '用户', value: stats.value.users ?? '-', path: '/users', icon: 'User', tone: 'tone-teal' },
  { label: '订单', value: stats.value.orders ?? '-', path: '/orders', icon: 'List', tone: 'tone-indigo' },
  {
    label: '待支付订单',
    value: stats.value.pendingOrders ?? '-',
    path: '/orders',
    query: { status: 'pending' },
    icon: 'Clock',
    tone: 'tone-amber'
  },
  { label: '积分商品', value: stats.value.mallGoods ?? '-', path: '/mall', icon: 'Goods', tone: 'tone-rose' },
  { label: '优惠券模板', value: stats.value.coupons ?? '-', path: '/coupons', icon: 'Ticket', tone: 'tone-violet' }
])

function go(item) {
  router.push({ path: item.path, query: item.query || {} })
}

onMounted(async () => {
  stats.value = await http.get('/dashboard')
})
</script>

<style scoped>
.dash {
  max-width: 1100px;
}
.stat {
  display: flex;
  align-items: stretch;
  justify-content: space-between;
  gap: 12px;
  min-height: 118px;
  margin-bottom: 16px;
  padding: 20px 18px;
  border-radius: 14px;
  border: 1px solid #e8edf3;
  background: #fff;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
}
.stat:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
  border-color: transparent;
}
.stat:focus-visible {
  outline: 2px solid #94a3b8;
  outline-offset: 2px;
}
.stat-main {
  min-width: 0;
}
.label {
  color: #64748b;
  font-size: 14px;
  margin-bottom: 10px;
}
.value {
  font-size: 32px;
  font-weight: 700;
  color: #0f172a;
  line-height: 1.1;
}
.hint {
  margin-top: 10px;
  font-size: 12px;
  color: #94a3b8;
}
.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  align-self: center;
}
.tone-blue .stat-icon { background: #eff6ff; color: #2563eb; }
.tone-teal .stat-icon { background: #f0fdfa; color: #0d9488; }
.tone-indigo .stat-icon { background: #eef2ff; color: #4f46e5; }
.tone-amber .stat-icon { background: #fffbeb; color: #d97706; }
.tone-rose .stat-icon { background: #fff1f2; color: #e11d48; }
.tone-violet .stat-icon { background: #f5f3ff; color: #7c3aed; }
</style>
