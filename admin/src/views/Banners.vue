<template>
  <el-card>
    <div class="toolbar">
      <el-button type="primary" @click="openEdit()">新增轮播</el-button>
    </div>
    <el-table :data="list" stripe>
      <el-table-column label="图片" width="140">
        <template #default="{ row }">
          <el-image :src="row.image" style="width: 100px; height: 50px" fit="cover" />
        </template>
      </el-table-column>
      <el-table-column label="点击后去" min-width="160">
        <template #default="{ row }">{{ linkLabel(row.link) }}</template>
      </el-table-column>
      <el-table-column prop="sort" label="排序" width="80" />
      <el-table-column label="是否显示" width="100">
        <template #default="{ row }">
          <el-tag :type="row.enabled ? 'success' : 'info'">{{ row.enabled ? '显示' : '隐藏' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" :loading="busy('remove-' + row.id)" @click="onRemove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="visible" :title="form.id ? '编辑轮播图' : '新增轮播图'" width="520px">
      <el-form label-width="100px">
        <el-form-item label="轮播图片">
          <ImageField v-model="form.image" folder="banners" placeholder="上传或粘贴图片地址" />
        </el-form-item>
        <el-form-item label="点击后去">
          <el-select v-model="form.link" placeholder="请选择要打开的页面" style="width: 100%" clearable filterable>
            <el-option
              v-for="item in linkOptions"
              :key="item.value || 'none'"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort" :min="0" />
          <span class="hint">数字越小越靠前</span>
        </el-form-item>
        <el-form-item label="是否显示">
          <el-switch v-model="form.enabled" active-text="显示" inactive-text="隐藏" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" :loading="busy('save')" @click="onSave">保存</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../api/http'
import { useLock } from '../composables/useLock'
import ImageField from '../components/ImageField.vue'

const { busy, run } = useLock()

const activities = ref([])

const baseLinkOptions = [
  { label: '不跳转', value: '' },
  { label: '订酒店', value: '/pages/recommend/recommend' },
  { label: '聚餐', value: '/pages/gather/gather' },
  { label: '积分商城', value: '/pages/mall/mall' },
  { label: '包房预约', value: '/pages/booking/booking' },
  { label: '我的订单', value: '/pages/orders/orders' },
  { label: '每日签到', value: '/pages/checkin/checkin' },
  { label: '会员中心', value: '/pages/mine/member' },
  { label: '视频号', value: '/pages/video/video' }
]

const linkOptions = computed(() => {
  const actLinks = (activities.value || [])
    .filter((a) => a && a.enabled !== false && (a.tag || a.name))
    .map((a) => {
      const tag = String(a.tag || a.name).trim()
      return {
        label: `活动：${a.name || tag}`,
        value: `/pages/nye/nye?tag=${encodeURIComponent(tag)}`
      }
    })
  return [...baseLinkOptions.slice(0, 1), ...actLinks, ...baseLinkOptions.slice(1)]
})

function defaultActivityLink() {
  const nye = linkOptions.value.find((item) => item.label === '活动：年夜饭')
  return (nye || linkOptions.value.find((item) => String(item.value).startsWith('/pages/nye/nye?')))?.value || ''
}

const list = ref([])
const visible = ref(false)
const form = reactive({ id: null, image: '', link: '', sort: 0, enabled: true })

function linkLabel(link) {
  const hit = linkOptions.value.find((item) => item.value === (link || ''))
  if (hit) return hit.label
  if (!link) return '不跳转'
  try {
    if (String(link).startsWith('/pages/nye/nye')) {
      const q = String(link).split('?')[1] || ''
      const tag = new URLSearchParams(q).get('tag')
      if (tag) return `活动：${decodeURIComponent(tag)}`
      return '活动：年夜饭'
    }
  } catch (_) {
    /* ignore */
  }
  return '自定义页面'
}

async function load() {
  const [rows, acts] = await Promise.all([http.get('/banners'), http.get('/activities')])
  list.value = rows || []
  activities.value = acts || []
}

function openEdit(row) {
  Object.assign(form, { id: null, image: '', link: '', sort: 0, enabled: true }, row || {})
  if (form.link === '/pages/nye/nye') {
    form.link = defaultActivityLink()
  }
  visible.value = true
}

async function onSave() {
  return run('save', async () => {
    if (!form.image) {
      ElMessage.warning('请上传轮播图片')
      return
    }
    const payload = {
      image: form.image,
      link: form.link || '',
      sort: form.sort,
      enabled: form.enabled
    }
    if (form.id) await http.put(`/banners/${form.id}`, payload)
    else await http.post('/banners', payload)
    ElMessage.success('已保存')
    visible.value = false
    load()
  })
}

async function onRemove(row) {
  return run('remove-' + row.id, async () => {
    await ElMessageBox.confirm('确认删除该轮播？', '提示')
    await http.delete(`/banners/${row.id}`)
    load()
  })
}

onMounted(load)
</script>

<style scoped>
.toolbar {
  margin-bottom: 12px;
}
.hint {
  margin-left: 8px;
  color: #999;
  font-size: 12px;
}
</style>
