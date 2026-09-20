<template>
  <el-card>
    <div class="toolbar">
      <el-button type="primary" @click="openEdit()">新增轮播</el-button>
    </div>
    <el-table :data="list" stripe>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column label="图片" width="120">
        <template #default="{ row }">
          <el-image :src="row.image" style="width: 80px; height: 40px" fit="cover" />
        </template>
      </el-table-column>
      <el-table-column prop="image" label="图片地址" min-width="180" />
      <el-table-column prop="link" label="跳转链接" min-width="160" />
      <el-table-column prop="sort" label="排序" width="80" />
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

    <el-dialog v-model="visible" :title="form.id ? '编辑轮播' : '新增轮播'" width="520px">
      <el-form label-width="90px">
        <el-form-item label="图片">
          <ImageField v-model="form.image" folder="banners" />
        </el-form-item>
        <el-form-item label="跳转链接"><el-input v-model="form.link" placeholder="小程序页面路径" /></el-form-item>
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
import ImageField from '../components/ImageField.vue'

const list = ref([])
const visible = ref(false)
const form = reactive({ id: null, image: '', link: '', sort: 0, enabled: true })

async function load() {
  list.value = await http.get('/banners')
}

function openEdit(row) {
  Object.assign(form, row || { id: null, image: '', link: '', sort: 0, enabled: true })
  visible.value = true
}

async function onSave() {
  const payload = { image: form.image, link: form.link, sort: form.sort, enabled: form.enabled }
  if (form.id) await http.put(`/banners/${form.id}`, payload)
  else await http.post('/banners', payload)
  ElMessage.success('已保存')
  visible.value = false
  load()
}

async function onRemove(row) {
  await ElMessageBox.confirm('确认删除？', '提示')
  await http.delete(`/banners/${row.id}`)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<style scoped>
.toolbar {
  margin-bottom: 12px;
}
</style>
