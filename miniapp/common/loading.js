import { reactive } from 'vue'

const SHOW_DELAY = 300
const MIN_VISIBLE = 200

export const loadingState = reactive({
	visible: false,
	title: '加载中'
})

let count = 0
let showTimer = null
let hideTimer = null
let shownAt = 0

function clearShowTimer() {
	if (!showTimer) return
	clearTimeout(showTimer)
	showTimer = null
}

function clearHideTimer() {
	if (!hideTimer) return
	clearTimeout(hideTimer)
	hideTimer = null
}

export function beginLoading(nextTitle) {
	count += 1
	clearHideTimer()
	if (nextTitle) loadingState.title = nextTitle
	else if (count === 1) loadingState.title = '加载中'
	if (loadingState.visible || showTimer) return
	showTimer = setTimeout(() => {
		showTimer = null
		if (count <= 0) return
		loadingState.visible = true
		shownAt = Date.now()
	}, SHOW_DELAY)
}

export function endLoading() {
	count = Math.max(0, count - 1)
	if (count > 0) return
	clearShowTimer()
	if (!loadingState.visible) return
	const wait = Math.max(0, MIN_VISIBLE - (Date.now() - shownAt))
	hideTimer = setTimeout(() => {
		hideTimer = null
		if (count > 0) return
		loadingState.visible = false
	}, wait)
}

export function withLoading(task, title) {
	beginLoading(title)
	let ret
	try {
		ret = typeof task === 'function' ? task() : task
	} catch (e) {
		endLoading()
		throw e
	}
	if (ret && typeof ret.then === 'function') {
		return ret.then(
			(value) => {
				endLoading()
				return value
			},
			(err) => {
				endLoading()
				return Promise.reject(err)
			}
		)
	}
	endLoading()
	return ret
}
