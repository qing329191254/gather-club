<template>
  <div>
    <el-row :gutter="16">
      <el-col v-for="item in cards" :key="item.label" :span="8">
        <el-card shadow="hover" class="stat">
          <div class="label">{{ item.label }}</div>
          <div class="value">{{ item.value }}</div>
        </el-card>
      </el-col>
    </el-row>
    <el-card class="mt">
      <template #header>使用说明</template>
      <ol>
        <li>先在本页确认演示数据已导入（门店、年夜饭、积分商品等）。</li>
        <li>管理端打包后产物在 <code>server/static/admin</code>，推送 server 即可同步后台。</li>
        <li>小程序正式接口走 <code>/api/v1/*</code>，云托管用 callContainer 调用。</li>
        <li>上线前请修改管理员密码与 JWT_SECRET，并配置 MySQL。</li>
      </ol>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import http from '../api/http'

const stats = ref({})
const cards = computed(() => [
  { label: '门店', value: stats.value.stores ?? '-' },
  { label: '用户', value: stats.value.users ?? '-' },
  { label: '订单', value: stats.value.orders ?? '-' },
  { label: '待支付订单', value: stats.value.pendingOrders ?? '-' },
  { label: '积分商品', value: stats.value.mallGoods ?? '-' },
  { label: '优惠券模板', value: stats.value.coupons ?? '-' }
])

onMounted(async () => {
  stats.value = await http.get('/dashboard')
})
</script>

<style scoped>
.stat {
  margin-bottom: 16px;
}
.label {
  color: #64748b;
  margin-bottom: 8px;
}
.value {
  font-size: 28px;
  font-weight: 700;
}
.mt {
  margin-top: 8px;
}
ol {
  line-height: 1.9;
  color: #334155;
  padding-left: 18px;
}
code {
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
}
</style>
