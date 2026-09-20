import { reactive } from 'vue'

export function useLock() {
  const locks = reactive({})
  function busy(key = 'default') {
    return !!locks[key]
  }
  async function run(key, fn, visual) {
    const k = key || 'default'
    if (locks[k]) return
    locks[k] = true
    const vis = visual && visual !== k ? visual : ''
    if (vis) locks[vis] = true
    try {
      return await fn()
    } finally {
      locks[k] = false
      if (vis) locks[vis] = false
    }
  }
  return { busy, run }
}
