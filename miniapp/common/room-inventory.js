/** 包房时段常量与日期工具（库存数据一律走接口） */

export const SLOTS = [
	{ key: 'lunch', name: '午市', time: '11:00-14:00' },
	{ key: 'dinner', name: '晚市', time: '17:00-21:30' }
]

function pad2(n) {
	return String(n).padStart(2, '0')
}

export function formatDate(d) {
	return `${d.getFullYear()}-${pad2(d.getMonth() + 1)}-${pad2(d.getDate())}`
}
