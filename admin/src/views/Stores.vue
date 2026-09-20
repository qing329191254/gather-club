<template>
  <el-card>
    <div class="toolbar">
      <el-button type="primary" @click="openEdit()">新增门店</el-button>
    </div>
    <el-table :data="list" stripe>
      <el-table-column label="封面" width="100">
        <template #default="{ row }">
          <el-image v-if="row.cover" :src="row.cover" style="width: 72px; height: 48px" fit="cover" />
          <span v-else class="muted">暂无</span>
        </template>
      </el-table-column>
      <el-table-column prop="name" label="门店名称" min-width="180" />
      <el-table-column prop="address" label="地址" min-width="220" show-overflow-tooltip />
      <el-table-column prop="phone" label="电话" width="130" />
      <el-table-column prop="sort" label="排序" width="70" />
      <el-table-column label="是否显示" width="100">
        <template #default="{ row }">
          <el-tag :type="row.enabled ? 'success' : 'info'">{{ row.enabled ? '显示' : '隐藏' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" :loading="busy('remove-' + row.id)" @click="onRemove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="visible" :title="editing ? '编辑门店' : '新增门店'" width="640px">
      <el-form label-width="90px">
        <el-form-item label="门店名称" required>
          <el-input v-model="form.name" placeholder="例如：天天俱乐部上海世博店" />
        </el-form-item>
        <el-form-item label="封面图">
          <ImageField v-model="form.cover" folder="stores" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="form.address" placeholder="门店详细地址" />
        </el-form-item>
        <el-form-item label="路线说明">
          <el-input v-model="form.route" type="textarea" :rows="3" placeholder="怎么走、地铁公交等说明，可选" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="form.phone" placeholder="门店联系电话" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort" :min="0" />
          <span class="hint">数字越小越靠前</span>
        </el-form-item>
        <el-form-item label="是否显示">
          <el-switch v-model="form.enabled" active-text="显示" inactive-text="隐藏" />
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
import ImageField from '../components/ImageField.vue'

const { busy, run } = useLock()

const list = ref([])
const visible = ref(false)
const editing = ref(false)
const empty = () => ({
  id: '',
  name: '',
  cover: '',
  address: '',
  route: '',
  phone: '',
  lat: 0,
  lng: 0,
  sort: 0,
  enabled: true
})
const form = reactive(empty())

async function load() {
  list.value = await http.get('/stores')
}

function openEdit(row) {
  editing.value = !!row
  Object.assign(form, empty(), row || {})
  visible.value = true
}

async function onSave() {
  return run('save', async () => {
  if (!(form.name || '').trim()) {
    ElMessage.warning('请填写门店名称')
    return
  }
  const payload = {
    id: form.id || '',
    name: form.name.trim(),
    cover: form.cover || '',
    address: form.address || '',
    route: form.route || '',
    phone: form.phone || '',
    lat: form.lat || 0,
    lng: form.lng || 0,
    sort: form.sort || 0,
    enabled: !!form.enabled
  }
  if (editing.value) await http.put(`/stores/${form.id}`, payload)
  else await http.post('/stores', payload)
  ElMessage.success('已保存')
  visible.value = false
  load()
  })
}

async function onRemove(row) {
  return run('remove-' + row.id, async () => {
  await ElMessageBox.confirm(`确认删除门店「${row.name}」？`, '提示')
  await http.delete(`/stores/${row.id}`)
  ElMessage.success('已删除')
  load()
  })
}

onMounted(load)
</script>

<style scoped>
.toolbar {
  margin-bottom: 12px;
}
.hint {
  margin-left: 12px;
  color: #94a3b8;
  font-size: 13px;
}
.muted {
  color: #94a3b8;
  font-size: 13px;
}
</style>
