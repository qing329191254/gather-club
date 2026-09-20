import { request } from './cloud.js'

export const api = {
	health() {
		return request('/api/v1/health')
	},
	wxLogin(payload) {
		return request('/api/v1/auth/wx-login', { method: 'POST', data: payload || {} })
	},
	bindPhone(payload) {
		return request('/api/v1/auth/bind-phone', { method: 'POST', data: payload || {} })
	},
	home() {
		return request('/api/v1/home')
	},
	site() {
		return request('/api/v1/site')
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
	mallRecords() {
		return request('/api/v1/mall/records')
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
	orderDetail(id) {
		return request('/api/v1/orders/' + id)
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
	updateProfile(payload) {
		return request('/api/v1/user/profile', { method: 'PUT', data: payload || {} })
	},
	cancelAccount() {
		return request('/api/v1/user/cancel', { method: 'POST' })
	},
	points() {
		return request('/api/v1/user/points')
	},
	coupons() {
		return request('/api/v1/user/coupons')
	},
	claimCoupon(payload) {
		return request('/api/v1/user/coupons/claim', { method: 'POST', data: payload || {} })
	},
	addresses() {
		return request('/api/v1/user/addresses')
	},
	createAddress(payload) {
		return request('/api/v1/user/addresses', { method: 'POST', data: payload || {} })
	},
	updateAddress(id, payload) {
		return request('/api/v1/user/addresses/' + id, { method: 'PUT', data: payload || {} })
	},
	deleteAddress(id) {
		return request('/api/v1/user/addresses/' + id, { method: 'DELETE' })
	},
	setDefaultAddress(id) {
		return request('/api/v1/user/addresses/' + id + '/default', { method: 'POST' })
	},
	checkin(makeup) {
		const q = makeup ? '?makeup=true' : ''
		return request('/api/v1/checkin' + q, { method: 'POST' })
	},
	checkinMonth(year, month) {
		return request('/api/v1/checkin/month', { data: { year, month } })
	},
	videoHome() {
		return request('/api/v1/video')
	},
	videoFollow() {
		return request('/api/v1/video/follow', { method: 'POST' })
	},
	videoReserve(liveId) {
		return request('/api/v1/video/reserve', { method: 'POST', data: { liveId } })
	},
	videoWatch(liveId) {
		return request('/api/v1/video/watch', { method: 'POST', data: { liveId: liveId || 0 } })
	}
}

export default api
