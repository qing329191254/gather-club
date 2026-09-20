/** 读取首页缓存的站点配置（管家二维码、热线等） */
export function getSiteConfig() {
	try {
		const app = getApp()
		if (app && app.globalData && app.globalData.site) {
			return app.globalData.site
		}
	} catch (e) {}
	return null
}

export function stewardPropsFromSite(site) {
	const s = site || getSiteConfig() || {}
	return {
		title: s.stewardTitle || '添加管家企业微信',
		tip: s.stewardTip || '长按二维码添加管家微信',
		qrSrc: s.stewardQr || '',
		phone: s.hotline || '4001919179'
	}
}

export function groupQrFromSite(site) {
	const s = site || getSiteConfig() || {}
	return s.groupQr || ''
}
