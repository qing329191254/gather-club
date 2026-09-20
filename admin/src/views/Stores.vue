<template>
  <el-card>
    <div class="toolbar">
      <el-button type="primary" @click="openEdit()">新增门店</el-button>
    </div>
    <el-table :data="list" stripe>
      <el-table-column prop="id" label="ID" width="110" />
      <el-table-column prop="name" label="名称" min-width="180" />
      <el-table-column prop="address" label="地址" min-width="220" show-overflow-tooltip />
      <el-table-column prop="phone" label="电话" width="120" />
      <el-table-column prop="sort" label="排序" width="70" />
      <el-table-column label="启用" width="80">
        <template #default="{ row }">
          <el-tag :type="row.enabled ? 'success' : 'info'">{{ row.enabled ? '是' : '否' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="onRemove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="visible" :title="editing ? '编辑门店' : '新增门店'" width="640px">
      <el-form label-width="90px">
        <el-form-item label="门店ID"><el-input v-model="form.id" :disabled="editing" placeholder="门店唯一标识" /></el-form-item>
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="封面"><el-input v-model="form.cover" /></el-form-item>
        <el-form-item label="地址"><el-input v-model="form.address" /></el-form-item>
        <el-form-item label="路线"><el-input v-model="form.route" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="电话"><el-input v-model="form.phone" /></el-form-item>
        <el-form-item label="纬度"><el-input-number v-model="form.lat" :step="0.0001" /></el-form-item>
        <el-form-item label="经度"><el-input-number v-model="form.lng" :step="0.0001" /></el-form-item>
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
const editing = ref(false)
const empty = () => ({ id: '', name: '', cover: '', address: '', route: '', phone: '', lat: 0, lng: 0, sort: 0, enabled: true })
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
  if (editing.value) await http.put(`/stores/${form.id}`, form)
  else await http.post('/stores', form)
  ElMessage.success('已保存')
  visible.value = false
  load()
}

async function onRemove(row) {
  await ElMessageBox.confirm('确认删除该门店？', '提示')
  await http.delete(`/stores/${row.id}`)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<style scoped>
.toolbar { margin-bottom: 12px; }
</style>
