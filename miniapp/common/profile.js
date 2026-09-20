/** 昵称、生日、手机号、兴趣都填了才算资料完整。默认昵称「微信用户」不算。 */
export function isProfileComplete(user) {
	const u = user || {}
	const nick = String(u.nickname || '').trim()
	if (!nick || nick === '微信用户') return false
	if (!String(u.birthday || '').trim()) return false
	if (!String(u.phone || '').trim()) return false
	if (!String(u.hobby || '').trim()) return false
	return true
}
