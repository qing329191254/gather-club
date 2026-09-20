<template>
  <el-card>
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
        <div v-if="item.kind === 'order'">金额：¥{{ item.amount }}　人数：{{ item.people || '-' }}　用餐：{{ item.room_date || '-' }} {{ item.room_slot || '' }}</div>
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
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../api/http'

const keyword = ref('')
const list = ref([])
const loading = ref(false)
const searched = ref(false)
const actingId = ref('')

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
  } catch {
    /* 取消确认 */
  } finally {
    actingId.value = ''
  }
}
</script>

<style scoped>
.toolbar { display: flex; gap: 8px; margin-bottom: 8px; }
.hint { margin: 0 0 16px; color: #64748b; font-size: 13px; }
.card {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 14px 16px;
  margin-bottom: 12px;
}
.card-head { display: flex; align-items: center; gap: 10px; }
.code { font-size: 22px; font-weight: 700; letter-spacing: 2px; }
.meta { margin-top: 10px; color: #334155; line-height: 1.7; font-size: 14px; }
.actions { margin-top: 12px; }
</style>
