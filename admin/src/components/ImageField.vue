<template>
  <div class="img-field">
    <div class="row">
      <el-input v-model="inner" :placeholder="placeholder" clearable @change="emitValue" />
      <el-upload
        :show-file-list="false"
        :http-request="onUpload"
        :disabled="loading"
        accept="image/jpeg,image/png,image/gif,image/webp"
      >
        <el-button :loading="loading">上传</el-button>
      </el-upload>
    </div>
    <el-image v-if="inner" :src="inner" class="preview" fit="cover" :preview-src-list="[inner]" />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../api/http'

const props = defineProps({
  modelValue: { type: String, default: '' },
  folder: { type: String, default: 'uploads' },
  placeholder: { type: String, default: '图片地址或上传' }
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
.row {
  display: flex;
  gap: 8px;
  align-items: center;
}
.row :deep(.el-input) {
  flex: 1;
}
.preview {
  margin-top: 8px;
  width: 120px;
  height: 80px;
  border-radius: 6px;
  background: #f5f5f5;
}
</style>
