import { ref } from 'vue'

/** Shared admin list pager state */
export function usePager(defaultSize = 20) {
  const page = ref(1)
  const pageSize = ref(defaultSize)
  const total = ref(0)

  function applyPage(res) {
    const data = res || {}
    const list = Array.isArray(data) ? data : data.list || []
    total.value = Array.isArray(data) ? list.length : Number(data.total || 0)
    if (!Array.isArray(data)) {
      page.value = Number(data.page || page.value)
      pageSize.value = Number(data.page_size || pageSize.value)
    }
    return list
  }

  function resetPage() {
    page.value = 1
  }

  function pageParams(extra = {}) {
    return {
      page: page.value,
      page_size: pageSize.value,
      ...extra
    }
  }

  return { page, pageSize, total, applyPage, resetPage, pageParams }
}
