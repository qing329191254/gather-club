<template>
  <el-card>
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
        <el-button type="primary" @click="onSave">保存配置</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../api/http'
import ImageField from '../components/ImageField.vue'

const rulesText = ref('')
const form = reactive({
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

async function load() {
  const res = await http.get('/config/site')
  Object.assign(form, {
    logo: '/static/icons/brand.png',
    hotline: '',
    stewardTitle: '',
    stewardTip: '',
    stewardQr: '',
    mallRules: [],
    roomCapacity: { lunch: 4, dinner: 8 },
    nyeOpenStart: '2027-02-05',
    nyeOpenEnd: '2027-02-12'
  }, res.value || {})
  if (!form.logo) form.logo = '/static/icons/brand.png'
  if (!form.roomCapacity) form.roomCapacity = { lunch: 4, dinner: 8 }
  rulesText.value = (form.mallRules || []).join('\n')
}

async function onSave() {
  const value = {
    ...form,
    mallRules: rulesText.value.split(/\n/).map((s) => s.trim()).filter(Boolean)
  }
  await http.put('/config/site', { value })
  ElMessage.success('已保存')
}

onMounted(load)
</script>
