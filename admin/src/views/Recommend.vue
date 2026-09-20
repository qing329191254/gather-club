<template>
  <el-card>
    <div class="toolbar">
      <el-button type="primary" @click="openEdit()">新增推荐</el-button>
      <el-button @click="openBanners">轮播图</el-button>
    </div>
    <el-table :data="list" stripe>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="name" label="名称" min-width="220" show-overflow-tooltip />
      <el-table-column prop="cover" label="封面" min-width="180" show-overflow-tooltip />
      <el-table-column prop="price" label="价格" width="90" />
      <el-table-column prop="sort" label="排序" width="80" />
      <el-table-column label="启用" width="80">
        <template #default="{ row }">
          <el-tag :type="row.enabled ? 'success' : 'info'">{{ row.enabled ? '是' : '否' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="onRemove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="visible" :title="form.id ? '编辑推荐' : '新增推荐'" width="520px">
      <el-form label-width="80px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="封面"><ImageField v-model="form.cover" folder="recommend" /></el-form-item>
        <el-form-item label="价格"><el-input-number v-model="form.price" :min="0" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="form.sort" :min="0" /></el-form-item>
        <el-form-item label="启用"><el-switch v-model="form.enabled" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" @click="onSave">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="bannerVisible" title="推荐轮播" width="520px">
      <el-input v-model="bannersText" type="textarea" :rows="6" placeholder="每行一个图片地址" />
      <div style="margin-top: 8px">
        <el-upload :show-file-list="false" :http-request="appendBannerUpload" accept="image/*">
          <el-button>上传并追加</el-button>
        </el-upload>
      </div>
      <template #footer>
        <el-button @click="bannerVisible = false">取消</el-button>
        <el-button type="primary" @click="saveBanners">保存</el-button>
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
const bannerVisible = ref(false)
const bannersText = ref('')
const form = reactive({ id: null, name: '', cover: '', price: 0, sort: 0, enabled: true })

async function appendBannerUpload(option) {
  const file = option.file
  if (!file) return
  try {
    const body = new FormData()
    body.append('file', file)
    body.append('folder', 'recommend')
    const res = await http.post('/upload', body)
    const url = res.url || ''
    if (url) {
      bannersText.value = bannersText.value ? bannersText.value + '\n' + url : url
      ElMessage.success('已添加')
    }
    option.onSuccess && option.onSuccess(res)
  } catch (e) {
    option.onError && option.onError(e)
  }
}

async function load() {
  const res = await http.get('/recommend')
  list.value = res.list || []
  bannersText.value = (res.banners || []).join('\n')
}

function openEdit(row) {
  Object.assign(form, row || { id: null, name: '', cover: '', price: 0, sort: 0, enabled: true })
  visible.value = true
}

function openBanners() {
  bannerVisible.value = true
}

async function onSave() {
  const payload = { name: form.name, cover: form.cover, price: form.price, sort: form.sort, enabled: form.enabled }
  if (form.id) await http.put(`/recommend/${form.id}`, payload)
  else await http.post('/recommend', payload)
  ElMessage.success('已保存')
  visible.value = false
  load()
}

async function saveBanners() {
  const banners = bannersText.value.split(/\n/).map((s) => s.trim()).filter(Boolean)
  await http.put('/recommend/banners', { banners })
  ElMessage.success('已保存')
  bannerVisible.value = false
}

async function onRemove(row) {
  await ElMessageBox.confirm('确认删除？', '提示')
  await http.delete(`/recommend/${row.id}`)
  load()
}

onMounted(load)
</script>

<style scoped>
.toolbar { margin-bottom: 12px; display: flex; gap: 8px; }
</style>
