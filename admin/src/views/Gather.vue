<template>
  <div>
    <el-card>
      <el-tabs v-model="activePane">
        <el-tab-pane label="商品" name="products">
          <div class="pane-head">
            <p class="intro">每张卡片是独立商品：封面、套餐、销量各自维护。同一首页门店可挂多个主题。</p>
            <el-button type="primary" size="small" @click="openProduct()">新增商品</el-button>
          </div>
          <el-table :data="products" stripe>
            <el-table-column label="封面" width="88">
              <template #default="{ row }">
                <el-image v-if="row.cover" :src="row.cover" style="width: 64px; height: 48px" fit="cover" />
                <span v-else class="muted">暂无</span>
              </template>
            </el-table-column>
            <el-table-column prop="title" label="名称" min-width="200" show-overflow-tooltip />
            <el-table-column label="首页门店" width="120" show-overflow-tooltip>
              <template #default="{ row }">{{ storeName(row.detail_id) }}</template>
            </el-table-column>
            <el-table-column label="所属分类" width="100">
              <template #default="{ row }">{{ tabName(row.tab) }}</template>
            </el-table-column>
            <el-table-column label="所属地区" width="100">
              <template #default="{ row }">{{ regionName(row.region) }}</template>
            </el-table-column>
            <el-table-column prop="tag" label="角标" width="90" show-overflow-tooltip />
            <el-table-column label="起价" width="90">
              <template #default="{ row }">{{ row.price > 0 ? row.price : '—' }}</template>
            </el-table-column>
            <el-table-column label="套餐数" width="80">
              <template #default="{ row }">{{ (row.packages || []).length }}</template>
            </el-table-column>
            <el-table-column prop="sold_count" label="已购" width="80" />
            <el-table-column label="是否上架" width="90">
              <template #default="{ row }">
                <el-tag :type="row.enabled ? 'success' : 'info'" size="small">
                  {{ row.enabled ? '上架' : '下架' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="openProduct(row)">编辑</el-button>
                <el-button link type="warning" @click="openPackages(row)">套餐</el-button>
                <el-button link type="danger" :loading="busy('product-' + row.id)" @click="removeProduct(row)">删除</el-button>
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
              @current-change="loadProducts"
              @size-change="() => { page = 1; loadProducts() }"
            />
          </div>
        </el-tab-pane>

        <el-tab-pane label="分类" name="tabs">
          <div class="pane-head">
            <span class="pane-tip">对应小程序去哪聚顶部的分类 Tab</span>
            <el-button type="primary" size="small" @click="openTab()">新增分类</el-button>
          </div>
          <el-table :data="tabs" size="small" stripe>
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
                <el-button link type="danger" :loading="busy('tab-' + row.id)" @click="removeTab(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="地区" name="regions">
          <div class="pane-head">
            <span class="pane-tip">对应小程序去哪聚的地区筛选</span>
            <el-button type="primary" size="small" @click="openRegion()">新增地区</el-button>
          </div>
          <el-table :data="regions" size="small" stripe>
            <el-table-column prop="name" label="显示名称" min-width="140" />
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
                <el-button link type="primary" @click="openRegion(row)">编辑</el-button>
                <el-button link type="danger" :disabled="row.id === 'all'" :loading="busy('region-' + row.id)" @click="removeRegion(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-dialog v-model="regionVisible" :title="regionEditing ? '编辑地区' : '新增地区'" width="440px">
      <el-form label-width="110px">
        <el-form-item label="显示名称" required>
          <el-input v-model="regionForm.name" placeholder="例如：上海市" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="regionForm.sort" :min="0" />
          <span class="hint">数字越小越靠前</span>
        </el-form-item>
        <el-form-item label="是否显示">
          <el-switch v-model="regionForm.enabled" active-text="显示" inactive-text="隐藏" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="regionVisible = false">取消</el-button>
        <el-button type="primary" :loading="busy('save-region')" @click="saveRegion">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="tabVisible" :title="tabForm.id ? '编辑分类' : '新增分类'" width="440px">
      <el-form label-width="110px">
        <el-form-item label="分类名称" required>
          <el-input v-model="tabForm.name" placeholder="例如：聚一天、聚个餐" />
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
        <el-button type="primary" :loading="busy('save-tab')" @click="saveTab">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="productVisible" :title="productEditing ? '编辑商品' : '新增商品'" width="720px" top="5vh">
      <el-form label-width="100px">
        <el-form-item label="首页门店" required>
          <el-select v-model="productForm.detail_id" filterable placeholder="绑定包房库存的门店" style="width: 100%">
            <el-option v-for="s in stores" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
          <div class="hint block">同一门店可建多张主题商品，销量与套餐互不影响</div>
        </el-form-item>
        <el-form-item label="商品名称" required>
          <el-input v-model="productForm.title" placeholder="列表与详情展示名" />
        </el-form-item>
        <el-form-item label="封面">
          <ImageField v-model="productForm.cover" folder="gather" />
        </el-form-item>
        <el-form-item label="所属分类" required>
          <el-select v-model="productForm.tab" placeholder="请选择分类" style="width: 100%">
            <el-option v-for="t in tabs" :key="t.key" :label="t.name" :value="t.key" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属地区">
          <el-select v-model="productForm.region" clearable placeholder="不限（全国可见）" style="width: 100%">
            <el-option v-for="r in regionOptions" :key="r.id" :label="r.name" :value="r.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="角标文案">
          <el-input v-model="productForm.tag" placeholder="如：年夜饭、家宴；活动页按此筛选" />
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="tagsText" placeholder="多个用逗号分隔，例如：近地铁,包厢" />
        </el-form-item>
        <el-form-item label="现价">
          <el-input-number v-model="productForm.price" :min="0" :precision="2" :step="0.01" controls-position="right" class="num" />
          <div class="hint block">有套餐时列表「起」价取可用套餐最低价</div>
        </el-form-item>
        <el-form-item label="原价">
          <el-input-number v-model="productForm.origin_price" :min="0" :precision="2" :step="0.01" controls-position="right" class="num" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="productForm.address" placeholder="可选；留空则用首页门店地址" />
        </el-form-item>
        <el-form-item label="路线说明">
          <el-input v-model="productForm.route" type="textarea" :rows="2" placeholder="可选" />
        </el-form-item>
        <el-divider content-position="left">详情页轮播图</el-divider>
        <el-form-item label="轮播图">
          <ImageListField v-model="banners" folder="gather" />
        </el-form-item>
        <el-divider content-position="left">详情长图</el-divider>
        <el-form-item label="详情长图">
          <ImageListField v-model="detailImages" folder="gather" />
        </el-form-item>
        <el-form-item label="已购文案">
          <el-input v-model="productForm.sold_text" placeholder="留空则按真实销量「N人已购」" />
        </el-form-item>
        <el-form-item label="开放起">
          <el-input v-model="productForm.open_start" placeholder="YYYY-MM-DD，可选" />
        </el-form-item>
        <el-form-item label="开放止">
          <el-input v-model="productForm.open_end" placeholder="YYYY-MM-DD，可选" />
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
        <el-button type="primary" :loading="busy('save-product')" @click="saveProduct">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="pkgVisible"
      :title="pkgTitle ? `套餐管理 · ${pkgTitle}` : '套餐管理'"
      width="860px"
      top="4vh"
      destroy-on-close
    >
      <div class="pkg-head">
        <span class="pkg-tip">用户下单时选择的规格套餐，与商品基础信息分开维护</span>
        <el-button type="primary" size="small" @click="addPackage">新增套餐</el-button>
      </div>
      <div v-if="!packages.length" class="pkg-empty">暂无套餐，点击右上角新增</div>
      <div v-for="(pkg, idx) in packages" :key="pkg._key" class="pkg-card">
        <div class="pkg-card-head">
          <strong>套餐 {{ idx + 1 }}</strong>
          <el-button link type="danger" @click="removePackage(idx)">删除</el-button>
        </div>
        <el-form label-width="90px">
          <el-row :gutter="12">
            <el-col :span="12">
              <el-form-item label="展示名称">
                <el-input v-model="pkg.name" placeholder="套餐名称" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="宴席名称">
                <el-input v-model="pkg.meal" placeholder="宴席名称" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="用餐时段">
                <el-input v-model="pkg.time" placeholder="例如：10:00-14:00" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="可否预订">
                <el-switch v-model="pkg.bookable" active-text="可订" inactive-text="已满/停售" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="价格">
                <el-input-number v-model="pkg.price" :min="0" :precision="2" :step="0.01" controls-position="right" class="pkg-num" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="人数">
                <el-input-number v-model="pkg.people" :min="1" :precision="0" controls-position="right" class="pkg-num" />
              </el-form-item>
            </el-col>
            <el-col :span="24">
              <el-form-item label="套餐封面">
                <ImageField v-model="pkg.cover" folder="gather" />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="pkgVisible = false">取消</el-button>
        <el-button type="primary" :loading="pkgSaving" @click="onSavePackages">保存套餐</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../api/http'
import { usePager } from '../composables/usePager'
import { useLock } from '../composables/useLock'
import ImageField from '../components/ImageField.vue'
import ImageListField from '../components/ImageListField.vue'

const { busy, run } = useLock()

const activePane = ref('products')
const tabs = ref([])
const regions = ref([])
const products = ref([])
const stores = ref([])
const tabVisible = ref(false)
const regionVisible = ref(false)
const regionEditing = ref(false)
const productVisible = ref(false)
const productEditing = ref(false)
const tagsText = ref('')
const banners = ref([])
const detailImages = ref([])
const { page, pageSize, total, applyPage, pageParams } = usePager()
const tabForm = reactive({ id: null, key: '', name: '', show_sold: true, sort: 0, enabled: true })
const regionForm = reactive({ id: '', name: '', sort: 0, enabled: true })
const productForm = reactive({
  id: '',
  tab: '',
  region: '',
  detail_id: '',
  title: '',
  cover: '',
  tag: '',
  tags: [],
  sold_text: '',
  price: 0,
  origin_price: 0,
  address: '',
  route: '',
  lat: 0,
  lng: 0,
  banners: [],
  detail_images: [],
  recent_buy: {},
  packages: [],
  open_start: '',
  open_end: '',
  sort: 0,
  enabled: true
})

const pkgVisible = ref(false)
const pkgSaving = ref(false)
const pkgProductId = ref('')
const pkgTitle = ref('')
const pkgBasePrice = ref(0)
const pkgBaseCover = ref('')
const packages = ref([])
let pkgSeq = 1

const regionOptions = computed(() => regions.value.filter((r) => r.id !== 'all'))

function tabName(key) {
  return tabs.value.find((t) => t.key === key)?.name || key || '未分类'
}

function regionName(key) {
  if (!key) return '全国'
  return regions.value.find((r) => r.id === key)?.name || key
}

function storeName(id) {
  if (!id) return '—'
  return stores.value.find((s) => s.id === id)?.name || id
}

function genKey() {
  return `t${Date.now().toString(36)}`
}

function genProductId() {
  return `g${Date.now().toString(36)}`
}

function emptyProduct() {
  return {
    id: '',
    tab: tabs.value[0]?.key || '',
    region: '',
    detail_id: '',
    title: '',
    cover: '',
    tag: '',
    tags: [],
    sold_text: '',
    price: 0,
    origin_price: 0,
    address: '',
    route: '',
    lat: 0,
    lng: 0,
    banners: [],
    detail_images: [],
    recent_buy: {},
    packages: [],
    open_start: '',
    open_end: '',
    sort: 0,
    enabled: true
  }
}

function toPackageForm(p = {}) {
  return {
    _key: `k${pkgSeq++}`,
    id: p.id || pkgSeq,
    name: p.name || '',
    meal: p.meal || '',
    time: p.time || '',
    price: Number(p.price) || 0,
    people: Number(p.people) || 10,
    cover: p.cover || '',
    bookable: !p.disabled
  }
}

function serializePackages(rows) {
  return rows.map((p, i) => ({
    id: p.id || i + 1,
    name: (p.name || '').trim(),
    meal: (p.meal || '').trim(),
    time: (p.time || '').trim(),
    price: Number(p.price) || 0,
    people: Number(p.people) || 0,
    cover: p.cover || '',
    disabled: !p.bookable
  }))
}

function addPackage() {
  packages.value.push(
    toPackageForm({
      id: Date.now(),
      name: '',
      meal: '',
      time: '10:00-14:00',
      price: pkgBasePrice.value || 0,
      people: 10,
      cover: pkgBaseCover.value || '',
      disabled: false
    })
  )
}

function removePackage(idx) {
  packages.value.splice(idx, 1)
}

async function loadProducts() {
  const res = await http.get('/gather/products', { params: pageParams() })
  products.value = applyPage(res)
}

async function load() {
  const [tabList, regionList, storeList] = await Promise.all([
    http.get('/gather/tabs'),
    http.get('/gather/regions'),
    http.get('/stores')
  ])
  tabs.value = tabList
  regions.value = regionList || []
  stores.value = storeList || []
  await loadProducts()
}

function openRegion(row) {
  regionEditing.value = !!row
  Object.assign(regionForm, { id: '', name: '', sort: 0, enabled: true }, row || {})
  regionVisible.value = true
}

async function saveRegion() {
  return run('save-region', async () => {
    if (!regionForm.name?.trim()) {
      ElMessage.warning('请填写显示名称')
      return
    }
    if (!regionEditing.value) {
      regionForm.id = 'r' + Date.now()
    }
    const payload = {
      id: regionForm.id.trim(),
      name: regionForm.name.trim(),
      sort: regionForm.sort,
      enabled: regionForm.enabled
    }
    if (regionEditing.value) await http.put(`/gather/regions/${regionForm.id}`, payload)
    else await http.post('/gather/regions', payload)
    ElMessage.success('已保存')
    regionVisible.value = false
    load()
  })
}

async function removeRegion(row) {
  return run('region-' + row.id, async () => {
    await ElMessageBox.confirm(`确认删除地区「${row.name}」？`, '提示')
    await http.delete(`/gather/regions/${row.id}`)
    load()
  })
}

function openTab(row) {
  Object.assign(tabForm, { id: null, key: '', name: '', show_sold: true, sort: 0, enabled: true }, row || {})
  tabVisible.value = true
}

async function saveTab() {
  return run('save-tab', async () => {
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
  })
}

async function removeTab(row) {
  return run('tab-' + row.id, async () => {
    await ElMessageBox.confirm(`确认删除分类「${row.name}」？`, '提示')
    await http.delete(`/gather/tabs/${row.id}`)
    load()
  })
}

function openProduct(row) {
  productEditing.value = !!row
  Object.assign(productForm, emptyProduct(), row || {})
  tagsText.value = (productForm.tags || []).join(',')
  banners.value = [...(productForm.banners || [])]
  detailImages.value = [...(productForm.detail_images || [])]
  productVisible.value = true
}

function openPackages(row) {
  if (!row?.id) {
    ElMessage.warning('请先保存商品后再配置套餐')
    return
  }
  pkgProductId.value = row.id
  pkgTitle.value = row.title || ''
  pkgBasePrice.value = Number(row.price) || 0
  pkgBaseCover.value = row.cover || ''
  packages.value = (row.packages || []).map((p) => toPackageForm(p))
  pkgVisible.value = true
}

async function saveProduct() {
  return run('save-product', async () => {
    if (!productForm.detail_id) {
      ElMessage.warning('请选择关联首页门店')
      return
    }
    if (!productForm.title?.trim()) {
      ElMessage.warning('请填写商品名称')
      return
    }
    if (!productForm.tab) {
      ElMessage.warning('请选择所属分类')
      return
    }
    const existing = productEditing.value ? products.value.find((r) => r.id === productForm.id) : null
    const payload = {
      ...productForm,
      id: productEditing.value ? productForm.id : (productForm.id || genProductId()),
      title: productForm.title.trim(),
      region: productForm.region || '',
      tag: productForm.tag || '',
      sold_text: productForm.sold_text || '',
      banners: banners.value.filter(Boolean),
      detail_images: detailImages.value.filter(Boolean),
      packages: existing?.packages || productForm.packages || [],
      tags: tagsText.value ? tagsText.value.split(/[,，]/).map((s) => s.trim()).filter(Boolean) : []
    }
    if (productEditing.value) await http.put(`/gather/products/${productForm.id}`, payload)
    else await http.post('/gather/products', payload)
    ElMessage.success('已保存')
    productVisible.value = false
    loadProducts()
  })
}

async function onSavePackages() {
  if (pkgSaving.value) return
  const row = products.value.find((r) => r.id === pkgProductId.value)
  if (!row) {
    ElMessage.error('商品不存在或已删除')
    return
  }
  pkgSaving.value = true
  try {
    const payload = {
      ...row,
      packages: serializePackages(packages.value)
    }
    await http.put(`/gather/products/${row.id}`, payload)
    ElMessage.success('套餐已保存')
    pkgVisible.value = false
    loadProducts()
  } finally {
    pkgSaving.value = false
  }
}

async function removeProduct(row) {
  return run('product-' + row.id, async () => {
    await ElMessageBox.confirm(`确认删除商品「${row.title || row.id}」？`, '提示')
    await http.delete(`/gather/products/${row.id}`)
    loadProducts()
  })
}

onMounted(load)
</script>

<style scoped>
.pane-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}
.pane-tip {
  color: #888;
  font-size: 13px;
}
.intro {
  margin: 0;
  color: #888;
  font-size: 13px;
  line-height: 1.5;
  flex: 1;
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
.muted {
  color: #bbb;
  font-size: 12px;
}
.num {
  width: 168px;
}
.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
.pkg-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 0 0 12px;
}
.pkg-tip {
  color: #64748b;
  font-size: 13px;
}
.pkg-empty {
  padding: 24px;
  text-align: center;
  color: #94a3b8;
  background: #f8fafc;
  border-radius: 8px;
  margin-bottom: 12px;
}
.pkg-card {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 12px 12px 0;
  margin-bottom: 12px;
  background: #fafafa;
}
.pkg-card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.pkg-num {
  width: 168px;
}
</style>
