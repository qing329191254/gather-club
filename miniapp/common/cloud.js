import { CLOUD_ENV, CLOUD_SERVICE, PUBLIC_BASE, COS_CDN } from './config.js'
import { beginLoading, endLoading } from './loading.js'

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

/** 小程序端上传到云托管对象存储，返回 { fileID, url } */
export function uploadToCloud(filePath, cloudPath) {
	return new Promise((resolve, reject) => {
		const wxApi = typeof wx !== 'undefined' ? wx : null
		if (!wxApi || !wxApi.cloud || !wxApi.cloud.uploadFile) {
			reject(new Error('当前环境不支持云存储上传'))
			return
		}
		initCloud()
		const path =
			cloudPath ||
			'uploads/' + Date.now() + '_' + Math.random().toString(36).slice(2, 8) + '.jpg'
		wxApi.cloud.uploadFile({
			cloudPath: path,
			filePath,
			success: (res) => {
				const fileID = (res && res.fileID) || ''
				const url = cloudFileToUrl(fileID) || ''
				resolve({ fileID, url, path })
			},
			fail: (err) => reject(err || new Error('上传失败'))
		})
	})
}

/** cloud://fileID 转 CDN https 地址（需存储权限为所有用户可读） */
export function cloudFileToUrl(fileID) {
	if (!fileID) return ''
	if (/^https?:\/\//i.test(fileID)) return fileID
	const m = String(fileID).match(/^cloud:\/\/[^/]+\/(.+)$/)
	if (m) return COS_CDN.replace(/\/$/, '') + '/' + m[1]
	return ''
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
	const page = Number(data && data.page)
	const tracked = options.loading !== false && !(page > 1)
	if (tracked) beginLoading(options.loadingTitle)

	const run = callByContainer(fullPath, method, body, header).catch(() =>
		callByHttp(fullPath, method, body, header)
	)
	if (!tracked) return run
	return run.then(
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
