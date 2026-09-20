import { CLOUD_ENV, CLOUD_SERVICE, PUBLIC_BASE } from './config.js'

let cloudReady = false

export function initCloud() {
	try {
		const wxApi = typeof wx !== 'undefined' ? wx : null
		if (wxApi && wxApi.cloud && !cloudReady) {
			wxApi.cloud.init({
				env: CLOUD_ENV,
				traceUser: true
			})
			cloudReady = true
		}
	} catch (e) {
		cloudReady = false
	}
	return cloudReady
}

function getOpenid() {
	try {
		const auth = uni.getStorageSync('gather_auth')
		if (!auth || typeof auth !== 'object') return ''
		return auth.openid || (auth.user && auth.user.openid) || ''
	} catch (e) {
		return ''
	}
}

function parseBody(raw) {
	if (raw == null) return null
	if (typeof raw === 'object') return raw
	try {
		return JSON.parse(raw)
	} catch (e) {
		return raw
	}
}

function callByHttp(path, method, data, header) {
	return new Promise((resolve, reject) => {
		uni.request({
			url: PUBLIC_BASE + path,
			method,
			data: method === 'GET' ? undefined : data,
			header: Object.assign(
				{
					'content-type': 'application/json'
				},
				header || {}
			),
			success: (res) => {
				if (res.statusCode >= 200 && res.statusCode < 300) {
					resolve(parseBody(res.data))
					return
				}
				const detail =
					(res.data && (res.data.detail || res.data.message)) ||
					'请求失败 ' + res.statusCode
				reject(new Error(typeof detail === 'string' ? detail : '请求失败'))
			},
			fail: (err) => reject(err || new Error('网络异常'))
		})
	})
}

function callByContainer(path, method, data, header) {
	return new Promise((resolve, reject) => {
		const wxApi = typeof wx !== 'undefined' ? wx : null
		if (!wxApi || !wxApi.cloud || !wxApi.cloud.callContainer) {
			reject(new Error('cloud unavailable'))
			return
		}
		initCloud()
		wxApi.cloud.callContainer({
			config: { env: CLOUD_ENV },
			path,
			method,
			header: Object.assign(
				{
					'X-WX-SERVICE': CLOUD_SERVICE,
					'content-type': 'application/json'
				},
				header || {}
			),
			data: data || {},
			success: (res) => {
				const status = res.statusCode || res.status || 200
				const body = parseBody(res.data)
				if (status >= 200 && status < 300) {
					resolve(body)
					return
				}
				const detail =
					(body && (body.detail || body.message)) || '请求失败 ' + status
				reject(new Error(typeof detail === 'string' ? detail : '请求失败'))
			},
			fail: (err) => reject(err || new Error('云调用失败'))
		})
	})
}

/**
 * 统一请求：优先 callContainer，失败时回退公网域名（方便本地调试）。
 */
export function request(path, options = {}) {
	const method = (options.method || 'GET').toUpperCase()
	const data = options.data || {}
	const openid = getOpenid()
	const header = Object.assign({}, options.header || {})
	if (openid) header['X-Openid'] = openid

	const query =
		method === 'GET' && data && Object.keys(data).length
			? '?' +
				Object.keys(data)
					.filter((k) => data[k] !== undefined && data[k] !== null && data[k] !== '')
					.map((k) => encodeURIComponent(k) + '=' + encodeURIComponent(data[k]))
					.join('&')
			: ''
	const fullPath = path + query
	const body = method === 'GET' ? {} : data

	return callByContainer(fullPath, method, body, header).catch(() =>
		callByHttp(fullPath, method, body, header)
	)
}
