<template>
  <el-card>
    <div class="toolbar">
      <el-button type="primary" @click="openEdit()">新增活动</el-button>
      <span class="tip">商品「所属活动」按筛选标识匹配；首页轮播可跳到对应活动页</span>
    </div>
    <el-table :data="list" stripe>
      <el-table-column prop="name" label="活动名称" min-width="140" />
      <el-table-column prop="tag" label="筛选标识" width="120" show-overflow-tooltip />
      <el-table-column label="轮播图" width="90">
        <template #default="{ row }">{{ (row.banners || []).length }}</template>
      </el-table-column>
      <el-table-column prop="open_start" label="开放起" width="110" />
      <el-table-column prop="open_end" label="开放止" width="110" />
      <el-table-column prop="sort" label="排序" width="80" />
      <el-table-column label="是否启用" width="100">
        <template #default="{ row }">
          <el-tag :type="row.enabled ? 'success' : 'info'" size="small">
            {{ row.enabled ? '启用' : '停用' }}
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

    <el-dialog v-model="visible" :title="editing ? '编辑活动' : '新增活动'" width="640px" top="6vh">
      <el-form label-width="100px">
        <el-form-item label="活动名称" required>
          <el-input v-model="form.name" placeholder="如：年夜饭、宴席" />
        </el-form-item>
        <el-form-item label="筛选标识" required>
          <el-input v-model="form.tag" placeholder="与商品「所属活动」一致，如：宴席" />
          <div class="hint block">商品所属活动选这个值后，会出现在本活动页</div>
        </el-form-item>
        <el-form-item v-if="!editing" label="活动 ID" required>
          <el-input v-model="form.id" placeholder="英文/数字，如 banquet" />
        </el-form-item>
        <el-form-item label="活动轮播">
          <ImageListField v-model="banners" folder="activities" />
          <div class="hint block">留空则用商品封面顶上</div>
        </el-form-item>
        <el-form-item label="开放起">
          <el-input v-model="form.open_start" placeholder="YYYY-MM-DD，可选" />
        </el-form-item>
        <el-form-item label="开放止">
          <el-input v-model="form.open_end" placeholder="YYYY-MM-DD，可选" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort" :min="0" />
          <span class="hint">数字越小越靠前</span>
        </el-form-item>
        <el-form-item label="是否启用">
          <el-switch v-model="form.enabled" active-text="启用" inactive-text="停用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" :loading="busy('save')" @click="onSave">保存</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../api/http'
import { useLock } from '../composables/useLock'
import ImageListField from '../components/ImageListField.vue'

const { busy, run } = useLock()

const list = ref([])
const visible = ref(false)
const editing = ref(false)
const banners = ref([])
const form = reactive({
  id: '',
  name: '',
  tag: '',
  banners: [],
  open_start: '',
  open_end: '',
  sort: 0,
  enabled: true
})

function empty() {
  return {
    id: '',
    name: '',
    tag: '',
    banners: [],
    open_start: '',
    open_end: '',
    sort: 0,
    enabled: true
  }
}

function genId() {
  return `act${Date.now().toString(36)}`
}

async function load() {
  list.value = (await http.get('/activities')) || []
}

function openEdit(row) {
  editing.value = !!row
  Object.assign(form, empty(), row || {})
  if (!editing.value) form.id = genId()
  banners.value = [...(form.banners || [])]
  visible.value = true
}

async function onSave() {
  return run('save', async () => {
    if (!form.name?.trim()) {
      ElMessage.warning('请填写活动名称')
      return
    }
    const tag = (form.tag || form.name || '').trim()
    if (!tag) {
      ElMessage.warning('请填写筛选标识')
      return
    }
    if (!editing.value && !form.id?.trim()) {
      ElMessage.warning('请填写活动 ID')
      return
    }
    const payload = {
      ...form,
      id: editing.value ? form.id : form.id.trim(),
      name: form.name.trim(),
      tag,
      banners: banners.value.filter(Boolean)
    }
    if (editing.value) await http.put(`/activities/${form.id}`, payload)
    else await http.post('/activities', payload)
    ElMessage.success('已保存')
    visible.value = false
    load()
  })
}

async function onRemove(row) {
  return run('remove-' + row.id, async () => {
    await ElMessageBox.confirm(`确认删除活动「${row.name}」？`, '提示')
    await http.delete(`/activities/${row.id}`)
    load()
  })
}

onMounted(load)
</script>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.tip {
  color: #888;
  font-size: 13px;
}
.hint {
  margin-left: 8px;
  color: #999;
  font-size: 12px;
}
.hint.block {
  display: block;
  margin: 6px 0 0;
}
</style>
