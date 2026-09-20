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
	vipLabel: ''
}

export function getPrivacyStatus() {
	try {
		return uni.getStorageSync(PRIVACY_KEY) || ''
	} catch (e) {
		return ''
	}
}

export function setPrivacyStatus(status) {
	// agreed | declined
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
		return Object.assign({}, defaultUser, auth.user)
	}
	return Object.assign({}, defaultUser)
}

export function saveLogin(user) {
	const next = {
		loggedIn: true,
		user: Object.assign({}, defaultUser, user || {}),
		loginAt: Date.now()
	}
	uni.setStorageSync(AUTH_KEY, next)
	setPrivacyStatus('agreed')
	return next
}

export function logout() {
	uni.removeStorageSync(AUTH_KEY)
}

/** 静默登录：拿微信登录态，并写入本地用户（演示环境模拟手机号） */
export function silentLogin(extra) {
	return new Promise((resolve) => {
		const finish = (patch) => {
			const base = getUser()
			const user = Object.assign({}, base, {
				nickname: (patch && patch.nickname) || base.nickname || '微信用户',
				avatar: (patch && patch.avatar) || base.avatar || '',
				phone: (patch && patch.phone) || base.phone || '13881794601',
				points: base.points || 0,
				vip: base.vip || 'V0会员'
			}, extra || {})
			const auth = saveLogin(user)
			resolve(auth)
		}

		uni.login({
			provider: 'weixin',
			success: () => {
				// 真机可继续换 openid / 解密手机号；此处做本地静默登录
				finish({})
			},
			fail: () => {
				finish({})
			}
		})
	})
}

export function needPhoneLoginPrompt() {
	return !isLoggedIn()
}

export function needPrivacyPrompt() {
	return !isLoggedIn() && !getPrivacyStatus()
}
