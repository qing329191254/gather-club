<template>
  <el-card>
    <div class="toolbar">
      <el-button type="primary" @click="openEdit()">新增商品</el-button>
    </div>
    <el-table :data="list" stripe>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="name" label="名称" min-width="180" />
      <el-table-column prop="cost" label="积分" width="90" />
      <el-table-column prop="stock" label="库存" width="90" />
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

    <el-dialog v-model="visible" :title="form.id ? '编辑商品' : '新增商品'" width="640px">
      <el-form label-width="90px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="封面"><el-input v-model="form.cover" /></el-form-item>
        <el-form-item label="积分"><el-input-number v-model="form.cost" :min="0" /></el-form-item>
        <el-form-item label="库存"><el-input-number v-model="form.stock" :min="0" /></el-form-item>
        <el-form-item label="使用说明"><el-input v-model="form.usage" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="有效期"><el-input v-model="form.valid" /></el-form-item>
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

const list = ref([])
const visible = ref(false)
const empty = () => ({ id: null, name: '', title: '', cover: '', cost: 0, usage: '', valid: '', stock: 999, sort: 0, enabled: true })
const form = reactive(empty())

async function load() {
  list.value = await http.get('/mall/goods')
}

function openEdit(row) {
  Object.assign(form, empty(), row || {})
  visible.value = true
}

async function onSave() {
  const payload = { ...form }
  delete payload.id
  if (form.id) await http.put(`/mall/goods/${form.id}`, payload)
  else await http.post('/mall/goods', payload)
  ElMessage.success('已保存')
  visible.value = false
  load()
}

async function onRemove(row) {
  await ElMessageBox.confirm('确认删除？', '提示')
  await http.delete(`/mall/goods/${row.id}`)
  load()
}

onMounted(load)
</script>

<style scoped>
.toolbar { margin-bottom: 12px; }
</style>
