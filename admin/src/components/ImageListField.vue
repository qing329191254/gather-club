<template>
  <div class="img-list">
    <div class="grid">
      <div v-for="(url, idx) in list" :key="`${url}-${idx}`" class="item">
        <el-image :src="url" fit="cover" class="thumb" :preview-src-list="list" :initial-index="idx" />
        <div class="badge">{{ idx + 1 }}</div>
        <div class="ops">
          <el-button size="small" text :disabled="idx === 0" @click="move(idx, -1)">上移</el-button>
          <el-button size="small" text :disabled="idx === list.length - 1" @click="move(idx, 1)">下移</el-button>
          <el-button size="small" text type="danger" @click="remove(idx)">删除</el-button>
        </div>
      </div>

      <el-upload
        class="add"
        :show-file-list="false"
        :http-request="onUpload"
        :disabled="loading"
        accept="image/jpeg,image/png,image/gif,image/webp"
        multiple
      >
        <div class="add-box">
          <div class="add-title">{{ loading ? '上传中…' : '+ 上传' }}</div>
        </div>
      </el-upload>
    </div>
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
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}
.item {
  width: 140px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
}
.thumb {
  width: 140px;
  height: 100px;
  display: block;
  background: #f8fafc;
}
.badge {
  position: absolute;
  margin-top: -96px;
  margin-left: 6px;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  border-radius: 10px;
  background: rgba(15, 23, 42, 0.65);
  color: #fff;
  font-size: 12px;
  line-height: 20px;
  text-align: center;
  pointer-events: none;
}
.item {
  position: relative;
}
.ops {
  display: flex;
  justify-content: space-between;
  padding: 2px 4px;
  border-top: 1px solid #f1f5f9;
}
.add :deep(.el-upload) {
  display: block;
}
.add-box {
  width: 140px;
  height: 100px;
  border: 1px dashed #d1d5db;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  background: #fafafa;
  box-sizing: border-box;
}
.add-title {
  font-size: 13px;
}
</style>
