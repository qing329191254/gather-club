<template>
  <el-card>
    <div class="toolbar">
      <el-button type="primary" @click="openEdit()">新增酒店</el-button>
      <el-button @click="openBanners">顶部轮播</el-button>
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
      <el-table-column prop="sort" label="排序" width="80" />
      <el-table-column label="是否展示" width="100">
        <template #default="{ row }">
          <el-tag :type="row.enabled ? 'success' : 'info'" size="small">
            {{ row.enabled ? '展示' : '隐藏' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" :loading="busy('remove-' + row.id)" @click="onRemove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="visible" :title="form.id ? '编辑酒店' : '新增酒店'" width="560px">
      <el-form label-width="90px">
        <el-form-item label="名称" required>
          <el-input v-model="form.name" placeholder="酒店名称" />
        </el-form-item>
        <el-form-item label="封面">
          <ImageField v-model="form.cover" folder="recommend" />
        </el-form-item>
        <el-form-item label="参考价">
          <el-input-number v-model="form.price" :min="0" :precision="0" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort" :min="0" />
          <span class="hint">数字越小越靠前</span>
        </el-form-item>
        <el-form-item label="是否展示">
          <el-switch v-model="form.enabled" active-text="展示" inactive-text="隐藏" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" :loading="busy('save')" @click="onSave">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="bannerVisible" title="订酒店页顶部轮播" width="640px">
      <ImageListField v-model="banners" folder="recommend" />
      <template #footer>
        <el-button @click="bannerVisible = false">取消</el-button>
        <el-button type="primary" :loading="busy('banners')" @click="saveBanners">保存</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../api/http'
import { useLock } from '../composables/useLock'
import ImageField from '../components/ImageField.vue'
import ImageListField from '../components/ImageListField.vue'

const { busy, run } = useLock()

const list = ref([])
const visible = ref(false)
const bannerVisible = ref(false)
const banners = ref([])
const form = reactive({ id: null, name: '', cover: '', price: 0, sort: 0, enabled: true })
let bannerTimer = null

async function load() {
  const res = await http.get('/recommend')
  list.value = res.list || []
  banners.value = [...(res.banners || [])]
}

function openEdit(row) {
  Object.assign(form, row || { id: null, name: '', cover: '', price: 0, sort: 0, enabled: true })
  visible.value = true
}

async function onSave() {
  return run('save', async () => {
  if (!form.name?.trim()) {
    ElMessage.warning('请填写名称')
    return
  }
  const payload = {
    name: form.name.trim(),
    cover: form.cover,
    price: form.price,
    sort: form.sort,
    enabled: form.enabled
  }
  if (form.id) await http.put(`/recommend/${form.id}`, payload)
  else await http.post('/recommend', payload)
  ElMessage.success('已保存')
  visible.value = false
  load()
  })
}

async function saveBanners(showToast = true) {
  return run('banners', async () => {
  await http.put('/recommend/banners', { banners: banners.value.filter(Boolean) })
  if (showToast) {
    ElMessage.success('已保存')
    bannerVisible.value = false
  }
  })
}

function openBanners() {
  bannerVisible.value = true
}

watch(
  banners,
  () => {
    if (!bannerVisible.value) return
    if (bannerTimer) clearTimeout(bannerTimer)
    bannerTimer = setTimeout(() => saveBanners(false), 600)
  },
  { deep: true }
)

async function onRemove(row) {
  return run('remove-' + row.id, async () => {
  await ElMessageBox.confirm(`确认删除「${row.name}」？`, '提示')
  await http.delete(`/recommend/${row.id}`)
  load()
  })
}

onMounted(load)
</script>

<style scoped>
.toolbar { margin-bottom: 12px; display: flex; gap: 8px; }
.hint { margin-left: 8px; color: #94a3b8; font-size: 12px; }
.muted { color: #94a3b8; font-size: 12px; }
</style>
