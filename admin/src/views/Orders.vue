<template>
  <el-card>
    <div class="toolbar">
      <el-select v-model="status" clearable placeholder="状态" style="width: 140px" @change="load">
        <el-option label="待支付" value="pending" />
        <el-option label="已支付" value="paid" />
        <el-option label="已取消" value="cancelled" />
        <el-option label="已完成" value="completed" />
      </el-select>
      <el-input v-model="keyword" placeholder="订单号/手机号/门店" style="width: 240px" clearable @keyup.enter="load" />
      <el-button type="primary" @click="load">查询</el-button>
    </div>
    <el-table :data="list" stripe>
      <el-table-column prop="id" label="订单号" width="160" />
      <el-table-column prop="type" label="类型" width="80" />
      <el-table-column prop="store_name" label="门店" min-width="140" />
      <el-table-column prop="title" label="标题" min-width="180" show-overflow-tooltip />
      <el-table-column prop="amount" label="金额" width="90" />
      <el-table-column prop="contact_phone" label="手机" width="120" />
      <el-table-column prop="room_date" label="用餐日" width="110" />
      <el-table-column prop="room_slot" label="时段" width="90" />
      <el-table-column prop="status_text" label="状态" width="90" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-dropdown @command="(cmd) => setStatus(row, cmd)">
            <el-button link type="primary">改状态</el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="pending">待支付</el-dropdown-item>
                <el-dropdown-item command="paid">已支付</el-dropdown-item>
                <el-dropdown-item command="completed">已完成</el-dropdown-item>
                <el-dropdown-item command="cancelled">已取消</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../api/http'

const list = ref([])
const status = ref('')
const keyword = ref('')

async function load() {
  list.value = await http.get('/orders', { params: { status: status.value || undefined, keyword: keyword.value || undefined } })
}

async function setStatus(row, next) {
  await http.put(`/orders/${row.id}/status`, { status: next })
  ElMessage.success('已更新')
  load()
}

onMounted(load)
</script>

<style scoped>
.toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
}
</style>
