/**
 * VIP 等级配置
 * 后台可下发同结构覆盖本地默认：
 * { id, name, label, icon, theme }
 * - icon: 图片地址（本地或 CDN）
 * - label: 展示文案，如「V0会员」
 * - theme: 徽章配色
 */
export const vipLevels = [
	{
		id: 'V0',
		name: 'V0',
		label: 'V0会员',
		icon: '/static/icons/vip-style-v0.png',
		theme: {
			pill: '#d4e0f2',
			border: 'transparent',
			text: '#2f4578'
		}
	},
	{
		id: 'V1',
		name: 'V1',
		label: 'V1会员',
		icon: '/static/icons/vip-style-v1.png',
		theme: {
			pill: '#3b7de0',
			border: 'transparent',
			text: '#ffffff'
		}
	},
	{
		id: 'V2',
		name: 'V2',
		label: 'V2会员',
		icon: '/static/icons/vip-style-v2.png',
		theme: {
			pill: '#5a2d96',
			border: 'transparent',
			text: '#ffffff'
		}
	},
	{
		id: 'V3',
		name: 'V3',
		label: 'V3会员',
		icon: '/static/icons/vip-style-v3.png',
		theme: {
			pill: '#8c5a12',
			border: 'transparent',
			text: '#ffffff'
		}
	}
]

const fallback = vipLevels[0]

/** 合并后台下发的等级配置（可选） */
export function setVipLevelsFromServer(list) {
	if (!Array.isArray(list) || !list.length) return vipLevels
	list.forEach((item) => {
		if (!item || !item.id) return
		const idx = vipLevels.findIndex((row) => row.id === item.id)
		if (idx >= 0) {
			vipLevels[idx] = Object.assign({}, vipLevels[idx], item, {
				theme: Object.assign({}, vipLevels[idx].theme, item.theme || {})
			})
		} else {
			vipLevels.push(item)
		}
	})
	return vipLevels
}

/**
 * 根据用户信息解析当前 VIP
 * 支持：
 * - user.vipLevel / user.vipId: 'V0'
 * - user.vip: 'V0会员'
 * - user.vipIcon: 后台单独下发的图标 URL（优先）
 * - user.vipLabel: 后台单独下发的文案（优先）
 */
export function resolveVip(user) {
	const u = user || {}
	let id = u.vipLevel || u.vipId || ''
	if (!id && u.vip) {
		const m = String(u.vip).match(/V\d+/i)
		if (m) id = m[0].toUpperCase()
	}
	if (!id) id = 'V0'
	const conf = vipLevels.find((row) => row.id.toUpperCase() === String(id).toUpperCase()) || fallback
	return {
		id: conf.id,
		label: u.vipLabel || u.vip || conf.label,
		icon: u.vipIcon || conf.icon,
		theme: conf.theme
	}
}
