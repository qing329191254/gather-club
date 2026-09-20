import { api } from './api.js'
import { initCloud } from './cloud.js'

const AUTH_KEY = 'gather_auth'
const PRIVACY_KEY = 'gather_privacy'

const defaultUser = {
	nickname: '微信用户',
	avatar: '',
	phone: '',
	points: 0,
	vip: 'V0会员',
	vipLevel: 'V0',
	vipIcon: '',
	vipLabel: '',
	openid: ''
}

export function getPrivacyStatus() {
	try {
		return uni.getStorageSync(PRIVACY_KEY) || ''
	} catch (e) {
		return ''
	}
}

export function setPrivacyStatus(status) {
	uni.setStorageSync(PRIVACY_KEY, status)
}

export function isPrivacyAgreed() {
	return getPrivacyStatus() === 'agreed'
}

export function isLoggedIn() {
	const auth = getAuth()
	return !!(auth && auth.loggedIn)
}

export function getAuth() {
	try {
		const raw = uni.getStorageSync(AUTH_KEY)
		if (raw && typeof raw === 'object') return raw
	} catch (e) {}
	return null
}

export function getUser() {
	const auth = getAuth()
	if (auth && auth.user) {
		return Object.assign({}, defaultUser, auth.user, {
			openid: auth.openid || (auth.user && auth.user.openid) || ''
		})
	}
	return Object.assign({}, defaultUser)
}

export function getOpenid() {
	const auth = getAuth()
	return (auth && auth.openid) || (auth && auth.user && auth.user.openid) || ''
}

export function saveLogin(user, openid) {
	const merged = Object.assign({}, defaultUser, user || {})
	const oid = openid || merged.openid || ''
	if (oid) merged.openid = oid
	const next = {
		loggedIn: true,
		openid: oid,
		user: merged,
		loginAt: Date.now()
	}
	uni.setStorageSync(AUTH_KEY, next)
	setPrivacyStatus('agreed')
	return next
}

export function logout() {
	uni.removeStorageSync(AUTH_KEY)
}

function mapServerUser(raw, openid) {
	const u = raw || {}
	return {
		nickname: u.nickname || '微信用户',
		avatar: u.avatar || '',
		phone: u.phone || '',
		points: u.points != null ? u.points : 0,
		vipLevel: u.vipLevel || u.vip_level || 'V0',
		vip: u.vip || ((u.vipLevel || u.vip_level || 'V0') + '会员'),
		vipIcon: u.vipIcon || '',
		vipLabel: u.vipLabel || '',
		openid: openid || u.openid || ''
	}
}

/** 静默登录：wx.login 拿 code，换云托管用户 */
export function silentLogin(extra) {
	return new Promise((resolve) => {
		initCloud()
		const finishLocal = (patch) => {
			const base = getUser()
			const user = Object.assign({}, base, {
				nickname: (patch && patch.nickname) || base.nickname || '微信用户',
				avatar: (patch && patch.avatar) || base.avatar || '',
				phone: (patch && patch.phone) || base.phone || '',
				points: base.points || 0,
				vip: base.vip || 'V0会员'
			}, extra || {})
			resolve(saveLogin(user, user.openid))
		}

		uni.login({
			provider: 'weixin',
			success: (loginRes) => {
				const code = (loginRes && loginRes.code) || ''
				api
					.wxLogin({
						code,
						nickname: (extra && extra.nickname) || '',
						avatar: (extra && extra.avatar) || '',
						phone: (extra && extra.phone) || ''
					})
					.then((res) => {
						const openid = res.openid || ''
						const user = Object.assign({}, mapServerUser(res.user, openid), extra || {})
						resolve(saveLogin(user, openid))
					})
					.catch(() => finishLocal(extra || {}))
			},
			fail: () => finishLocal(extra || {})
		})
	})
}

export function refreshProfile() {
	if (!getOpenid()) {
		return Promise.resolve(getUser())
	}
	return api
		.profile()
		.then((res) => {
			const user = mapServerUser(res, getOpenid())
			saveLogin(user, getOpenid())
			return user
		})
		.catch(() => getUser())
}

export function needPhoneLoginPrompt() {
	return !isLoggedIn()
}

export function needPrivacyPrompt() {
	return !isLoggedIn() && !getPrivacyStatus()
}
