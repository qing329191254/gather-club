<template>
  <div>
    <el-card>
      <template #header>
        <div class="card-head">
          <span>视频号资料</span>
          <span class="hint">{{ profileStatus }}</span>
        </div>
      </template>
      <el-form label-width="120px" style="max-width: 720px">
        <el-form-item label="名称"><el-input v-model="profile.name" /></el-form-item>
        <el-form-item label="头像"><ImageField v-model="profile.avatar" folder="video" /></el-form-item>
        <el-form-item label="封面"><ImageField v-model="profile.cover" folder="video" /></el-form-item>
        <el-form-item label="简介"><el-input v-model="profile.intro" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="视频号 ID">
          <el-input v-model="profile.finderUserName" placeholder="视频号 ID" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="profileSaving" @click="saveProfile(true)">保存资料</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card style="margin-top: 16px">
      <div class="toolbar">
        <el-button type="primary" @click="openEdit()">新增直播</el-button>
      </div>
      <el-table :data="list" stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">{{ row.status === 'living' ? '直播中' : '预约' }}</template>
        </el-table-column>
        <el-table-column prop="time_text" label="时间" width="140" />
        <el-table-column prop="line1" label="标题" min-width="160" />
        <el-table-column prop="line2" label="副标题" min-width="120" />
        <el-table-column prop="points" label="积分" width="80" />
        <el-table-column prop="notice_id" label="预告 ID" min-width="140" />
        <el-table-column prop="sort" label="排序" width="70" />
        <el-table-column label="启用" width="80">
          <template #default="{ row }">{{ row.enabled ? '是' : '否' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="140">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link type="danger" :loading="busy('remove-' + row.id)" @click="onRemove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="visible" title="直播" width="560px">
      <el-form label-width="100px">
        <el-form-item label="状态">
          <el-select v-model="form.status">
            <el-option label="直播中" value="living" />
            <el-option label="预约" value="scheduled" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间"><el-input v-model="form.time_text" placeholder="开播时间" /></el-form-item>
        <el-form-item label="标题"><el-input v-model="form.line1" /></el-form-item>
        <el-form-item label="副标题"><el-input v-model="form.line2" /></el-form-item>
        <el-form-item label="预约积分"><el-input-number v-model="form.points" :min="0" /></el-form-item>
        <el-form-item label="头像"><ImageField v-model="form.avatar" folder="video" placeholder="可选，留空使用视频号头像" /></el-form-item>
        <el-form-item label="预告 ID"><el-input v-model="form.notice_id" placeholder="直播预告 ID" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="form.sort" :min="0" /></el-form-item>
        <el-form-item label="启用"><el-switch v-model="form.enabled" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" :loading="busy('save')" @click="onSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../api/http'
import { useLock } from '../composables/useLock'
import ImageField from '../components/ImageField.vue'

const { busy, run } = useLock()

const profile = reactive({
  name: '',
  avatar: '',
  cover: '',
  intro: '',
  finderUserName: ''
})
const profileReady = ref(false)
const profileSaving = ref(false)
const profileDirty = ref(false)
const profileSavedAt = ref('')
let profileTimer = null

const profileStatus = computed(() => {
  if (profileSaving.value) return '正在保存…'
  if (profileDirty.value) return '有未保存修改，将自动保存'
  if (profileSavedAt.value) return `已自动保存 ${profileSavedAt.value}`
  return '修改后会自动保存'
})

const list = ref([])
const visible = ref(false)
const emptyForm = () => ({
  id: null,
  status: 'scheduled',
  time_text: '',
  line1: '',
  line2: '',
  points: 10,
  avatar: '',
  notice_id: '',
  sort: 0,
  enabled: true
})
const form = reactive(emptyForm())

async function loadProfile() {
  profileReady.value = false
  const res = await http.get('/config/video')
  Object.assign(profile, { name: '', avatar: '', cover: '', intro: '', finderUserName: '' }, res.value || {})
  profileDirty.value = false
  profileReady.value = true
}

async function saveProfile(showToast = false) {
  if (profileSaving.value) return
  profileSaving.value = true
  try {
    await http.put('/config/video', { value: { ...profile } })
    profileDirty.value = false
    profileSavedAt.value = new Date().toLocaleTimeString()
    if (showToast) ElMessage.success('资料已保存')
  } finally {
    profileSaving.value = false
  }
}

function scheduleProfileSave() {
  if (!profileReady.value) return
  profileDirty.value = true
  if (profileTimer) clearTimeout(profileTimer)
  profileTimer = setTimeout(() => saveProfile(false), 600)
}

watch(
  () => [profile.name, profile.avatar, profile.cover, profile.intro, profile.finderUserName],
  () => scheduleProfileSave()
)

async function loadLives() {
  list.value = await http.get('/video/lives')
}

function openEdit(row) {
  Object.assign(form, emptyForm(), row || {})
  visible.value = true
}

async function onSave() {
  return run('save', async () => {
  const payload = {
    status: form.status,
    time_text: form.time_text,
    line1: form.line1,
    line2: form.line2,
    points: form.points,
    avatar: form.avatar,
    notice_id: form.notice_id,
    sort: form.sort,
    enabled: form.enabled
  }
  if (form.id) await http.put(`/video/lives/${form.id}`, payload)
  else await http.post('/video/lives', payload)
  ElMessage.success('已保存')
  visible.value = false
  loadLives()
  })
}

async function onRemove(row) {
  return run('remove-' + row.id, async () => {
  await ElMessageBox.confirm('确认删除这条直播？', '提示')
  await http.delete(`/video/lives/${row.id}`)
  loadLives()
  })
}

onMounted(() => {
  loadProfile()
  loadLives()
})
</script>

<style scoped>
.toolbar {
  margin-bottom: 12px;
}
.card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.hint {
  color: #94a3b8;
  font-size: 13px;
  font-weight: 400;
}
</style>
