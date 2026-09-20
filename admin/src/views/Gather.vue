<template>
  <div>
    <el-card class="mb">
      <template #header>
        <div class="head">
          <span>分类（小程序顶部 Tab）</span>
          <el-button type="primary" size="small" @click="openTab()">新增分类</el-button>
        </div>
      </template>
      <el-table :data="tabs" size="small">
        <el-table-column prop="name" label="分类名称" min-width="140" />
        <el-table-column label="显示已购人数" width="120">
          <template #default="{ row }">{{ row.show_sold ? '显示' : '不显示' }}</template>
        </el-table-column>
        <el-table-column prop="sort" label="排序" width="80" />
        <el-table-column label="是否显示" width="100">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'info'" size="small">
              {{ row.enabled ? '显示' : '隐藏' }}
            </el-tag>
          </template>
        </el-table-column>
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
        <el-table-column label="封面" width="88">
          <template #default="{ row }">
            <el-image v-if="row.cover" :src="row.cover" style="width: 64px; height: 48px" fit="cover" />
            <span v-else class="muted">暂无</span>
          </template>
        </el-table-column>
        <el-table-column label="所属分类" width="110">
          <template #default="{ row }">{{ tabName(row.tab) }}</template>
        </el-table-column>
        <el-table-column prop="title" label="商品标题" min-width="220" show-overflow-tooltip />
        <el-table-column prop="price" label="现价" width="90" />
        <el-table-column prop="origin_price" label="原价" width="90" />
        <el-table-column prop="sold_text" label="已购文案" width="120" show-overflow-tooltip />
        <el-table-column label="是否上架" width="100">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'info'" size="small">
              {{ row.enabled ? '上架' : '下架' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openProduct(row)">编辑</el-button>
            <el-button link type="danger" @click="removeProduct(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="tabVisible" :title="tabForm.id ? '编辑分类' : '新增分类'" width="440px">
      <el-form label-width="110px">
        <el-form-item label="分类名称" required>
          <el-input v-model="tabForm.name" placeholder="例如：聚一天、招牌菜" />
        </el-form-item>
        <el-form-item label="显示已购人数">
          <el-switch v-model="tabForm.show_sold" active-text="显示" inactive-text="不显示" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="tabForm.sort" :min="0" />
          <span class="hint">数字越小越靠前</span>
        </el-form-item>
        <el-form-item label="是否显示">
          <el-switch v-model="tabForm.enabled" active-text="显示" inactive-text="隐藏" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="tabVisible = false">取消</el-button>
        <el-button type="primary" @click="saveTab">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="productVisible" :title="productEditing ? '编辑商品' : '新增商品'" width="640px">
      <el-form label-width="100px">
        <el-form-item label="所属分类" required>
          <el-select v-model="productForm.tab" placeholder="请选择分类" style="width: 100%">
            <el-option v-for="t in tabs" :key="t.key" :label="t.name" :value="t.key" />
          </el-select>
        </el-form-item>
        <el-form-item label="商品标题" required>
          <el-input v-model="productForm.title" placeholder="小程序列表展示的标题" />
        </el-form-item>
        <el-form-item label="封面图">
          <ImageField v-model="productForm.cover" folder="gather" />
        </el-form-item>
        <el-form-item label="关联门店">
          <el-select
            v-model="productForm.detail_id"
            clearable
            filterable
            placeholder="跳转详情时关联的门店，可选"
            style="width: 100%"
          >
            <el-option v-for="s in stores" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="角标文案">
          <el-input v-model="productForm.tag" placeholder="例如：招牌、家宴，可选" />
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="tagsText" placeholder="多个用逗号分隔，例如：近地铁,包厢" />
        </el-form-item>
        <el-form-item label="已购文案">
          <el-input v-model="productForm.sold_text" placeholder="例如：1.2万+人已购" />
        </el-form-item>
        <el-form-item label="现价">
          <el-input-number v-model="productForm.price" :min="0" :precision="0" />
        </el-form-item>
        <el-form-item label="原价">
          <el-input-number v-model="productForm.origin_price" :min="0" :precision="0" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="productForm.sort" :min="0" />
          <span class="hint">数字越小越靠前</span>
        </el-form-item>
        <el-form-item label="是否上架">
          <el-switch v-model="productForm.enabled" active-text="上架" inactive-text="下架" />
        </el-form-item>
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
const stores = ref([])
const tabVisible = ref(false)
const productVisible = ref(false)
const productEditing = ref(false)
const tagsText = ref('')
const tabForm = reactive({ id: null, key: '', name: '', show_sold: true, sort: 0, enabled: true })
const productForm = reactive({
  id: '',
  tab: '',
  detail_id: '',
  cover: '',
  title: '',
  tag: '',
  tags: [],
  sold_text: '',
  price: 0,
  origin_price: 0,
  sort: 0,
  enabled: true
})

function tabName(key) {
  return tabs.value.find((t) => t.key === key)?.name || key || '未分类'
}

function genKey() {
  return `t${Date.now().toString(36)}`
}

function genProductId() {
  return `g${Date.now().toString(36)}`
}

async function load() {
  const [tabList, productList, storeList] = await Promise.all([
    http.get('/gather/tabs'),
    http.get('/gather/products'),
    http.get('/stores')
  ])
  tabs.value = tabList
  products.value = productList
  stores.value = storeList || []
}

function openTab(row) {
  Object.assign(tabForm, { id: null, key: '', name: '', show_sold: true, sort: 0, enabled: true }, row || {})
  tabVisible.value = true
}

async function saveTab() {
  if (!tabForm.name?.trim()) {
    ElMessage.warning('请填写分类名称')
    return
  }
  const payload = {
    key: tabForm.id ? tabForm.key : (tabForm.key || genKey()),
    name: tabForm.name.trim(),
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
  await ElMessageBox.confirm(`确认删除分类「${row.name}」？`, '提示')
  await http.delete(`/gather/tabs/${row.id}`)
  load()
}

function openProduct(row) {
  productEditing.value = !!row
  const defaultTab = tabs.value[0]?.key || ''
  Object.assign(productForm, {
    id: '',
    tab: defaultTab,
    detail_id: '',
    cover: '',
    title: '',
    tag: '',
    tags: [],
    sold_text: '',
    price: 0,
    origin_price: 0,
    sort: 0,
    enabled: true
  }, row || {})
  tagsText.value = (productForm.tags || []).join(',')
  productVisible.value = true
}

async function saveProduct() {
  if (!productForm.tab) {
    ElMessage.warning('请选择所属分类')
    return
  }
  if (!productForm.title?.trim()) {
    ElMessage.warning('请填写商品标题')
    return
  }
  const payload = {
    ...productForm,
    id: productEditing.value ? productForm.id : (productForm.id || genProductId()),
    title: productForm.title.trim(),
    detail_id: productForm.detail_id || '',
    tags: tagsText.value ? tagsText.value.split(/[,，]/).map((s) => s.trim()).filter(Boolean) : []
  }
  if (productEditing.value) await http.put(`/gather/products/${productForm.id}`, payload)
  else await http.post('/gather/products', payload)
  ElMessage.success('已保存')
  productVisible.value = false
  load()
}

async function removeProduct(row) {
  await ElMessageBox.confirm(`确认删除商品「${row.title}」？`, '提示')
  await http.delete(`/gather/products/${row.id}`)
  load()
}

onMounted(load)
</script>

<style scoped>
.mb { margin-bottom: 16px; }
.head { display: flex; justify-content: space-between; align-items: center; }
.hint { margin-left: 8px; color: #94a3b8; font-size: 12px; }
.muted { color: #94a3b8; font-size: 12px; }
</style>
