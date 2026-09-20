import { enforcePrivacyGate, needPrivacyPrompt } from './auth.js'

/**
 * 全局隐私协议闸门：
 * - 未同意时禁止静默登录（见 auth.silentLogin）
 * - 非协议阅读页强制回到首页弹出协议窗
 */
export const privacyMixin = {
	onShow() {
		enforcePrivacyGate()
	}
}

export function shouldShowPrivacyDialog() {
	return needPrivacyPrompt()
}
