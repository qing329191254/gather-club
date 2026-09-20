<template>
  <el-card>
    <div class="toolbar">
      <el-button type="primary" @click="openEdit()">新增专题门店</el-button>
    </div>
    <el-table :data="list" stripe>
      <el-table-column label="封面" width="100">
        <template #default="{ row }">
          <el-image v-if="row.cover" :src="row.cover" style="width: 72px; height: 48px" fit="cover" />
          <span v-else class="muted">暂无</span>
        </template>
      </el-table-column>
      <el-table-column prop="name" label="名称" min-width="220" show-overflow-tooltip />
      <el-table-column prop="price" label="价格" width="90" />
      <el-table-column prop="address" label="地址" min-width="180" show-overflow-tooltip />
      <el-table-column prop="open_start" label="开放起" width="110" />
      <el-table-column prop="open_end" label="开放止" width="110" />
      <el-table-column label="是否上架" width="100">
        <template #default="{ row }">
          <el-tag :type="row.enabled ? 'success' : 'info'" size="small">
            {{ row.enabled ? '上架' : '下架' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="onRemove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="visible" :title="editing ? '编辑专题门店' : '新增专题门店'" width="820px" top="5vh">
      <el-form label-width="100px">
        <el-form-item label="名称" required>
          <el-input v-model="form.name" placeholder="例如：上海莘庄店·春节家宴 / 商务午宴" />
        </el-form-item>
        <el-form-item label="封面">
          <ImageField v-model="form.cover" folder="nye" />
        </el-form-item>
        <el-form-item label="现价">
          <el-input-number v-model="form.price" :min="0" :precision="0" />
        </el-form-item>
        <el-form-item label="原价">
          <el-input-number v-model="form.origin_price" :min="0" :precision="0" />
        </el-form-item>
        <el-form-item label="角标文案">
          <el-input v-model="form.tag" placeholder="例如：家宴、商务宴，可自定义" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="form.address" placeholder="门店详细地址" />
        </el-form-item>
        <el-form-item label="路线说明">
          <el-input v-model="form.route" type="textarea" :rows="2" placeholder="怎么走、地铁公交等，可选" />
        </el-form-item>

        <el-divider content-position="left">详情页轮播图</el-divider>
        <el-form-item label="轮播图">
          <ImageListField v-model="banners" folder="nye" />
        </el-form-item>

        <el-divider content-position="left">详情长图</el-divider>
        <el-form-item label="详情长图">
          <ImageListField v-model="detailImages" folder="nye" />
        </el-form-item>

        <el-divider content-position="left">套餐列表</el-divider>
        <div class="pkg-head">
          <span class="pkg-tip">用户选规格时看到的套餐，可逐条添加</span>
          <el-button type="primary" size="small" @click="addPackage">新增套餐</el-button>
        </div>
        <div v-if="!packages.length" class="pkg-empty">暂无套餐，点击右上角新增</div>
        <div v-for="(pkg, idx) in packages" :key="pkg._key" class="pkg-card">
          <div class="pkg-card-head">
            <strong>套餐 {{ idx + 1 }}</strong>
            <el-button link type="danger" @click="removePackage(idx)">删除</el-button>
          </div>
          <el-row :gutter="12">
            <el-col :span="12">
              <el-form-item label="展示名称">
                <el-input v-model="pkg.name" placeholder="例如：喜气羊羊宴 (10-12人) 午市大厅" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="宴席名称">
                <el-input v-model="pkg.meal" placeholder="例如：喜气羊羊宴" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="用餐时段">
                <el-input v-model="pkg.time" placeholder="例如：10:00-14:00" />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="价格">
                <el-input-number v-model="pkg.price" :min="0" :precision="0" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="人数">
                <el-input-number v-model="pkg.people" :min="1" :precision="0" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="套餐封面">
                <ImageField v-model="pkg.cover" folder="nye" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="可否预订">
                <el-switch v-model="pkg.bookable" active-text="可订" inactive-text="已满/停售" />
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <el-divider />
        <el-form-item label="开放起">
          <el-input v-model="form.open_start" placeholder="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="开放止">
          <el-input v-model="form.open_end" placeholder="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort" :min="0" />
          <span class="hint">数字越小越靠前</span>
        </el-form-item>
        <el-form-item label="是否上架">
          <el-switch v-model="form.enabled" active-text="上架" inactive-text="下架" />
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
import ImageField from '../components/ImageField.vue'
import ImageListField from '../components/ImageListField.vue'

const list = ref([])
const visible = ref(false)
const editing = ref(false)
const banners = ref([])
const detailImages = ref([])
const packages = ref([])
let pkgSeq = 1

const empty = () => ({
  id: '',
  name: '',
  cover: '',
  price: 0,
  origin_price: 0,
  tag: '宴会',
  address: '',
  route: '',
  lat: 0,
  lng: 0,
  banners: [],
  detail_images: [],
  recent_buy: {},
  packages: [],
  open_start: '2027-02-05',
  open_end: '2027-02-12',
  sort: 0,
  enabled: true
})
const form = reactive(empty())

function genId() {
  return `nye${Date.now().toString(36)}`
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

function addPackage() {
  packages.value.push(
    toPackageForm({
      id: Date.now(),
      name: '',
      meal: '',
      time: '10:00-14:00',
      price: form.price || 0,
      people: 10,
      cover: form.cover || '',
      disabled: false
    })
  )
}

function removePackage(idx) {
  packages.value.splice(idx, 1)
}

async function load() {
  list.value = await http.get('/nye')
}

function openEdit(row) {
  editing.value = !!row
  Object.assign(form, empty(), row || {})
  banners.value = [...(form.banners || [])]
  detailImages.value = [...(form.detail_images || [])]
  packages.value = (form.packages || []).map((p) => toPackageForm(p))
  visible.value = true
}

async function onSave() {
  if (!form.name?.trim()) {
    ElMessage.warning('请填写名称')
    return
  }
  const payload = {
    ...form,
    id: editing.value ? form.id : form.id || genId(),
    name: form.name.trim(),
    banners: banners.value.filter(Boolean),
    detail_images: detailImages.value.filter(Boolean),
    packages: packages.value.map((p, i) => ({
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
  if (editing.value) await http.put(`/nye/${form.id}`, payload)
  else await http.post('/nye', payload)
  ElMessage.success('已保存')
  visible.value = false
  load()
}

async function onRemove(row) {
  await ElMessageBox.confirm(`确认删除「${row.name}」？`, '提示')
  await http.delete(`/nye/${row.id}`)
  load()
}

onMounted(load)
</script>

<style scoped>
.toolbar { margin-bottom: 12px; }
.hint { margin-left: 8px; color: #94a3b8; font-size: 12px; }
.muted { color: #94a3b8; font-size: 12px; }
.pkg-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 0 0 12px;
}
.pkg-tip { color: #64748b; font-size: 13px; }
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
</style>
