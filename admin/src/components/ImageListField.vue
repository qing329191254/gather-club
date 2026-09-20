<template>
  <div class="img-list">
    <div class="grid">
      <div v-for="(url, idx) in list" :key="`${url}-${idx}`" class="item">
        <el-image :src="url" fit="cover" class="thumb" :preview-src-list="list" :initial-index="idx" />
        <div class="badge">{{ idx + 1 }}</div>
        <div class="mask">
          <el-button type="primary" size="small" circle :disabled="idx === 0" @click.stop="move(idx, -1)">
            ↑
          </el-button>
          <el-button type="primary" size="small" circle :disabled="idx === list.length - 1" @click.stop="move(idx, 1)">
            ↓
          </el-button>
          <el-button type="danger" size="small" circle @click.stop="remove(idx)">删</el-button>
        </div>
      </div>

      <el-upload
        class="add"
        drag
        :show-file-list="false"
        :http-request="onUpload"
        :disabled="loading"
        accept="image/jpeg,image/png,image/gif,image/webp"
        multiple
      >
        <div class="add-inner">
          <div class="add-title">{{ loading ? '上传中…' : '+ 添加图片' }}</div>
          <div class="add-tip">点击或拖拽，可多选</div>
        </div>
      </el-upload>
    </div>
    <div v-if="list.length" class="footer-tip">共 {{ list.length }} 张，鼠标移到图片上可排序或删除，点击图片可放大预览</div>
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
  grid-template-columns: repeat(auto-fill, minmax(148px, 1fr));
  gap: 12px;
}
.item {
  position: relative;
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  aspect-ratio: 16 / 10;
}
.thumb {
  width: 100%;
  height: 100%;
  display: block;
}
.badge {
  position: absolute;
  top: 6px;
  left: 6px;
  min-width: 22px;
  height: 22px;
  padding: 0 6px;
  border-radius: 11px;
  background: rgba(15, 23, 42, 0.7);
  color: #fff;
  font-size: 12px;
  line-height: 22px;
  text-align: center;
}
.mask {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  background: rgba(15, 23, 42, 0.45);
  opacity: 0;
  transition: opacity 0.15s ease;
}
.item:hover .mask { opacity: 1; }
.add {
  aspect-ratio: 16 / 10;
}
.add :deep(.el-upload),
.add :deep(.el-upload-dragger) {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
  border-radius: 10px;
}
.add-inner {
  height: 100%;
  min-height: 90px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
}
.add-title {
  font-size: 14px;
  font-weight: 600;
  color: #334155;
}
.add-tip {
  font-size: 12px;
  color: #94a3b8;
}
.footer-tip {
  margin-top: 10px;
  font-size: 12px;
  color: #94a3b8;
}
</style>
