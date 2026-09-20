<template>
  <el-card>
    <div class="toolbar">
      <el-select v-model="storeId" placeholder="全部门店" clearable filterable style="width: 220px" @change="onSearch">
        <el-option v-for="s in stores" :key="s.id" :label="s.name" :value="s.id" />
      </el-select>
      <el-date-picker
        v-model="date"
        type="date"
        value-format="YYYY-MM-DD"
        placeholder="选择日期"
        clearable
        style="width: 180px"
        @change="onSearch"
      />
      <el-button @click="onSearch">查询</el-button>
      <el-button type="primary" @click="openEdit()">新增/覆盖库存</el-button>
    </div>
    <el-table :data="list" stripe>
      <el-table-column label="门店" min-width="180">
        <template #default="{ row }">{{ storeName(row.store_id) }}</template>
      </el-table-column>
      <el-table-column prop="date" label="日期" width="120" />
      <el-table-column label="时段" width="90">
        <template #default="{ row }">{{ slotLabel(row.slot) }}</template>
      </el-table-column>
      <el-table-column prop="capacity" label="总库存" width="90" />
      <el-table-column prop="booked" label="已订" width="90" />
      <el-table-column label="剩余" width="90">
        <template #default="{ row }">{{ Math.max(0, row.capacity - row.booked) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="onRemove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div class="pager">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        background
        @current-change="load"
        @size-change="onSearch"
      />
    </div>

    <el-dialog v-model="visible" :title="editing ? '编辑库存' : '新增库存'" width="480px">
      <el-form label-width="90px">
        <el-form-item label="门店" required>
          <el-select v-model="form.store_id" filterable placeholder="请选择门店" style="width: 100%">
            <el-option v-for="s in stores" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期" required>
          <el-date-picker
            v-model="form.date"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="选择日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="时段">
          <el-select v-model="form.slot" style="width: 100%">
            <el-option label="午市" value="lunch" />
            <el-option label="晚市" value="dinner" />
          </el-select>
        </el-form-item>
        <el-form-item label="总库存">
          <el-input-number v-model="form.capacity" :min="0" />
        </el-form-item>
        <el-form-item label="已订">
          <el-input-number v-model="form.booked" :min="0" />
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
import { usePager } from '../composables/usePager'

const list = ref([])
const stores = ref([])
const storeId = ref('')
const date = ref('')
const visible = ref(false)
const editing = ref(false)
const form = reactive({ store_id: '', date: '', slot: 'dinner', capacity: 4, booked: 0 })
const { page, pageSize, total, applyPage, resetPage, pageParams } = usePager()

function storeName(id) {
  return stores.value.find((s) => s.id === id)?.name || id || '—'
}

function slotLabel(slot) {
  if (slot === 'lunch') return '午市'
  if (slot === 'dinner') return '晚市'
  return slot || '—'
}

async function loadStores() {
  stores.value = (await http.get('/stores')) || []
}

async function load() {
  const res = await http.get('/rooms', {
    params: pageParams({
      store_id: storeId.value || undefined,
      date: date.value || undefined
    })
  })
  list.value = applyPage(res)
}

function onSearch() {
  if (!resetPage()) load()
}

function openEdit(row) {
  editing.value = !!row
  Object.assign(form, { store_id: '', date: '', slot: 'dinner', capacity: 4, booked: 0 }, row || {})
  visible.value = true
}

async function onSave() {
  if (!form.store_id) {
    ElMessage.warning('请选择门店')
    return
  }
  if (!form.date) {
    ElMessage.warning('请选择日期')
    return
  }
  await http.post('/rooms', form)
  ElMessage.success('已保存')
  visible.value = false
  load()
}

async function onRemove(row) {
  await ElMessageBox.confirm(`确认删除「${storeName(row.store_id)} ${row.date} ${slotLabel(row.slot)}」库存？`, '提示')
  await http.delete(`/rooms/${row.id}`)
  load()
}

onMounted(async () => {
  await loadStores()
  load()
})
</script>

<style scoped>
.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 12px;
  align-items: center;
}
.pager {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
