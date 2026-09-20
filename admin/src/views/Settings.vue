<template>
  <el-card>
    <div class="toolbar">
      <el-button type="primary" :loading="saving" @click="onSave">保存配置</el-button>
      <el-button :loading="bootstrapping" @click="onBootstrap">同步品牌图到云存储</el-button>
      <span class="hint">{{ statusText }}</span>
    </div>
    <el-form label-width="120px" style="max-width: 720px">
      <el-form-item label="品牌 Logo">
        <ImageField v-model="form.logo" folder="site" placeholder="小程序品牌 Logo" />
      </el-form-item>
      <el-form-item label="客服热线"><el-input v-model="form.hotline" /></el-form-item>
      <el-form-item label="管家标题"><el-input v-model="form.stewardTitle" /></el-form-item>
      <el-form-item label="管家提示"><el-input v-model="form.stewardTip" /></el-form-item>
      <el-form-item label="管家二维码"><ImageField v-model="form.stewardQr" folder="site" /></el-form-item>
      <el-form-item label="午市库存默认"><el-input-number v-model="form.roomCapacity.lunch" :min="0" /></el-form-item>
      <el-form-item label="晚市库存默认"><el-input-number v-model="form.roomCapacity.dinner" :min="0" /></el-form-item>
      <el-form-item label="专题开放起"><el-input v-model="form.nyeOpenStart" placeholder="宴会专题可预订开始日期" /></el-form-item>
      <el-form-item label="专题开放止"><el-input v-model="form.nyeOpenEnd" placeholder="宴会专题可预订结束日期" /></el-form-item>
      <el-form-item label="积分规则">
        <el-input v-model="rulesText" type="textarea" :rows="6" placeholder="每行一条规则" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="saving" @click="onSave">保存配置</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../api/http'
import ImageField from '../components/ImageField.vue'

const defaults = () => ({
  logo: '/static/icons/brand.png',
  hotline: '',
  stewardTitle: '',
  stewardTip: '',
  stewardQr: '',
  mallRules: [],
  roomCapacity: { lunch: 4, dinner: 8 },
  nyeOpenStart: '2027-02-05',
  nyeOpenEnd: '2027-02-12'
})

const rulesText = ref('')
const form = reactive(defaults())
const ready = ref(false)
const saving = ref(false)
const bootstrapping = ref(false)
const dirty = ref(false)
const lastSavedAt = ref('')
let saveTimer = null

const statusText = computed(() => {
  if (bootstrapping.value) return '正在上传品牌图…'
  if (saving.value) return '正在保存…'
  if (dirty.value) return '有未保存修改，将自动保存'
  if (lastSavedAt.value) return `已自动保存 ${lastSavedAt.value}`
  return '修改后会自动保存到服务器'
})

function buildValue() {
  return {
    ...form,
    roomCapacity: {
      lunch: Number(form.roomCapacity?.lunch ?? 4),
      dinner: Number(form.roomCapacity?.dinner ?? 8)
    },
    mallRules: rulesText.value.split(/\n/).map((s) => s.trim()).filter(Boolean)
  }
}

async function load() {
  ready.value = false
  const res = await http.get('/config/site')
  const value = res.value || {}
  Object.assign(form, defaults(), value)
  if (!form.logo) form.logo = '/static/icons/brand.png'
  if (!form.roomCapacity) form.roomCapacity = { lunch: 4, dinner: 8 }
  rulesText.value = (form.mallRules || []).join('\n')
  dirty.value = false
  ready.value = true
}

async function onSave(showToast = true) {
  if (saving.value) return
  saving.value = true
  try {
    const value = buildValue()
    await http.put('/config/site', { value })
    dirty.value = false
    lastSavedAt.value = new Date().toLocaleTimeString()
    if (showToast) ElMessage.success('已保存')
  } finally {
    saving.value = false
  }
}

async function onBootstrap() {
  bootstrapping.value = true
  try {
    const res = await http.post('/assets/bootstrap', null, { params: { force: true } })
    if (res.ok === false) {
      ElMessage.warning(res.reason || '云存储未就绪')
      return
    }
    ElMessage.success(`已同步品牌图（上传 ${res.uploaded || 0} 张）`)
    await load()
  } finally {
    bootstrapping.value = false
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
    form.roomCapacity?.lunch,
    form.roomCapacity?.dinner,
    form.nyeOpenStart,
    form.nyeOpenEnd,
    rulesText.value
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
.hint {
  color: #94a3b8;
  font-size: 13px;
}
</style>
