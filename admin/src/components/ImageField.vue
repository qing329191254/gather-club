<template>
  <div class="img-field">
    <div class="row">
      <el-input
        v-model="inner"
        clearable
        :placeholder="placeholder"
        @change="emitValue"
      />
      <el-upload
        :show-file-list="false"
        :http-request="onUpload"
        :disabled="loading"
        accept="image/jpeg,image/png,image/gif,image/webp"
      >
        <el-button :loading="loading">上传</el-button>
      </el-upload>
    </div>
    <div v-if="inner" class="preview-box">
      <el-image :src="inner" class="preview" fit="cover" :preview-src-list="[inner]" />
      <el-button class="clear-btn" size="small" text type="danger" @click="clear">清除</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../api/http'

const props = defineProps({
  modelValue: { type: String, default: '' },
  folder: { type: String, default: 'uploads' },
  placeholder: { type: String, default: '图片链接' }
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
    const url = res.url || res.fileId || ''
    if (!url) {
      ElMessage.error('上传失败：未返回图片地址')
      option.onError && option.onError(new Error('empty url'))
      return
    }
    inner.value = url
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
.row {
  display: flex;
  gap: 8px;
  align-items: center;
}
.row :deep(.el-input) {
  flex: 1;
}
.preview-box {
  position: relative;
  margin-top: 10px;
  width: 160px;
  height: 160px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  background: #f8fafc;
}
.preview {
  width: 100%;
  height: 100%;
  display: block;
}
.clear-btn {
  position: absolute;
  right: 4px;
  bottom: 4px;
  background: rgba(255, 255, 255, 0.92) !important;
}
</style>
