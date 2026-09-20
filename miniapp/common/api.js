import { request } from './cloud.js'

export const api = {
	health() {
		return request('/api/v1/health')
	},
	wxLogin(payload) {
		return request('/api/v1/auth/wx-login', { method: 'POST', data: payload || {} })
	},
	home() {
		return request('/api/v1/home')
	},
	gather() {
		return request('/api/v1/gather')
	},
	nyeList() {
		return request('/api/v1/nye')
	},
	nyeDetail(id) {
		return request('/api/v1/nye/' + id)
	},
	mallGoods() {
		return request('/api/v1/mall/goods')
	},
	mallGoodsDetail(id) {
		return request('/api/v1/mall/goods/' + id)
	},
	mallRedeem(goodsId) {
		return request('/api/v1/mall/redeem', { method: 'POST', data: { goodsId } })
	},
	roomAvailability(storeId, date, slot) {
		return request('/api/v1/rooms/availability', {
			data: { store_id: storeId, date, slot }
		})
	},
	roomMonth(storeId, year, month) {
		return request('/api/v1/rooms/month', {
			data: { store_id: storeId, year, month }
		})
	},
	orders() {
		return request('/api/v1/orders')
	},
	createOrder(payload) {
		return request('/api/v1/orders', { method: 'POST', data: payload })
	},
	payOrder(id) {
		return request('/api/v1/orders/' + id + '/pay', { method: 'POST' })
	},
	cancelOrder(id) {
		return request('/api/v1/orders/' + id + '/cancel', { method: 'POST' })
	},
	profile() {
		return request('/api/v1/user/profile')
	},
	points() {
		return request('/api/v1/user/points')
	},
	coupons() {
		return request('/api/v1/user/coupons')
	},
	checkin(makeup) {
		const q = makeup ? '?makeup=true' : ''
		return request('/api/v1/checkin' + q, { method: 'POST' })
	},
	checkinMonth(year, month) {
		return request('/api/v1/checkin/month', { data: { year, month } })
	}
}

export default api
