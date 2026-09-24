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
		icon: '',
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
		icon: '',
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
		icon: '',
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
		icon: '',
		theme: {
			pill: '#8c5a12',
			border: 'transparent',
			text: '#ffffff'
		}
	}
]

const fallback = vipLevels[0]

/** 用会员中心后台色（levelColor / barColor）推导徽章主题 */
function themeFromLevel(item, base) {
	const fromServer = (item && item.theme) || {}
	const levelColor = (item && (item.levelColor || item.barColor)) || ''
	const derived = {}
	if (levelColor) {
		derived.pill = levelColor
		// 浅色底用深字，深色底用白字
		const hex = String(levelColor).replace('#', '')
		if (/^[0-9a-fA-F]{6}$/.test(hex)) {
			const r = parseInt(hex.slice(0, 2), 16)
			const g = parseInt(hex.slice(2, 4), 16)
			const b = parseInt(hex.slice(4, 6), 16)
			const luma = (r * 299 + g * 587 + b * 114) / 1000
			derived.text = luma > 160 ? '#1a1a1a' : '#ffffff'
		} else {
			derived.text = '#ffffff'
		}
		derived.border = 'transparent'
	}
	return Object.assign({}, (base && base.theme) || {}, derived, fromServer)
}

/** 合并后台下发的等级配置（可选） */
export function setVipLevelsFromServer(list) {
	if (!Array.isArray(list) || !list.length) return vipLevels
	list.forEach((item) => {
		if (!item || !item.id) return
		const idx = vipLevels.findIndex((row) => row.id === item.id)
		if (idx >= 0) {
			const prev = vipLevels[idx]
			vipLevels[idx] = Object.assign({}, prev, item, {
				icon: item.icon || item.crownIcon || prev.icon || '',
				theme: themeFromLevel(item, prev)
			})
		} else {
			vipLevels.push(
				Object.assign({}, item, {
					theme: themeFromLevel(item, null)
				})
			)
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
	if (u.isMember) {
		const exp = u.memberExpireAt || ''
		return {
			id: 'MEMBER',
			label: exp ? `会员` : '会员',
			icon: u.vipIcon || '',
			theme: {
				pill: '#c45c26',
				border: 'transparent',
				text: '#ffffff'
			},
			expireAt: exp
		}
	}
	return {
		id: 'NONE',
		label: '未开通',
		icon: '',
		theme: {
			pill: 'rgba(255,255,255,0.22)',
			border: 'rgba(255,255,255,0.55)',
			text: '#ffffff'
		},
		expireAt: ''
	}
}
