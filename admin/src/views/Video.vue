<template>
  <el-card>
    <template #header>
      <div class="card-head">
        <span>视频号资料</span>
        <span class="hint">{{ profileStatus }}</span>
      </div>
    </template>
    <p class="intro">直播中 / 预约列表由小程序自动同步视频号，无需在后台手动维护场次。</p>
    <el-form label-width="120px" style="max-width: 720px">
      <el-form-item label="名称"><el-input v-model="profile.name" /></el-form-item>
      <el-form-item label="头像"><ImageField v-model="profile.avatar" folder="video" /></el-form-item>
      <el-form-item label="封面"><ImageField v-model="profile.cover" folder="video" /></el-form-item>
      <el-form-item label="简介"><el-input v-model="profile.intro" type="textarea" :rows="3" /></el-form-item>
      <el-form-item label="视频号">
        <el-input v-model="profile.finderUserName" placeholder="如 sphj1OzseK7ibsJ" />
      </el-form-item>
      <el-form-item label="默认预约积分">
        <el-input-number v-model="profile.defaultReservePoints" :min="0" :max="9999" />
        <span class="field-tip">用户预约直播预告时发放的积分</span>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="profileSaving" @click="saveProfile(true)">保存资料</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../api/http'
import ImageField from '../components/ImageField.vue'

const profile = reactive({
  name: '',
  avatar: '',
  cover: '',
  intro: '',
  finderUserName: '',
  defaultReservePoints: 10
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

async function loadProfile() {
  profileReady.value = false
  const res = await http.get('/config/video')
  Object.assign(
    profile,
    { name: '', avatar: '', cover: '', intro: '', finderUserName: '', defaultReservePoints: 10 },
    res.value || {}
  )
  if (profile.defaultReservePoints == null || profile.defaultReservePoints === '') {
    profile.defaultReservePoints = 10
  } else {
    profile.defaultReservePoints = Number(profile.defaultReservePoints) || 0
  }
  profileDirty.value = false
  profileReady.value = true
}

async function saveProfile(showToast = false) {
  if (profileSaving.value) return
  profileSaving.value = true
  try {
    const points = Number(profile.defaultReservePoints)
    await http.put('/config/video', {
      value: {
        ...profile,
        defaultReservePoints: Number.isFinite(points) && points >= 0 ? points : 10
      }
    })
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
  () => [
    profile.name,
    profile.avatar,
    profile.cover,
    profile.intro,
    profile.finderUserName,
    profile.defaultReservePoints
  ],
  () => scheduleProfileSave()
)

onMounted(loadProfile)
</script>

<style scoped>
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
.intro {
  margin: 0 0 16px;
  color: #64748b;
  font-size: 13px;
  line-height: 1.5;
}
.field-tip {
  margin-left: 12px;
  color: #94a3b8;
  font-size: 13px;
}
</style>
