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
	mallRecords(params) {
		return request('/api/v1/mall/records', { data: params || {} })
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
	orders(params) {
		return request('/api/v1/orders', { data: params || {} })
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
	points(params) {
		return request('/api/v1/user/points', { data: params || {} })
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
	hobbyOptions() {
		return request('/api/v1/hobby/options')
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
	},
	recommend() {
		return request('/api/v1/recommend')
	},
	gatherProduct(id) {
		return request('/api/v1/gather/product/' + id)
	},
	stores() {
		return request('/api/v1/stores')
	},
	agreements() {
		return request('/api/v1/agreements')
	},
	agreement(type) {
		return request('/api/v1/agreements/' + type)
	},
	privacyCollect() {
		return request('/api/v1/privacy/collect')
	},
	privacyShare() {
		return request('/api/v1/privacy/share')
	},
	memberConfig() {
		return request('/api/v1/member/config')
	}
}

export default api
