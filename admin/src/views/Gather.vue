<template>
  <div>
    <el-card class="mb">
      <template #header>
        <div class="head">
          <span>分类 Tabs</span>
          <el-button type="primary" size="small" @click="openTab()">新增分类</el-button>
        </div>
      </template>
      <el-table :data="tabs" size="small">
        <el-table-column prop="key" label="Key" width="100" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="show_sold" label="显示已购" width="100">
          <template #default="{ row }">{{ row.show_sold ? '是' : '否' }}</template>
        </el-table-column>
        <el-table-column prop="sort" label="排序" width="80" />
        <el-table-column label="操作" width="140">
          <template #default="{ row }">
            <el-button link type="primary" @click="openTab(row)">编辑</el-button>
            <el-button link type="danger" @click="removeTab(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card>
      <template #header>
        <div class="head">
          <span>商品列表</span>
          <el-button type="primary" size="small" @click="openProduct()">新增商品</el-button>
        </div>
      </template>
      <el-table :data="products" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="tab" label="分类" width="90" />
        <el-table-column prop="title" label="标题" min-width="220" show-overflow-tooltip />
        <el-table-column prop="price" label="现价" width="90" />
        <el-table-column prop="origin_price" label="原价" width="90" />
        <el-table-column prop="sold_text" label="已购文案" width="120" />
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openProduct(row)">编辑</el-button>
            <el-button link type="danger" @click="removeProduct(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="tabVisible" title="分类" width="420px">
      <el-form label-width="90px">
        <el-form-item label="Key"><el-input v-model="tabForm.key" :disabled="!!tabForm.id" /></el-form-item>
        <el-form-item label="名称"><el-input v-model="tabForm.name" /></el-form-item>
        <el-form-item label="显示已购"><el-switch v-model="tabForm.show_sold" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="tabForm.sort" :min="0" /></el-form-item>
        <el-form-item label="启用"><el-switch v-model="tabForm.enabled" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="tabVisible = false">取消</el-button>
        <el-button type="primary" @click="saveTab">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="productVisible" title="商品" width="640px">
      <el-form label-width="90px">
        <el-form-item label="ID"><el-input v-model="productForm.id" :disabled="productEditing" /></el-form-item>
        <el-form-item label="分类">
          <el-select v-model="productForm.tab" style="width: 100%">
            <el-option v-for="t in tabs" :key="t.key" :label="t.name" :value="t.key" />
          </el-select>
        </el-form-item>
        <el-form-item label="标题"><el-input v-model="productForm.title" /></el-form-item>
        <el-form-item label="封面"><ImageField v-model="productForm.cover" folder="gather" /></el-form-item>
        <el-form-item label="详情门店"><el-input v-model="productForm.detail_id" placeholder="关联详情门店 ID，可选" /></el-form-item>
        <el-form-item label="标签"><el-input v-model="productForm.tag" /></el-form-item>
        <el-form-item label="多标签"><el-input v-model="tagsText" placeholder="逗号分隔" /></el-form-item>
        <el-form-item label="已购文案"><el-input v-model="productForm.sold_text" /></el-form-item>
        <el-form-item label="现价"><el-input-number v-model="productForm.price" :min="0" /></el-form-item>
        <el-form-item label="原价"><el-input-number v-model="productForm.origin_price" :min="0" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="productForm.sort" :min="0" /></el-form-item>
        <el-form-item label="启用"><el-switch v-model="productForm.enabled" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="productVisible = false">取消</el-button>
        <el-button type="primary" @click="saveProduct">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../api/http'
import ImageField from '../components/ImageField.vue'

const tabs = ref([])
const products = ref([])
const tabVisible = ref(false)
const productVisible = ref(false)
const productEditing = ref(false)
const tagsText = ref('')
const tabForm = reactive({ id: null, key: '', name: '', show_sold: true, sort: 0, enabled: true })
const productForm = reactive({
  id: '', tab: 'day', detail_id: '', cover: '', title: '', tag: '', tags: [],
  sold_text: '', price: 0, origin_price: 0, sort: 0, enabled: true
})

async function load() {
  tabs.value = await http.get('/gather/tabs')
  products.value = await http.get('/gather/products')
}

function openTab(row) {
  Object.assign(tabForm, { id: null, key: '', name: '', show_sold: true, sort: 0, enabled: true }, row || {})
  tabVisible.value = true
}

async function saveTab() {
  const payload = {
    key: tabForm.key,
    name: tabForm.name,
    show_sold: tabForm.show_sold,
    sort: tabForm.sort,
    enabled: tabForm.enabled
  }
  if (tabForm.id) await http.put(`/gather/tabs/${tabForm.id}`, payload)
  else await http.post('/gather/tabs', payload)
  ElMessage.success('已保存')
  tabVisible.value = false
  load()
}

async function removeTab(row) {
  await ElMessageBox.confirm('确认删除分类？', '提示')
  await http.delete(`/gather/tabs/${row.id}`)
  load()
}

function openProduct(row) {
  productEditing.value = !!row
  Object.assign(productForm, {
    id: '', tab: 'day', detail_id: '', cover: '', title: '', tag: '', tags: [],
    sold_text: '', price: 0, origin_price: 0, sort: 0, enabled: true
  }, row || {})
  tagsText.value = (productForm.tags || []).join(',')
  productVisible.value = true
}

async function saveProduct() {
  const payload = {
    ...productForm,
    tags: tagsText.value ? tagsText.value.split(/[,，]/).map((s) => s.trim()).filter(Boolean) : []
  }
  if (productEditing.value) await http.put(`/gather/products/${productForm.id}`, payload)
  else await http.post('/gather/products', payload)
  ElMessage.success('已保存')
  productVisible.value = false
  load()
}

async function removeProduct(row) {
  await ElMessageBox.confirm('确认删除商品？', '提示')
  await http.delete(`/gather/products/${row.id}`)
  load()
}

onMounted(load)
</script>

<style scoped>
.mb { margin-bottom: 16px; }
.head { display: flex; justify-content: space-between; align-items: center; }
</style>
