import { ref, watch } from 'vue'

const STORAGE_KEY = 'gather_admin_page_size'
const ALLOWED = [10, 20, 50]

function readStoredSize(fallback) {
  try {
    const n = Number(localStorage.getItem(STORAGE_KEY))
    if (ALLOWED.includes(n)) return n
  } catch {
    /* ignore */
  }
  return fallback
}

/** Shared admin list pager state; page size persists across menu switches. */
export function usePager(defaultSize = 20) {
  const page = ref(1)
  const pageSize = ref(readStoredSize(defaultSize))
  const total = ref(0)

  watch(pageSize, (n) => {
    const size = Number(n)
    if (!ALLOWED.includes(size)) return
    try {
      localStorage.setItem(STORAGE_KEY, String(size))
    } catch {
      /* ignore */
    }
  })

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

  /** Reset to page 1. Returns true if page actually changed (caller can skip load if pagination will fire). */
  function resetPage() {
    if (page.value === 1) return false
    page.value = 1
    return true
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
