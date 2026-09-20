<template>
  <div class="img-list">
    <div v-if="list.length" class="grid">
      <div v-for="(url, idx) in list" :key="`${url}-${idx}`" class="item">
        <el-image :src="url" fit="cover" class="thumb" :preview-src-list="list" :initial-index="idx" />
        <div class="actions">
          <el-button link type="primary" size="small" :disabled="idx === 0" @click="move(idx, -1)">上移</el-button>
          <el-button link type="primary" size="small" :disabled="idx === list.length - 1" @click="move(idx, 1)">下移</el-button>
          <el-button link type="danger" size="small" @click="remove(idx)">删除</el-button>
        </div>
      </div>
    </div>
    <el-upload
      drag
      :show-file-list="false"
      :http-request="onUpload"
      :disabled="loading"
      accept="image/jpeg,image/png,image/gif,image/webp"
      multiple
    >
      <div class="empty">
        <div class="empty-title">{{ loading ? '上传中…' : '点击或拖拽上传图片' }}</div>
        <div class="empty-tip">可多选，支持 JPG / PNG / WEBP</div>
      </div>
    </el-upload>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../api/http'

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
  folder: { type: String, default: 'uploads' }
})
const emit = defineEmits(['update:modelValue'])

const loading = ref(false)
const list = computed(() => (Array.isArray(props.modelValue) ? props.modelValue : []).filter(Boolean))

function setList(next) {
  emit('update:modelValue', next)
}

function remove(idx) {
  const next = list.value.slice()
  next.splice(idx, 1)
  setList(next)
}

function move(idx, delta) {
  const to = idx + delta
  if (to < 0 || to >= list.value.length) return
  const next = list.value.slice()
  const [item] = next.splice(idx, 1)
  next.splice(to, 0, item)
  setList(next)
}

async function onUpload(option) {
  const file = option.file
  if (!file) return
  loading.value = true
  try {
    const body = new FormData()
    body.append('file', file)
    body.append('folder', props.folder || 'uploads')
    const res = await http.post('/upload', body)
    const url = res.url || res.fileId || ''
    if (url) setList([...list.value, url])
    ElMessage.success('上传成功')
    option.onSuccess && option.onSuccess(res)
  } catch (e) {
    option.onError && option.onError(e)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.img-list { width: 100%; }
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 12px;
  margin-bottom: 12px;
}
.item {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
}
.thumb {
  width: 100%;
  height: 96px;
  display: block;
  background: #f8fafc;
}
.actions {
  display: flex;
  justify-content: space-between;
  padding: 4px 6px;
}
.empty {
  padding: 20px 12px;
  text-align: center;
}
.empty-title {
  font-size: 14px;
  color: #334155;
  font-weight: 600;
}
.empty-tip {
  margin-top: 6px;
  font-size: 12px;
  color: #94a3b8;
}
:deep(.el-upload) { width: 100%; }
:deep(.el-upload-dragger) {
  width: 100%;
  padding: 12px;
  border-radius: 10px;
}
</style>
