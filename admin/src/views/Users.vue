<template>
  <el-card>
    <div class="toolbar">
      <el-input v-model="keyword" placeholder="昵称/手机/openid" style="width: 240px" clearable @keyup.enter="onSearch" />
      <el-button type="primary" @click="onSearch">查询</el-button>
    </div>
    <el-table :data="list" stripe>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="nickname" label="昵称" width="120" />
      <el-table-column prop="phone" label="手机" width="120" />
      <el-table-column prop="points" label="积分" width="90" />
      <el-table-column prop="vip_level" label="会员" width="90" />
      <el-table-column prop="openid" label="OpenID" min-width="160" show-overflow-tooltip />
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="adjust(row)">调积分</el-button>
          <el-button link type="warning" @click="setVip(row)">改等级</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div class="pager">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        background
        @current-change="load"
        @size-change="onSearch"
      />
    </div>
  </el-card>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../api/http'
import { usePager } from '../composables/usePager'

const list = ref([])
const keyword = ref('')
const { page, pageSize, total, applyPage, resetPage, pageParams } = usePager()

async function load() {
  const res = await http.get('/users', {
    params: pageParams({ keyword: keyword.value || undefined })
  })
  list.value = applyPage(res)
}

function onSearch() {
  resetPage()
  load()
}

async function adjust(row) {
  const { value } = await ElMessageBox.prompt('输入增减积分（可为负数）', '调整积分', {
    inputValue: '10',
    inputPattern: /^-?\d+$/,
    inputErrorMessage: '请输入整数'
  })
  await http.post(`/users/${row.id}/points`, { points: Number(value), title: '后台调整' })
  ElMessage.success('已调整')
  load()
}

async function setVip(row) {
  const { value } = await ElMessageBox.prompt('输入等级：V0 / V1 / V2 / V3', '修改会员等级', {
    inputValue: row.vip_level || 'V0'
  })
  await http.put(`/users/${row.id}/vip`, null, { params: { vip_level: value } })
  ElMessage.success('已更新')
  load()
}

onMounted(load)
</script>

<style scoped>
.toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
}
.pager {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
