<template>
  <el-card>
    <el-tabs v-model="tab">
      <el-tab-pane label="协议" name="agreements" />
      <el-tab-pane label="收集清单" name="privacy_collect" />
      <el-tab-pane label="共享清单" name="privacy_share" />
      <el-tab-pane label="会员配置" name="member" />
    </el-tabs>
    <el-input v-model="text" type="textarea" :rows="22" />
    <div class="actions">
      <el-button type="primary" @click="onSave">保存</el-button>
    </div>
  </el-card>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../api/http'

const tab = ref('agreements')
const text = ref('{}')

async function load() {
  const res = await http.get(`/config/${tab.value}`)
  text.value = JSON.stringify(res.value || {}, null, 2)
}

async function onSave() {
  let value
  try {
    value = JSON.parse(text.value)
  } catch (e) {
    ElMessage.error('JSON 格式不正确')
    return
  }
  await http.put(`/config/${tab.value}`, { value })
  ElMessage.success('已保存')
}

watch(tab, load)
onMounted(load)
</script>

<style scoped>
.actions { margin-top: 12px; }
</style>
