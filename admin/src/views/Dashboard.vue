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
</style>
