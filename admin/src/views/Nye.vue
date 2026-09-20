<template>
  <el-card>
    <div class="toolbar">
      <el-button type="primary" @click="openEdit()">新增年夜饭门店</el-button>
    </div>
    <el-table :data="list" stripe>
      <el-table-column label="封面" width="100">
        <template #default="{ row }">
          <el-image v-if="row.cover" :src="row.cover" style="width: 72px; height: 48px" fit="cover" />
          <span v-else class="muted">暂无</span>
        </template>
      </el-table-column>
      <el-table-column prop="name" label="名称" min-width="220" show-overflow-tooltip />
      <el-table-column prop="price" label="价格" width="90" />
      <el-table-column prop="address" label="地址" min-width="180" show-overflow-tooltip />
      <el-table-column prop="open_start" label="开放起" width="110" />
      <el-table-column prop="open_end" label="开放止" width="110" />
      <el-table-column label="是否上架" width="100">
        <template #default="{ row }">
          <el-tag :type="row.enabled ? 'success' : 'info'" size="small">
            {{ row.enabled ? '上架' : '下架' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="onRemove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="visible" :title="editing ? '编辑年夜饭门店' : '新增年夜饭门店'" width="720px">
      <el-form label-width="100px">
        <el-form-item label="名称" required>
          <el-input v-model="form.name" placeholder="例如：上海莘庄店-天天俱乐部-2027年夜饭" />
        </el-form-item>
        <el-form-item label="封面">
          <ImageField v-model="form.cover" folder="nye" />
        </el-form-item>
        <el-form-item label="现价">
          <el-input-number v-model="form.price" :min="0" :precision="0" />
        </el-form-item>
        <el-form-item label="原价">
          <el-input-number v-model="form.origin_price" :min="0" :precision="0" />
        </el-form-item>
        <el-form-item label="角标文案">
          <el-input v-model="form.tag" placeholder="例如：年夜饭" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="form.address" placeholder="门店详细地址" />
        </el-form-item>
        <el-form-item label="路线说明">
          <el-input v-model="form.route" type="textarea" :rows="2" placeholder="怎么走、地铁公交等，可选" />
        </el-form-item>
        <el-form-item label="轮播图">
          <el-input v-model="bannersText" type="textarea" :rows="2" placeholder="每行一个图片链接" />
        </el-form-item>
        <el-form-item label="详情长图">
          <el-input v-model="detailText" type="textarea" :rows="2" placeholder="每行一个图片链接" />
        </el-form-item>
        <el-form-item label="套餐配置">
          <el-input v-model="packagesText" type="textarea" :rows="8" placeholder="套餐列表（技术配置，一般不用改）" />
        </el-form-item>
        <el-form-item label="开放起">
          <el-input v-model="form.open_start" placeholder="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="开放止">
          <el-input v-model="form.open_end" placeholder="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort" :min="0" />
          <span class="hint">数字越小越靠前</span>
        </el-form-item>
        <el-form-item label="是否上架">
          <el-switch v-model="form.enabled" active-text="上架" inactive-text="下架" />
        </el-form-item>
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

function genId() {
  return `nye${Date.now().toString(36)}`
}

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
  if (!form.name?.trim()) {
    ElMessage.warning('请填写名称')
    return
  }
  let packages = []
  if (packagesText.value.trim()) {
    try {
      packages = JSON.parse(packagesText.value)
      if (!Array.isArray(packages)) throw new Error('not array')
    } catch (e) {
      ElMessage.error('套餐配置格式不正确，请联系技术处理')
      return
    }
  }
  const payload = {
    ...form,
    id: editing.value ? form.id : (form.id || genId()),
    name: form.name.trim(),
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
  await ElMessageBox.confirm(`确认删除「${row.name}」？`, '提示')
  await http.delete(`/nye/${row.id}`)
  load()
}

onMounted(load)
</script>

<style scoped>
.toolbar { margin-bottom: 12px; }
.hint { margin-left: 8px; color: #94a3b8; font-size: 12px; }
.muted { color: #94a3b8; font-size: 12px; }
</style>
