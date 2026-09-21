import { request } from './cloud.js'

export const api = {
	health() {
		return request('/api/v1/health')
	},
	wxLogin(payload, options) {
		return request('/api/v1/auth/wx-login', Object.assign({ method: 'POST', data: payload || {} }, options || {}))
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
	mallRedeem(goodsId, addressId) {
		return request('/api/v1/mall/redeem', {
			method: 'POST',
			data: { goodsId, addressId }
		})
	},
	loyaltyConfig() {
		return request('/api/v1/loyalty/config')
	},
	profileReward() {
		return request('/api/v1/profile-reward')
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
	profile(options) {
		return request('/api/v1/user/profile', options || {})
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
	videoReserve(payload) {
		const data =
			payload && typeof payload === 'object'
				? payload
				: { liveId: payload }
		return request('/api/v1/video/reserve', { method: 'POST', data })
	},
	videoWatch(liveId) {
		const id = Number(liveId)
		return request('/api/v1/video/watch', {
			method: 'POST',
			data: { liveId: Number.isFinite(id) && id > 0 ? id : 0 }
		})
	},
	recommend() {
		return request('/api/v1/recommend')
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
