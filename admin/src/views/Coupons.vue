<template>
  <el-card>
    <div class="toolbar">
      <el-button type="primary" @click="openEdit()">新增优惠券</el-button>
    </div>
    <el-table :data="list" stripe>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="name" label="名称" min-width="160" />
      <el-table-column prop="amount" label="面额" width="90" />
      <el-table-column prop="condition" label="条件" min-width="140" />
      <el-table-column prop="expire" label="有效期" min-width="140" />
      <el-table-column prop="total" label="总量" width="80" />
      <el-table-column prop="claimed" label="已领" width="80" />
      <el-table-column label="操作" width="140">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="onRemove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="visible" title="优惠券" width="520px">
      <el-form label-width="90px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="面额"><el-input-number v-model="form.amount" :min="0" /></el-form-item>
        <el-form-item label="条件"><el-input v-model="form.condition" /></el-form-item>
        <el-form-item label="有效期"><el-input v-model="form.expire" /></el-form-item>
        <el-form-item label="总量"><el-input-number v-model="form.total" :min="0" /></el-form-item>
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
const form = reactive({ id: null, name: '', amount: 0, condition: '无门槛', expire: '', total: 0, enabled: true })

async function load() {
  list.value = await http.get('/coupons')
}

function openEdit(row) {
  Object.assign(form, { id: null, name: '', amount: 0, condition: '无门槛', expire: '', total: 0, enabled: true }, row || {})
  visible.value = true
}

async function onSave() {
  const payload = {
    name: form.name,
    amount: form.amount,
    condition: form.condition,
    expire: form.expire,
    total: form.total,
    enabled: form.enabled
  }
  if (form.id) await http.put(`/coupons/${form.id}`, payload)
  else await http.post('/coupons', payload)
  ElMessage.success('已保存')
  visible.value = false
  load()
}

async function onRemove(row) {
  await ElMessageBox.confirm('确认删除？', '提示')
  await http.delete(`/coupons/${row.id}`)
  load()
}

onMounted(load)
</script>

<style scoped>
.toolbar { margin-bottom: 12px; }
</style>
