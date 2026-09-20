<template>
  <el-card>
    <div class="toolbar">
      <el-input v-model="keyword" placeholder="昵称或手机号" style="width: 240px" clearable @keyup.enter="onSearch" />
      <el-button type="primary" @click="onSearch">查询</el-button>
    </div>
    <el-table :data="list" stripe>
      <el-table-column prop="nickname" label="昵称" width="120" />
      <el-table-column prop="phone" label="手机" width="120" />
      <el-table-column prop="points" label="积分" width="90" />
      <el-table-column prop="table_count" label="近1年桌数" width="110" />
      <el-table-column prop="vip_level" label="会员" width="90" />
      <el-table-column label="操作" width="260" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDetail(row)">详情</el-button>
          <el-button link type="primary" :loading="busy('adjust-list-' + row.id)" @click="adjust(row, 'adjust-list-' + row.id)">调积分</el-button>
          <el-button link type="warning" :loading="busy('vip-list-' + row.id)" @click="setVip(row, 'vip-list-' + row.id)">改等级</el-button>
        </template>
      </el-table-column>
    </el-table>
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

    <el-drawer v-model="drawer" :title="drawerTitle" size="560px" destroy-on-close @closed="onDrawerClosed">
      <div v-loading="detailLoading" class="detail">
        <el-tabs v-model="detailTab" @tab-change="onDetailTab">
          <el-tab-pane label="基本信息" name="profile" />
          <el-tab-pane label="积分流水" name="points" />
          <el-tab-pane label="优惠券" name="coupons" />
          <el-tab-pane label="收货地址" name="addresses" />
        </el-tabs>

        <template v-if="detailTab === 'profile'">
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="昵称">{{ detail.nickname || '-' }}</el-descriptions-item>
            <el-descriptions-item label="手机">{{ detail.phone || '-' }}</el-descriptions-item>
            <el-descriptions-item label="生日">{{ detail.birthday || '-' }}</el-descriptions-item>
            <el-descriptions-item label="兴趣爱好">{{ detail.hobby || '-' }}</el-descriptions-item>
            <el-descriptions-item label="积分">{{ detail.points ?? 0 }}</el-descriptions-item>
            <el-descriptions-item label="会员">
              {{ detail.vip_level || '-' }}
              <span v-if="detail.vip_manual">（已固定）</span>
            </el-descriptions-item>
            <el-descriptions-item label="近1年桌数">{{ detail.table_count ?? 0 }}</el-descriptions-item>
            <el-descriptions-item label="已注销">{{ detail.cancelled ? '是' : '否' }}</el-descriptions-item>
            <el-descriptions-item label="注册时间">{{ formatTime(detail.created_at) }}</el-descriptions-item>
          </el-descriptions>
          <div class="detail-actions">
            <el-button type="primary" :loading="busy('adjust-profile-' + detail.id)" @click="adjust(detail, 'adjust-profile-' + detail.id)">调积分</el-button>
            <el-button type="warning" :loading="busy('vip-profile-' + detail.id)" @click="setVip(detail, 'vip-profile-' + detail.id)">改等级</el-button>
          </div>
        </template>

        <template v-else-if="detailTab === 'points'">
          <div class="subbar">
            <span>当前余额 <b>{{ pointsBalance }}</b></span>
            <el-button size="small" type="primary" :loading="busy('adjust-points-' + detail.id)" @click="adjust(detail, 'adjust-points-' + detail.id)">调积分</el-button>
          </div>
          <el-table :data="pointsList" size="small" stripe max-height="420">
            <el-table-column prop="created_at" label="时间" width="160" />
            <el-table-column prop="title" label="说明" min-width="140" />
            <el-table-column prop="value" label="变动" width="90">
              <template #default="{ row }">
                <span :class="row.value >= 0 ? 'plus' : 'minus'">{{ row.value >= 0 ? '+' : '' }}{{ row.value }}</span>
              </template>
            </el-table-column>
          </el-table>
          <div class="pager compact">
            <el-pagination
              v-model:current-page="pointsPage"
              v-model:page-size="pointsPageSize"
              :total="pointsTotal"
              :page-sizes="[10, 20, 50]"
              layout="total, prev, pager, next"
              small
              background
              @current-change="loadPoints"
              @size-change="() => { pointsPage = 1; loadPoints() }"
            />
          </div>
        </template>

        <template v-else-if="detailTab === 'coupons'">
          <div class="subbar">
            <el-select v-model="issueCouponId" placeholder="选择优惠券模板" clearable style="width: 220px" filterable>
              <el-option
                v-for="c in couponTemplates"
                :key="c.id"
                :label="`${c.name}（¥${c.amount}）`"
                :value="c.id"
              />
            </el-select>
            <el-button type="primary" size="small" :disabled="!issueCouponId" :loading="busy('issue')" @click="issueCoupon">补发</el-button>
          </div>
          <el-table :data="couponsList" size="small" stripe max-height="460">
            <el-table-column prop="name" label="名称" min-width="120" />
            <el-table-column prop="amount" label="面额" width="70" />
            <el-table-column prop="expire" label="有效期" width="100" />
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">{{ couponStatusText(row.status) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="70">
              <template #default="{ row }">
                <el-button
                  v-if="row.status === 'unused'"
                  link
                  type="danger"
                  :loading="busy('void-' + row.id)"
                  @click="voidCoupon(row)"
                >作废</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!couponsList.length" description="暂无优惠券" :image-size="64" />
        </template>

        <template v-else-if="detailTab === 'addresses'">
          <el-table :data="addressesList" size="small" stripe>
            <el-table-column prop="name" label="收货人" width="90" />
            <el-table-column prop="phone" label="手机" width="110" />
            <el-table-column label="地址" min-width="200">
              <template #default="{ row }">
                {{ row.region || '' }}{{ row.detail || '' }}
                <el-tag v-if="row.is_default" size="small" type="success" style="margin-left: 6px">默认</el-tag>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!addressesList.length" description="暂无收货地址" :image-size="64" />
        </template>
      </div>
    </el-drawer>
  </el-card>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../api/http'
import { useLock } from '../composables/useLock'
import { usePager } from '../composables/usePager'

const list = ref([])
const keyword = ref('')
const { page, pageSize, total, applyPage, resetPage, pageParams } = usePager()

const drawer = ref(false)
const detailLoading = ref(false)
const { busy, run } = useLock()
const detailTab = ref('profile')
const detail = reactive({
  id: null,
  nickname: '',
  phone: '',
  birthday: '',
  hobby: '',
  points: 0,
  vip_level: '',
  table_count: 0,
  openid: '',
  phone_edited: false,
  cancelled: false,
  created_at: null
})

const pointsList = ref([])
const pointsPage = ref(1)
const pointsPageSize = ref(20)
const pointsTotal = ref(0)
const pointsBalance = ref(0)

const couponsList = ref([])
const couponTemplates = ref([])
const issueCouponId = ref(null)

const addressesList = ref([])

const drawerTitle = computed(() => {
  if (!detail.id) return '用户详情'
  return `用户详情 · ${detail.nickname || detail.id}`
})

function formatTime(v) {
  if (!v) return '-'
  return String(v).replace('T', ' ').slice(0, 19)
}

function couponStatusText(status) {
  return { unused: '未使用', used: '已使用', expired: '已失效' }[status] || status || '-'
}

async function load() {
  const res = await http.get('/users', {
    params: pageParams({ keyword: keyword.value || undefined })
  })
  list.value = applyPage(res)
}

function onSearch() {
  if (!resetPage()) load()
}

async function openDetail(row) {
  detailTab.value = 'profile'
  drawer.value = true
  detailLoading.value = true
  try {
    const res = await http.get(`/users/${row.id}`)
    Object.assign(detail, res)
    pointsBalance.value = res.points || 0
  } finally {
    detailLoading.value = false
  }
}

function onDrawerClosed() {
  detail.id = null
  pointsList.value = []
  couponsList.value = []
  addressesList.value = []
  issueCouponId.value = null
}

async function onDetailTab(name) {
  if (!detail.id) return
  if (name === 'points') {
    pointsPage.value = 1
    await loadPoints()
  } else if (name === 'coupons') {
    await Promise.all([loadCoupons(), loadCouponTemplates()])
  } else if (name === 'addresses') {
    await loadAddresses()
  } else if (name === 'profile') {
    const res = await http.get(`/users/${detail.id}`)
    Object.assign(detail, res)
  }
}

async function loadPoints() {
  if (!detail.id) return
  const res = await http.get(`/users/${detail.id}/points`, {
    params: { page: pointsPage.value, page_size: pointsPageSize.value }
  })
  pointsList.value = res.list || res.items || []
  pointsTotal.value = res.total || 0
  pointsBalance.value = res.balance ?? detail.points ?? 0
}

async function loadCoupons() {
  if (!detail.id) return
  couponsList.value = await http.get(`/users/${detail.id}/coupons`)
}

async function loadCouponTemplates() {
  const res = await http.get('/coupons', { params: { page: 1, page_size: 100 } })
  couponTemplates.value = res.list || res.items || []
}

async function loadAddresses() {
  if (!detail.id) return
  addressesList.value = await http.get(`/users/${detail.id}/addresses`)
}

async function adjust(row, visual) {
  if (!row?.id) return
  return run('adjust-' + row.id, async () => {
  const { value } = await ElMessageBox.prompt('输入增减积分（可为负数）', '调整积分', {
    inputValue: '10',
    inputPattern: /^-?\d+$/,
    inputErrorMessage: '请输入整数'
  })
  await http.post(`/users/${row.id}/points`, { points: Number(value), title: '后台调整' })
  ElMessage.success('已调整')
  load()
  if (drawer.value && detail.id === row.id) {
    const res = await http.get(`/users/${row.id}`)
    Object.assign(detail, res)
    if (detailTab.value === 'points') await loadPoints()
  }
  }, visual)
}

async function setVip(row, visual) {
  if (!row?.id) return
  return run('vip-' + row.id, async () => {
  const { value } = await ElMessageBox.prompt('请输入 V0、V1、V2 或 V3。保存后不再随消费桌数自动变化。', '修改会员等级', {
    inputValue: row.vip_level || detail.vip_level || 'V0'
  })
  await http.put(`/users/${row.id}/vip`, null, { params: { vip_level: value, lock: true } })
  ElMessage.success('已保存该等级')
  load()
  if (drawer.value && detail.id === row.id) {
    const res = await http.get(`/users/${row.id}`)
    Object.assign(detail, res)
  }
  }, visual)
}

async function issueCoupon() {
  if (!detail.id || !issueCouponId.value) return
  return run('issue', async () => {
  await http.post(`/users/${detail.id}/coupons`, null, { params: { coupon_id: issueCouponId.value } })
  ElMessage.success('已补发')
  issueCouponId.value = null
  await loadCoupons()
  })
}

async function voidCoupon(row) {
  return run('void-' + row.id, async () => {
  await ElMessageBox.confirm(`确认作废「${row.name}」？`, '提示')
  await http.post(`/users/${detail.id}/coupons/${row.id}/void`)
  ElMessage.success('已作废')
  await loadCoupons()
  })
}

onMounted(load)
</script>

<style scoped>
.toolbar { margin-bottom: 12px; display: flex; gap: 8px; }
.pager {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
.pager.compact { margin-top: 12px; }
.detail { min-height: 240px; }
.detail-actions { margin-top: 16px; display: flex; gap: 8px; }
.subbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 12px;
}
.mono { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; word-break: break-all; }
.plus { color: #16a34a; }
.minus { color: #dc2626; }
</style>
