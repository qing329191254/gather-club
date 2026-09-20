<template>
  <div class="img-field">
    <el-upload
      class="uploader"
      drag
      :show-file-list="false"
      :http-request="onUpload"
      :disabled="loading"
      accept="image/jpeg,image/png,image/gif,image/webp"
    >
      <div v-if="inner" class="preview-wrap" @click.stop>
        <el-image :src="inner" class="preview" fit="cover" :preview-src-list="[inner]" />
        <div class="preview-actions">
          <el-button type="primary" size="small" :loading="loading">重新上传</el-button>
          <el-button size="small" @click.stop="clear">清除</el-button>
        </div>
      </div>
      <div v-else class="empty">
        <div class="empty-title">{{ loading ? '上传中…' : '点击或拖拽图片到此处上传' }}</div>
        <div class="empty-tip">支持 JPG / PNG / WEBP，不超过 8MB</div>
      </div>
    </el-upload>
    <el-input
      v-model="inner"
      class="url-input"
      :placeholder="placeholder"
      clearable
      @change="emitValue"
    />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../api/http'

const props = defineProps({
  modelValue: { type: String, default: '' },
  folder: { type: String, default: 'uploads' },
  placeholder: { type: String, default: '也可直接粘贴图片链接' }
})
const emit = defineEmits(['update:modelValue'])

const inner = ref(props.modelValue || '')
const loading = ref(false)

watch(
  () => props.modelValue,
  (v) => {
    if (v !== inner.value) inner.value = v || ''
  }
)

function emitValue() {
  emit('update:modelValue', inner.value || '')
}

function clear() {
  inner.value = ''
  emitValue()
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
    inner.value = res.url || res.fileId || ''
    emitValue()
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
.img-field {
  width: 100%;
}
.uploader {
  width: 100%;
}
.uploader :deep(.el-upload) {
  width: 100%;
}
.uploader :deep(.el-upload-dragger) {
  width: 100%;
  padding: 16px;
  border-radius: 10px;
}
.empty {
  padding: 28px 12px;
  text-align: center;
}
.empty-title {
  font-size: 15px;
  color: #334155;
  font-weight: 600;
}
.empty-tip {
  margin-top: 8px;
  font-size: 12px;
  color: #94a3b8;
}
.preview-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}
.preview {
  width: 100%;
  max-width: 280px;
  height: 140px;
  border-radius: 8px;
  background: #f5f5f5;
}
.preview-actions {
  display: flex;
  gap: 8px;
}
.url-input {
  margin-top: 10px;
}
</style>
