/**
 * 本地订单读写（与 orders 页共用 key）
 * 后台就绪后改为接口即可。
 */
const ORDERS_KEY = 'gather_orders_v3'

export function loadOrders() {
	try {
		const raw = uni.getStorageSync(ORDERS_KEY)
		if (Array.isArray(raw)) return raw
	} catch (e) {}
	return []
}

export function saveOrders(list) {
	uni.setStorageSync(ORDERS_KEY, list || [])
}

export function prependOrder(order) {
	const list = loadOrders()
	list.unshift(order)
	saveOrders(list)
	return list
}

export function updateOrder(id, patch) {
	const list = loadOrders()
	const idx = list.findIndex((o) => o.id === id)
	if (idx < 0) return false
	list[idx] = Object.assign({}, list[idx], patch)
	saveOrders(list)
	return true
}
