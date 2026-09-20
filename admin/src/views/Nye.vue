<template>
  <el-card>
    <div class="toolbar">
      <el-button type="primary" @click="openEdit()">新增年夜饭门店</el-button>
    </div>
    <el-table :data="list" stripe>
      <el-table-column prop="id" label="ID" width="110" />
      <el-table-column prop="name" label="名称" min-width="220" show-overflow-tooltip />
      <el-table-column prop="price" label="价格" width="90" />
      <el-table-column prop="address" label="地址" min-width="180" show-overflow-tooltip />
      <el-table-column prop="open_start" label="开放起" width="110" />
      <el-table-column prop="open_end" label="开放止" width="110" />
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="onRemove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="visible" :title="editing ? '编辑' : '新增'" width="720px">
      <el-form label-width="100px">
        <el-form-item label="ID"><el-input v-model="form.id" :disabled="editing" /></el-form-item>
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="封面"><ImageField v-model="form.cover" folder="nye" /></el-form-item>
        <el-form-item label="价格"><el-input-number v-model="form.price" :min="0" /></el-form-item>
        <el-form-item label="原价"><el-input-number v-model="form.origin_price" :min="0" /></el-form-item>
        <el-form-item label="标签"><el-input v-model="form.tag" /></el-form-item>
        <el-form-item label="地址"><el-input v-model="form.address" /></el-form-item>
        <el-form-item label="路线"><el-input v-model="form.route" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="轮播图"><el-input v-model="bannersText" type="textarea" :rows="2" placeholder="每行一个图片地址" /></el-form-item>
        <el-form-item label="详情长图"><el-input v-model="detailText" type="textarea" :rows="2" placeholder="每行一个图片地址" /></el-form-item>
        <el-form-item label="套餐 JSON"><el-input v-model="packagesText" type="textarea" :rows="8" placeholder="套餐列表 JSON" /></el-form-item>
        <el-form-item label="开放起"><el-input v-model="form.open_start" placeholder="YYYY-MM-DD" /></el-form-item>
        <el-form-item label="开放止"><el-input v-model="form.open_end" placeholder="YYYY-MM-DD" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="form.sort" :min="0" /></el-form-item>
        <el-form-item label="启用"><el-switch v-model="form.enabled" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" @click="onSave">保存</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../api/http'
import ImageField from '../components/ImageField.vue'

const list = ref([])
const visible = ref(false)
const editing = ref(false)
const bannersText = ref('')
const detailText = ref('')
const packagesText = ref('')
const empty = () => ({
  id: '', name: '', cover: '', price: 0, origin_price: 0, tag: '年夜饭', address: '', route: '',
  lat: 0, lng: 0, banners: [], detail_images: [], recent_buy: {}, packages: [],
  open_start: '2027-02-05', open_end: '2027-02-12', sort: 0, enabled: true
})
const form = reactive(empty())

async function load() {
  list.value = await http.get('/nye')
}

function openEdit(row) {
  editing.value = !!row
  Object.assign(form, empty(), row || {})
  bannersText.value = (form.banners || []).join('\n')
  detailText.value = (form.detail_images || []).join('\n')
  packagesText.value = form.packages && form.packages.length ? JSON.stringify(form.packages, null, 2) : ''
  visible.value = true
}

async function onSave() {
  let packages = []
  if (packagesText.value.trim()) {
    try {
      packages = JSON.parse(packagesText.value)
      if (!Array.isArray(packages)) throw new Error('not array')
    } catch (e) {
      ElMessage.error('套餐 JSON 格式不正确')
      return
    }
  }
  const payload = {
    ...form,
    banners: bannersText.value.split(/\n/).map((s) => s.trim()).filter(Boolean),
    detail_images: detailText.value.split(/\n/).map((s) => s.trim()).filter(Boolean),
    packages
  }
  if (editing.value) await http.put(`/nye/${form.id}`, payload)
  else await http.post('/nye', payload)
  ElMessage.success('已保存')
  visible.value = false
  load()
}

async function onRemove(row) {
  await ElMessageBox.confirm('确认删除？', '提示')
  await http.delete(`/nye/${row.id}`)
  load()
}

onMounted(load)
</script>

<style scoped>
.toolbar { margin-bottom: 12px; }
</style>
