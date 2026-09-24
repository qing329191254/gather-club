<template>
  <div class="verify-page">
    <el-card class="search-card">
      <div class="toolbar">
        <el-input
          v-model="keyword"
          placeholder="输入手机号或 8 位核销码"
          clearable
          style="width: 320px"
          @keyup.enter="onSearch"
        />
        <el-button type="primary" :loading="loading" @click="onSearch">查询</el-button>
      </div>
      <p class="hint">顾客在订单或优惠券页出示核销码。手机号只列出待核销订单和未使用的券；输入核销码可看到是否已经核销过。</p>

      <el-empty v-if="searched && !list.length" description="没有找到可核销的订单或优惠券" />

      <div v-for="item in list" :key="item.kind + '-' + item.id" class="card">
        <div class="card-head">
          <el-tag :type="item.kind === 'order' ? 'warning' : 'success'" size="small">
            {{ item.kind === 'order' ? '订单' : '到店券' }}
          </el-tag>
          <span class="code">{{ item.verify_code || '—' }}</span>
          <el-tag size="small" :type="item.can_verify ? 'danger' : 'info'">{{ item.status_text }}</el-tag>
        </div>
        <div class="meta">
          <div>{{ item.title }} <span v-if="item.spec">· {{ item.spec }}</span></div>
          <div v-if="item.store_name">门店：{{ item.store_name }}</div>
          <div v-if="item.kind === 'order'">
            金额：¥{{ item.amount }}
            <span v-if="item.member_reserve">　到店应收：¥{{ item.settle_amount }}</span>
            <span v-if="item.member_reserve">　（会员免付）</span>
            　人数：{{ item.people || '-' }}　用餐：{{ item.room_date || '待选日期' }} {{ item.room_slot || '' }}
          </div>
          <div v-else>面额：¥{{ item.amount }}　有效期：{{ item.expire || '-' }}</div>
          <div>顾客：{{ item.contact_name || '-' }}　{{ item.contact_phone || '-' }}</div>
        </div>
        <div class="actions">
          <el-button
            type="primary"
            :disabled="!item.can_verify"
            :loading="actingId === item.kind + item.id"
            @click="onVerify(item)"
          >
            {{ item.can_verify ? '确认核销' : '不可核销' }}
          </el-button>
        </div>
      </div>
    </el-card>

    <el-card class="logs-card page-fill">
      <template #header>
        <div class="logs-head">
          <span>核销记录</span>
          <span class="hint">按日查看台账，默认今天</span>
        </div>
      </template>
      <div class="toolbar">
        <el-date-picker
          v-model="logDate"
          type="date"
          value-format="YYYY-MM-DD"
          placeholder="日期"
          style="width: 160px"
          @change="onLogSearch"
        />
        <el-select v-model="logKind" clearable placeholder="全部类型" style="width: 120px" @change="onLogSearch">
          <el-option label="订单" value="order" />
          <el-option label="到店券" value="coupon" />
        </el-select>
        <el-input
          v-model="logKeyword"
          placeholder="核销码/手机/标题"
          clearable
          style="width: 200px"
          @keyup.enter="onLogSearch"
        />
        <el-button type="primary" @click="onLogSearch">查询</el-button>
      </div>
      <div class="table-wrap">
        <el-table :data="logs" stripe height="100%">
          <el-table-column prop="created_at" label="时间" width="170" />
          <el-table-column label="类型" width="90">
            <template #default="{ row }">{{ row.kind === 'order' ? '订单' : '到店券' }}</template>
          </el-table-column>
          <el-table-column prop="verify_code" label="核销码" width="110" />
          <el-table-column prop="title" label="标题" min-width="180" show-overflow-tooltip />
          <el-table-column prop="store_name" label="门店" min-width="140" show-overflow-tooltip />
          <el-table-column prop="contact_phone" label="手机" width="120" />
          <el-table-column prop="amount" label="金额" width="90" />
          <el-table-column prop="admin_name" label="操作人" width="100" />
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
          @current-change="loadLogs"
          @size-change="onLogSearch"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../api/http'
import { usePager } from '../composables/usePager'

const keyword = ref('')
const list = ref([])
const loading = ref(false)
const searched = ref(false)
const actingId = ref('')

const logs = ref([])
const logDate = ref(todayStr())
const logKind = ref('')
const logKeyword = ref('')
const { page, pageSize, total, applyPage, resetPage, pageParams } = usePager()

function todayStr() {
  const d = new Date()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${d.getFullYear()}-${m}-${day}`
}

async function onSearch() {
  const q = keyword.value.trim()
  if (!q) {
    ElMessage.warning('请输入手机号或核销码')
    return
  }
  if (loading.value) return
  loading.value = true
  searched.value = true
  try {
    const res = await http.get('/verify', { params: { q } })
    list.value = res.list || []
  } finally {
    loading.value = false
  }
}

async function onVerify(item) {
  const id = item.kind + item.id
  if (actingId.value) return
  actingId.value = id
  try {
    const label = item.kind === 'order' ? '订单' : '优惠券'
    await ElMessageBox.confirm(`确认核销这张${label}？`, '核销', { type: 'warning' })
    const res = await http.post('/verify', { kind: item.kind, id: item.id })
    ElMessage.success(res.message || '已核销')
    await onSearch()
    await loadLogs()
  } catch {
    /* 取消确认 */
  } finally {
    actingId.value = ''
  }
}

async function loadLogs() {
  const res = await http.get('/verify/logs', {
    params: pageParams({
      date: logDate.value || undefined,
      kind: logKind.value || undefined,
      keyword: logKeyword.value.trim() || undefined
    })
  })
  logs.value = applyPage(res)
}

function onLogSearch() {
  if (!resetPage()) loadLogs()
}

onMounted(loadLogs)
</script>

<style scoped>
.verify-page {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.search-card {
  flex-shrink: 0;
}
.logs-card {
  flex: 1;
  min-height: 280px;
}
.toolbar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 8px;
}
.hint {
  margin: 0 0 16px;
  color: #64748b;
  font-size: 13px;
}
.logs-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.logs-head .hint {
  margin: 0;
  font-weight: 400;
}
.card {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 14px 16px;
  margin-bottom: 12px;
}
.card-head {
  display: flex;
  align-items: center;
  gap: 10px;
}
.code {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 2px;
}
.meta {
  margin-top: 10px;
  color: #334155;
  line-height: 1.7;
  font-size: 14px;
}
.actions {
  margin-top: 12px;
}
</style>
