<template>
  <el-card>
    <div class="toolbar">
      <el-input v-model="storeId" placeholder="门店ID" style="width: 140px" clearable />
      <el-input v-model="date" placeholder="日期 YYYY-MM-DD" style="width: 160px" clearable />
      <el-button @click="load">查询</el-button>
      <el-button type="primary" @click="openEdit()">新增/覆盖库存</el-button>
    </div>
    <el-table :data="list" stripe>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="store_id" label="门店" width="110" />
      <el-table-column prop="date" label="日期" width="120" />
      <el-table-column prop="slot" label="时段" width="90" />
      <el-table-column prop="capacity" label="总库存" width="90" />
      <el-table-column prop="booked" label="已订" width="90" />
      <el-table-column label="剩余" width="90">
        <template #default="{ row }">{{ Math.max(0, row.capacity - row.booked) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="onRemove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="visible" title="包房库存" width="480px">
      <el-form label-width="90px">
        <el-form-item label="门店ID"><el-input v-model="form.store_id" /></el-form-item>
        <el-form-item label="日期"><el-input v-model="form.date" placeholder="2026-09-20" /></el-form-item>
        <el-form-item label="时段">
          <el-select v-model="form.slot" style="width: 100%">
            <el-option label="午市 lunch" value="lunch" />
            <el-option label="晚市 dinner" value="dinner" />
          </el-select>
        </el-form-item>
        <el-form-item label="总库存"><el-input-number v-model="form.capacity" :min="0" /></el-form-item>
        <el-form-item label="已订"><el-input-number v-model="form.booked" :min="0" /></el-form-item>
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
const storeId = ref('')
const date = ref('')
const visible = ref(false)
const form = reactive({ store_id: '', date: '', slot: 'dinner', capacity: 4, booked: 0 })

async function load() {
  list.value = await http.get('/rooms', {
    params: { store_id: storeId.value || undefined, date: date.value || undefined }
  })
}

function openEdit(row) {
  Object.assign(form, { store_id: '', date: '', slot: 'dinner', capacity: 4, booked: 0 }, row || {})
  visible.value = true
}

async function onSave() {
  await http.post('/rooms', form)
  ElMessage.success('已保存')
  visible.value = false
  load()
}

async function onRemove(row) {
  await ElMessageBox.confirm('确认删除？', '提示')
  await http.delete(`/rooms/${row.id}`)
  load()
}

onMounted(load)
</script>

<style scoped>
.toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
}
</style>
