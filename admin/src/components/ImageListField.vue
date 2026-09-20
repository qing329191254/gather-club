<template>
  <div class="img-list">
    <div class="grid">
      <div v-for="(url, idx) in list" :key="`${url}-${idx}`" class="item">
        <div class="media">
          <el-image :src="url" fit="cover" class="thumb" :preview-src-list="list" :initial-index="idx" />
          <div class="badge">{{ idx + 1 }}</div>
        </div>
        <div class="ops">
          <button type="button" class="op" :disabled="idx === 0" @click="move(idx, -1)">上移</button>
          <button type="button" class="op" :disabled="idx === list.length - 1" @click="move(idx, 1)">下移</button>
          <button type="button" class="op danger" @click="remove(idx)">删除</button>
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
          <div class="add-title">{{ loading ? `上传中 ${pending}…` : '+ 上传' }}</div>
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
const pending = ref(0)
const queue = ref(Promise.resolve())
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

async function uploadOne(file) {
  const body = new FormData()
  body.append('file', file)
  body.append('folder', props.folder || 'uploads')
  const res = await http.post('/upload', body)
  const url = res.url || res.fileId || ''
  if (!url) throw new Error('empty url')
  setList([...list.value, url])
  return res
}

function onUpload(option) {
  const file = option.file
  if (!file) return
  pending.value += 1
  loading.value = true
  queue.value = queue.value
    .then(async () => {
      try {
        const res = await uploadOne(file)
        ElMessage.success('上传成功')
        option.onSuccess && option.onSuccess(res)
      } catch (e) {
        ElMessage.error('上传失败')
        option.onError && option.onError(e)
      } finally {
        pending.value = Math.max(0, pending.value - 1)
        if (pending.value === 0) loading.value = false
      }
    })
    .catch(() => {})
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
  width: 168px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #fff;
  overflow: hidden;
}
.media {
  position: relative;
  width: 100%;
  height: 112px;
  background: #f8fafc;
}
.thumb {
  width: 100%;
  height: 112px;
  display: block;
}
.badge {
  position: absolute;
  top: 6px;
  left: 6px;
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
.ops {
  display: flex;
  align-items: center;
  justify-content: space-around;
  gap: 2px;
  padding: 6px 4px;
  border-top: 1px solid #f1f5f9;
  box-sizing: border-box;
}
.op {
  flex: 1;
  margin: 0;
  padding: 2px 0;
  border: none;
  background: transparent;
  color: #64748b;
  font-size: 12px;
  line-height: 1.4;
  cursor: pointer;
  white-space: nowrap;
}
.op:hover:not(:disabled) {
  color: #2563eb;
}
.op:disabled {
  color: #cbd5e1;
  cursor: not-allowed;
}
.op.danger {
  color: #ef4444;
}
.op.danger:hover {
  color: #dc2626;
}
.add :deep(.el-upload) {
  display: block;
}
.add-box {
  width: 168px;
  height: 112px;
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
