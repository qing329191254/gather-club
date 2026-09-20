/**
 * 包房库存（小程序本地模拟）
 * 后台就绪后：把 readState / writeState / seed 换成接口请求即可，页面调用方式不变。
 *
 * 维度：门店 storeId + 日期 YYYY-MM-DD + 时段 lunch|dinner
 */

const STORAGE_KEY = 'gather_room_inventory_v1'
const BOOKINGS_KEY = 'gather_room_bookings_v1'

export const SLOTS = [
	{ key: 'lunch', name: '午市', time: '11:00-14:00' },
	{ key: 'dinner', name: '晚市', time: '17:00-21:30' }
]

/** 默认每日可订包房数（演示用，后台可覆盖） */
const DEFAULT_CAPACITY = {
	lunch: 4,
	dinner: 8
}

function pad2(n) {
	return String(n).padStart(2, '0')
}

export function formatDate(d) {
	return `${d.getFullYear()}-${pad2(d.getMonth() + 1)}-${pad2(d.getDate())}`
}

function todayStr() {
	return formatDate(new Date())
}

function makeKey(storeId, date, slot) {
	return `${storeId}|${date}|${slot}`
}

function readState() {
	try {
		const raw = uni.getStorageSync(STORAGE_KEY)
		if (raw && typeof raw === 'object') return raw
	} catch (e) {}
	return null
}

function writeState(state) {
	uni.setStorageSync(STORAGE_KEY, state)
}

/** 确保库存已初始化；可传入门店列表补齐缺失门店 */
export function ensureInventory(storeIds) {
	return ensureSeed(storeIds)
}

function ensureSeed(storeIds) {
	let state = readState()
	if (state && state.slots && Object.keys(state.slots).length) {
		// 补齐新门店未来 60 天（不覆盖已有）
		if (storeIds && storeIds.length) {
			const start = new Date()
			start.setHours(0, 0, 0, 0)
			let changed = false
			storeIds.forEach((storeId) => {
				const probe = makeKey(storeId, formatDate(start), 'dinner')
				if (state.slots[probe]) return
				for (let i = 0; i < 60; i++) {
					const d = new Date(start)
					d.setDate(start.getDate() + i)
					const date = formatDate(d)
					;['lunch', 'dinner'].forEach((slot) => {
						const key = makeKey(storeId, date, slot)
						if (state.slots[key]) return
						const day = d.getDate()
						const capacity = DEFAULT_CAPACITY[slot]
						let booked = 0
						if (day % 11 === 0) booked = capacity
						else if (day % 7 === 0) booked = Math.max(0, capacity - 1)
						else if (day % 5 === 0) booked = Math.min(capacity, 2)
						state.slots[key] = { capacity, booked }
						changed = true
					})
				}
			})
			if (changed) writeState(state)
		}
		return state
	}
	const slots = {}
	const start = new Date()
	start.setHours(0, 0, 0, 0)
	const ids = storeIds && storeIds.length ? storeIds : ['default']
	ids.forEach((storeId) => {
		for (let i = 0; i < 60; i++) {
			const d = new Date(start)
			d.setDate(start.getDate() + i)
			const date = formatDate(d)
			;['lunch', 'dinner'].forEach((slot) => {
				const key = makeKey(storeId, date, slot)
				// 演示：部分日期故意订满，方便看到「已满」
				const day = d.getDate()
				let booked = 0
				const capacity = DEFAULT_CAPACITY[slot]
				if (day % 11 === 0) booked = capacity
				else if (day % 7 === 0) booked = Math.max(0, capacity - 1)
				else if (day % 5 === 0) booked = Math.min(capacity, 2)
				slots[key] = { capacity, booked }
			})
		}
	})
	state = { version: 1, slots, updatedAt: Date.now() }
	writeState(state)
	return state
}

function getSlotRecord(storeId, date, slot) {
	const state = ensureSeed([storeId])
	const key = makeKey(storeId, date, slot)
	if (!state.slots[key]) {
		state.slots[key] = {
			capacity: DEFAULT_CAPACITY[slot] || 4,
			booked: 0
		}
		writeState(state)
	}
	return state.slots[key]
}

/**
 * 查询某一时段可订情况
 * @returns {{ capacity, booked, remain, full, statusText }}
 */
export function getAvailability(storeId, date, slot) {
	const sid = storeId || 'default'
	const rec = getSlotRecord(sid, date, slot)
	const remain = Math.max(0, (rec.capacity || 0) - (rec.booked || 0))
	const full = remain <= 0
	return {
		storeId: sid,
		date,
		slot,
		capacity: rec.capacity,
		booked: rec.booked,
		remain,
		full,
		statusText: full ? '已满' : remain <= 2 ? `仅剩${remain}间` : `剩余${remain}间`
	}
}

/**
 * 某月日历：每天汇总（取晚市为主展示，并带午市信息）
 */
export function getMonthAvailability(storeId, year, month) {
	const sid = storeId || 'default'
	ensureSeed([sid])
	const daysInMonth = new Date(year, month, 0).getDate()
	const today = todayStr()
	const map = {}
	for (let d = 1; d <= daysInMonth; d++) {
		const date = `${year}-${pad2(month)}-${pad2(d)}`
		const lunch = getAvailability(sid, date, 'lunch')
		const dinner = getAvailability(sid, date, 'dinner')
		const remain = lunch.remain + dinner.remain
		const past = date < today
		map[date] = {
			date,
			past,
			lunch,
			dinner,
			remain,
			full: !past && lunch.full && dinner.full,
			open: !past,
			statusText: past
				? ''
				: lunch.full && dinner.full
					? '已满'
					: remain <= 3
						? `剩${remain}`
						: `剩${remain}`
		}
	}
	return map
}

/**
 * 锁定包房（下单成功时调用）
 * @returns {{ ok: boolean, message?: string, remain?: number }}
 */
export function lockRooms({ storeId, date, slot, qty = 1, orderId }) {
	const sid = storeId || 'default'
	const n = Math.max(1, Number(qty) || 1)
	const state = ensureSeed([sid])
	const key = makeKey(sid, date, slot)
	const rec = state.slots[key] || {
		capacity: DEFAULT_CAPACITY[slot] || 4,
		booked: 0
	}
	const remain = rec.capacity - rec.booked
	if (remain < n) {
		return { ok: false, message: '该时段包房已满，请换日期或时段', remain: Math.max(0, remain) }
	}
	rec.booked += n
	state.slots[key] = rec
	state.updatedAt = Date.now()
	writeState(state)

	const bookings = readBookings()
	bookings.push({
		id: orderId || `rb_${Date.now()}`,
		storeId: sid,
		date,
		slot,
		qty: n,
		createdAt: Date.now()
	})
	uni.setStorageSync(BOOKINGS_KEY, bookings)

	return { ok: true, remain: rec.capacity - rec.booked }
}

export function releaseRooms({ storeId, date, slot, qty = 1 }) {
	const sid = storeId || 'default'
	const n = Math.max(1, Number(qty) || 1)
	const state = ensureSeed([sid])
	const key = makeKey(sid, date, slot)
	const rec = state.slots[key]
	if (!rec) return { ok: true }
	rec.booked = Math.max(0, rec.booked - n)
	state.slots[key] = rec
	state.updatedAt = Date.now()
	writeState(state)
	return { ok: true, remain: rec.capacity - rec.booked }
}

function readBookings() {
	try {
		const raw = uni.getStorageSync(BOOKINGS_KEY)
		if (Array.isArray(raw)) return raw
	} catch (e) {}
	return []
}

export function listBookings() {
	return readBookings()
}

/** 开发调试：清空本地库存后重新播种 */
export function resetInventory(storeIds) {
	try {
		uni.removeStorageSync(STORAGE_KEY)
		uni.removeStorageSync(BOOKINGS_KEY)
	} catch (e) {}
	return ensureSeed(storeIds)
}
