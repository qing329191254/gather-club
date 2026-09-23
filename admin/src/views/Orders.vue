<template>
  <el-card class="page-fill">
    <div class="toolbar">
      <el-select v-model="status" clearable placeholder="状态" style="width: 140px" @change="onSearch">
        <el-option label="待支付" value="pending" />
        <el-option label="待核销" value="paid" />
        <el-option label="已完成" value="completed" />
        <el-option label="已取消" value="cancelled" />
        <el-option label="待退款" value="refund_pending" />
        <el-option label="已退款" value="refunded" />
      </el-select>
      <el-input v-model="keyword" placeholder="订单号/手机号/门店" style="width: 240px" clearable @keyup.enter="onSearch" />
      <el-button type="primary" @click="onSearch">查询</el-button>
    </div>
    <div class="table-wrap">
      <el-table :data="list" stripe height="100%">
        <el-table-column prop="id" label="订单号" width="160" />
        <el-table-column label="类型" width="100">
          <template #default="{ row }">{{ typeLabel(row.type) }}</template>
        </el-table-column>
        <el-table-column prop="store_name" label="门店" min-width="140" />
        <el-table-column prop="title" label="标题" min-width="180" show-overflow-tooltip />
        <el-table-column prop="amount" label="金额" width="90" />
        <el-table-column prop="contact_phone" label="手机" width="120" />
        <el-table-column prop="room_date" label="用餐日" width="110" />
        <el-table-column label="时段" width="90">
          <template #default="{ row }">{{ slotLabel(row.room_slot) }}</template>
        </el-table-column>
        <el-table-column prop="status_text" label="状态" width="90" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <div class="row-ops">
              <el-button link type="primary" @click="showDetail(row)">详情</el-button>
              <el-dropdown @command="(cmd) => setStatus(row, cmd)">
                <el-button link type="primary" :loading="busy('status-' + row.id)">改状态</el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="pending">待支付</el-dropdown-item>
                    <el-dropdown-item command="paid">待核销</el-dropdown-item>
                    <el-dropdown-item command="completed">已完成</el-dropdown-item>
                    <el-dropdown-item command="cancelled">已取消</el-dropdown-item>
                    <el-dropdown-item command="refund_pending">待退款</el-dropdown-item>
                    <el-dropdown-item command="refunded">已退款</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <div class="pager">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        background
        @current-change="load"
        @size-change="onSearch"
      />
    </div>

    <el-drawer v-model="drawer" title="订单详情" size="480px">
      <el-descriptions v-if="current" :column="1" border size="small">
        <el-descriptions-item label="订单号">{{ current.id }}</el-descriptions-item>
        <el-descriptions-item label="类型">{{ typeLabel(current.type) }}</el-descriptions-item>
        <el-descriptions-item label="门店">{{ current.store_name }}</el-descriptions-item>
        <el-descriptions-item label="标题">{{ current.title }}</el-descriptions-item>
        <el-descriptions-item label="规格">{{ current.spec }}</el-descriptions-item>
        <el-descriptions-item label="金额">{{ current.amount }}</el-descriptions-item>
        <el-descriptions-item label="联系人">{{ current.contact_name }} {{ current.contact_phone }}</el-descriptions-item>
        <el-descriptions-item label="人数">{{ current.people || '-' }}</el-descriptions-item>
        <el-descriptions-item label="用餐">{{ current.room_date || '-' }} {{ slotLabel(current.room_slot) }}</el-descriptions-item>
        <el-descriptions-item label="备注">{{ current.remark || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">{{ current.status_text }}</el-descriptions-item>
        <el-descriptions-item v-if="current.extra && current.extra.refundReason" label="退款原因">
          {{ current.extra.refundReason }}。请先在微信商户平台退款，再把状态改为已退款。
        </el-descriptions-item>
      </el-descriptions>
    </el-drawer>
  </el-card>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import http from '../api/http'
import { useLock } from '../composables/useLock'
import { usePager } from '../composables/usePager'

const route = useRoute()
const { busy, run } = useLock()
const list = ref([])
const status = ref('')
const keyword = ref('')
const drawer = ref(false)
const current = ref(null)
const { page, pageSize, total, applyPage, resetPage, pageParams } = usePager()

function typeLabel(type) {
  return {
    gather: '聚餐',
    nye: '宴会',
    room: '包房',
    recommend: '订酒店',
    mall: '积分兑换'
  }[type] || type || '-'
}

function slotLabel(slot) {
  if (slot === 'lunch') return '午市'
  if (slot === 'dinner') return '晚市'
  return slot || ''
}

function showDetail(row) {
  current.value = row
  drawer.value = true
}

function syncFromQuery() {
  status.value = route.query.status ? String(route.query.status) : ''
}

async function load() {
  const res = await http.get('/orders', {
    params: pageParams({
      status: status.value || undefined,
      keyword: keyword.value || undefined
    })
  })
  list.value = applyPage(res)
}

function onSearch() {
  if (!resetPage()) load()
}

async function setStatus(row, next) {
  return run('status-' + row.id, async () => {
  await http.put(`/orders/${row.id}/status`, { status: next })
  ElMessage.success('已更新')
  load()
  })
}

watch(
  () => route.query.status,
  () => {
    syncFromQuery()
    onSearch()
  }
)

onMounted(() => {
  syncFromQuery()
  load()
})
</script>
