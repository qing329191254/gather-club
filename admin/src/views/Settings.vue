<template>
  <el-card>
    <div class="toolbar">
      <el-button type="primary" :loading="savingWhich === 'top'" @click="onSave(true, 'top')">保存配置</el-button>
      <span class="hint">{{ statusText }}</span>
    </div>
    <el-tabs v-model="activePane">
      <el-tab-pane label="基础信息" name="basic">
        <el-form label-width="120px" style="max-width: 780px">
          <el-form-item label="品牌 Logo">
            <ImageField v-model="form.logo" folder="site" placeholder="品牌 Logo" />
          </el-form-item>
          <el-form-item label="客服热线"><el-input v-model="form.hotline" /></el-form-item>
          <el-form-item label="管家标题"><el-input v-model="form.stewardTitle" /></el-form-item>
          <el-form-item label="管家提示"><el-input v-model="form.stewardTip" /></el-form-item>
          <el-form-item label="管家二维码"><ImageField v-model="form.stewardQr" folder="site" /></el-form-item>
          <el-form-item label="入群二维码"><ImageField v-model="form.groupQr" folder="site" /></el-form-item>
          <el-form-item label="积分规则">
            <el-input v-model="rulesText" type="textarea" :rows="6" placeholder="每行一条规则（积分商城）" />
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane label="包房与预订" name="rooms">
        <el-form label-width="120px" style="max-width: 780px">
          <el-form-item label="午市库存默认"><el-input-number v-model="form.roomCapacity.lunch" :min="0" /></el-form-item>
          <el-form-item label="晚市库存默认"><el-input-number v-model="form.roomCapacity.dinner" :min="0" /></el-form-item>
          <el-form-item label="包房单价">
            <el-input-number v-model="loyalty.roomPrice" :min="0" :precision="2" :step="0.01" />
            <span class="inline-tip">支付成功后才锁定包房，填 0 则不能预约</span>
          </el-form-item>
          <p class="section-tip pane-tip">活动可预订日期请在「活动管理」里按活动单独配置。</p>
        </el-form>
      </el-tab-pane>

      <el-tab-pane label="积分会员" name="loyalty">
        <el-form label-width="120px" style="max-width: 780px">
          <el-form-item label="新用户积分">
            <el-input-number v-model="loyalty.welcomePoints" :min="0" />
          </el-form-item>
          <el-form-item label="默认倍率">
            <el-input-number v-model="loyalty.earnRateDefault" :min="0" :step="0.1" :precision="2" />
            <span class="inline-tip">消费金额 × 倍率</span>
          </el-form-item>
          <el-form-item label="会员倍率">
            <el-input-number v-model="loyalty.earnRateV3" :min="0" :step="0.1" :precision="2" />
            <span class="inline-tip">年卡会员消费积分倍率</span>
          </el-form-item>
          <el-form-item label="首单倍率">
            <el-input-number v-model="loyalty.firstOrderRate" :min="0" :step="0.1" :precision="2" />
          </el-form-item>
          <el-form-item label="生日月倍数">
            <el-input-number v-model="loyalty.birthdayMultiplier" :min="1" :step="0.5" :precision="1" />
          </el-form-item>

          <el-divider content-position="left">完善资料奖励</el-divider>
          <el-form-item label="开启奖励">
            <el-switch v-model="profileReward.enabled" />
            <span class="inline-tip">资料未填完时，进入小程序会提示去完善</span>
          </el-form-item>
          <el-form-item label="奖励积分">
            <el-input-number v-model="profileReward.points" :min="0" />
            <span class="inline-tip">昵称、生日、手机号、兴趣都填完后发放一次</span>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane label="每日签到" name="checkin">
        <el-form label-width="120px" style="max-width: 780px">
          <p class="section-tip pane-tip">按当月累计签到天数发放，每档每月只发一次。</p>
          <el-form-item label="每日签到积分">
            <el-input-number v-model="checkin.dailyPoints" :min="0" />
          </el-form-item>
          <el-form-item label="补签积分">
            <el-input-number v-model="checkin.makeupPoints" :min="0" />
          </el-form-item>
          <el-form-item label="整月满签奖励">
            <el-input-number v-model="checkin.fullMonthBonus" :min="0" />
            <span class="inline-tip">当月每天都签到时额外发放</span>
          </el-form-item>
          <el-form-item label="签到规则文案">
            <el-input v-model="checkin.rules" type="textarea" :rows="3" placeholder="签到页「查看规则」中显示的内容" />
          </el-form-item>
          <el-form-item label="累计奖励档">
            <div class="mile-list">
              <div v-for="(m, i) in checkin.milestones" :key="i" class="mile-row">
                <el-input-number v-model="m.days" :min="1" placeholder="天数" />
                <span class="mile-x">天</span>
                <el-input-number v-model="m.points" :min="0" placeholder="积分" />
                <span class="mile-x">积分</span>
                <el-input v-model="m.label" placeholder="展示文案，如 签到5天" style="width: 160px" />
                <el-button link type="danger" @click="checkin.milestones.splice(i, 1)">删</el-button>
              </div>
              <el-button size="small" @click="addMilestone">+ 增加一档</el-button>
            </div>
          </el-form-item>
          <el-form-item>
            <el-button :loading="restoring" @click="restoreCheckin">恢复签到默认</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>
    </el-tabs>
  </el-card>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../api/http'
import ImageField from '../components/ImageField.vue'

const defaults = () => ({
  logo: '',
  hotline: '',
  stewardTitle: '',
  stewardTip: '',
  stewardQr: '',
  groupQr: '',
  mallRules: [],
  roomCapacity: { lunch: 4, dinner: 8 },
  nyeOpenStart: '2027-02-05',
  nyeOpenEnd: '2027-02-12'
})

const checkinDefaults = () => ({
  dailyPoints: 2,
  makeupPoints: 2,
  fullMonthBonus: 30,
  milestones: [
    { days: 5, points: 2, label: '签到5天' },
    { days: 15, points: 15, label: '签到15天' },
    { days: 25, points: 25, label: '签到25天' }
  ],
  rules: '每日签到可领取积分，当月累计签到可解锁额外奖励。漏签可用补签机会补回，每日仅一次。'
})

const rulesText = ref('')
const activePane = ref('basic')
const form = reactive(defaults())
const checkin = reactive(checkinDefaults())
const profileReward = reactive({
  enabled: false,
  points: 300
})
const loyalty = reactive({
  welcomePoints: 12,
  earnRateDefault: 0.5,
  earnRateV3: 1,
  firstOrderRate: 0.5,
  birthdayMultiplier: 2,
  vipTables: { V1: 1, V2: 2, V3: 5 },
  roomPrice: 0
})
const ready = ref(false)
const savingWhich = ref('')
const restoring = ref(false)
const saving = computed(() => !!savingWhich.value)
const dirty = ref(false)
const lastSavedAt = ref('')
let saveTimer = null

const statusText = computed(() => {
  if (saving.value) return '正在保存…'
  if (dirty.value) return '有未保存修改，将自动保存'
  if (lastSavedAt.value) return `已自动保存 ${lastSavedAt.value}`
  return '修改后会自动保存到服务器'
})

function addMilestone() {
  checkin.milestones.push({ days: 10, points: 5, label: '签到10天' })
}

function buildSiteValue() {
  return {
    ...form,
    roomCapacity: {
      lunch: Number(form.roomCapacity?.lunch ?? 4),
      dinner: Number(form.roomCapacity?.dinner ?? 8)
    },
    mallRules: rulesText.value.split(/\n/).map((s) => s.trim()).filter(Boolean)
  }
}

function buildCheckinValue() {
  return {
    dailyPoints: Number(checkin.dailyPoints ?? 0),
    makeupPoints: Number(checkin.makeupPoints ?? 0),
    fullMonthBonus: Number(checkin.fullMonthBonus ?? 0),
    rules: String(checkin.rules || '').trim(),
    milestones: (checkin.milestones || [])
      .map((m) => ({
        days: Number(m.days) || 0,
        points: Number(m.points) || 0,
        label: String(m.label || '').trim() || `签到${Number(m.days) || 0}天`
      }))
      .filter((m) => m.days > 0)
      .sort((a, b) => a.days - b.days)
  }
}

function applyCheckin(value = {}) {
  const d = checkinDefaults()
  checkin.dailyPoints = value.dailyPoints ?? d.dailyPoints
  checkin.makeupPoints = value.makeupPoints ?? d.makeupPoints
  checkin.fullMonthBonus = value.fullMonthBonus ?? d.fullMonthBonus
  checkin.rules = value.rules || d.rules
  const list = Array.isArray(value.milestones) && value.milestones.length ? value.milestones : d.milestones
  checkin.milestones = list.map((m) => ({
    days: Number(m.days) || 0,
    points: Number(m.points) || 0,
    label: m.label || `签到${m.days || ''}天`
  }))
}

async function load() {
  ready.value = false
  const [siteRes, checkinRes, loyaltyRes, rewardRes] = await Promise.all([
    http.get('/config/site'),
    http.get('/config/checkin'),
    http.get('/config/loyalty'),
    http.get('/config/profile_reward')
  ])
  const value = siteRes.value || {}
  Object.assign(form, defaults(), value)
  if (!form.roomCapacity) form.roomCapacity = { lunch: 4, dinner: 8 }
  rulesText.value = (form.mallRules || []).join('\n')
  applyCheckin(checkinRes.value || {})
  const lv = loyaltyRes.value || {}
  loyalty.welcomePoints = lv.welcomePoints ?? 12
  loyalty.earnRateDefault = lv.earnRateDefault ?? 0.5
  loyalty.earnRateV3 = lv.earnRateV3 ?? 1
  loyalty.firstOrderRate = lv.firstOrderRate ?? 0.5
  loyalty.birthdayMultiplier = lv.birthdayMultiplier ?? 2
  loyalty.roomPrice = lv.roomPrice ?? 0
  loyalty.vipTables = Object.assign({ V1: 1, V2: 2, V3: 5 }, lv.vipTables || {})
  const reward = rewardRes.value || {}
  profileReward.enabled = !!reward.enabled
  profileReward.points = reward.points ?? 300
  dirty.value = false
  ready.value = true
}

async function onSave(showToast = true, which = 'auto') {
  if (savingWhich.value || restoring.value) return
  savingWhich.value = which
  try {
    await Promise.all([
      http.put('/config/site', { value: buildSiteValue() }),
      http.put('/config/checkin', { value: buildCheckinValue() }),
      http.put('/config/loyalty', { value: { ...loyalty, vipTables: { ...loyalty.vipTables } } }),
      http.put('/config/profile_reward', {
        value: { enabled: !!profileReward.enabled, points: Number(profileReward.points) || 0 }
      })
    ])
    dirty.value = false
    lastSavedAt.value = new Date().toLocaleTimeString()
    if (showToast) ElMessage.success('已保存')
  } finally {
    savingWhich.value = ''
  }
}

async function restoreCheckin() {
  if (savingWhich.value || restoring.value) return
  restoring.value = true
  try {
    const res = await http.post('/config/checkin/restore')
    applyCheckin(res.value || {})
    dirty.value = false
    ElMessage.success('已恢复签到默认配置')
  } finally {
    restoring.value = false
  }
}

function scheduleSave() {
  if (!ready.value) return
  dirty.value = true
  if (saveTimer) clearTimeout(saveTimer)
  saveTimer = setTimeout(() => onSave(false), 600)
}

watch(
  () => [
    form.logo,
    form.hotline,
    form.stewardTitle,
    form.stewardTip,
    form.stewardQr,
    form.groupQr,
    form.roomCapacity?.lunch,
    form.roomCapacity?.dinner,
    form.nyeOpenStart,
    form.nyeOpenEnd,
    rulesText.value,
    checkin.dailyPoints,
    checkin.makeupPoints,
    checkin.fullMonthBonus,
    checkin.rules,
    JSON.stringify(checkin.milestones),
    loyalty.welcomePoints,
    loyalty.earnRateDefault,
    loyalty.earnRateV3,
    loyalty.firstOrderRate,
    loyalty.birthdayMultiplier,
    loyalty.roomPrice,
    JSON.stringify(loyalty.vipTables),
    profileReward.enabled,
    profileReward.points
  ],
  () => scheduleSave()
)

onMounted(load)
</script>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}
.hint { color: #64748b; font-size: 13px; }
.section-tip {
  margin: -4px 0 12px 120px;
  color: #64748b;
  font-size: 13px;
  line-height: 1.5;
}
.pane-tip {
  margin-left: 0;
  margin-bottom: 16px;
}
.inline-tip {
  margin-left: 10px;
  color: #94a3b8;
  font-size: 12px;
}
.mile-list { width: 100%; }
.mile-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}
.mile-x { color: #64748b; font-size: 13px; }
</style>
