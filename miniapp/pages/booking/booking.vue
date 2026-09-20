<template>
	<page-meta :page-style="'overflow:' + (calendarVisible ? 'hidden' : 'visible')"></page-meta>
	<view class="page">
		<view class="sec">
			<view class="sec-title">
				<view class="mark" />
				<text>预约门店</text>
			</view>
			<view class="store-card">
				<image class="store-cover" :src="store.cover" mode="aspectFill" />
				<view class="store-info">
					<text class="store-name">{{ store.name }}</text>
					<text class="store-addr">{{ store.address }}</text>
				</view>
			</view>
		</view>

		<view class="sec">
			<view class="row" @tap="openCalendar">
				<view class="sec-title">
					<view class="mark" />
					<text>用餐日期</text>
				</view>
				<view class="date">
					<text>{{ date || '请选择日期' }}</text>
					<view class="arrow" />
				</view>
			</view>
		</view>

		<view class="sec">
			<view class="sec-title">
				<view class="mark" />
				<text>用餐时段</text>
			</view>
			<view class="slots">
				<view
					v-for="item in slots"
					:key="item.key"
					class="slot"
					:class="{ on: slot === item.key, full: slotInfo(item.key).full }"
					@tap="pickSlot(item)"
				>
					<text class="slot-name">{{ item.name }}</text>
					<text class="slot-time">{{ item.time }}</text>
					<text class="slot-remain" :class="{ danger: slotInfo(item.key).full || slotInfo(item.key).remain <= 2 }">
						{{ slotInfo(item.key).statusText }}
					</text>
				</view>
			</view>
			<view v-if="date && currentAvail" class="hint">
				<text v-if="currentAvail.full">该时段包房已满，请换日期或时段</text>
				<text v-else>当前还可预约 {{ currentAvail.remain }} 间包房（含电话预留后剩余）</text>
			</view>
		</view>

		<view class="sec form">
			<view class="sec-title">
				<view class="mark" />
				<text>联系人</text>
			</view>
			<view class="field">
				<text class="label">姓名</text>
				<input class="input" v-model="name" placeholder="请输入联系人姓名" placeholder-class="ph" />
			</view>
			<view class="field">
				<text class="label">联系方式</text>
				<input class="input" v-model="phone" type="number" maxlength="11" placeholder="请输入手机号" placeholder-class="ph" />
			</view>
			<view class="field">
				<text class="label">预计人数</text>
				<view class="stepper">
					<view class="step" :class="{ mute: people <= 1 }" @tap="changePeople(-1)">－</view>
					<text class="step-num">{{ people }}</text>
					<view class="step" @tap="changePeople(1)">＋</view>
				</view>
			</view>
			<view class="field last">
				<text class="label">备注</text>
				<input class="input" v-model="remark" placeholder="如包间偏好、忌口等" placeholder-class="ph" />
			</view>
		</view>

		<view class="tip">
			<text>说明：小程序下单成功后会锁定 1 间包房库存；电话预订由后台人工锁定。当前为本地演示数据，接入后台后自动同步。</text>
		</view>

		<view class="bar">
			<view class="bar-left">
				<text class="bar-label">包房</text>
				<text class="bar-val" :class="{ danger: !canSubmit }">{{ barStatus }}</text>
			</view>
			<view class="submit" :class="{ mute: !canSubmit }" @tap="onSubmit">提交预约</view>
		</view>

		<view v-if="calendarVisible" class="cal-mask" @tap="closeCalendar">
			<view class="cal-sheet" @tap.stop>
				<view class="cal-head">
					<text class="cal-title">选择日期</text>
					<text class="cal-close" @tap="closeCalendar">关闭</text>
				</view>
				<view class="cal-nav">
					<view class="cal-nav-btn" @tap="shiftMonth(-1)">上个月</view>
					<text class="cal-month">{{ viewYear }}年{{ pad2(viewMonth) }}月</text>
					<view class="cal-nav-btn" @tap="shiftMonth(1)">下个月</view>
				</view>
				<view class="cal-week">
					<text v-for="w in weeks" :key="w">{{ w }}</text>
				</view>
				<view class="cal-grid">
					<view v-for="cell in calendarCells" :key="cell.key" class="cal-cell" @tap="pickDate(cell)">
						<view class="cal-box" :class="{ on: cell.key === draftDate, off: cell.muted, full: cell.full }">
							<text class="cal-day">{{ cell.day }}</text>
							<text v-if="cell.open && !cell.muted" class="cal-remain" :class="{ danger: cell.full }">
								{{ cell.full ? '已满' : '剩' + cell.remain }}
							</text>
						</view>
					</view>
				</view>
				<view class="cal-ok" @tap="confirmDate">确认</view>
			</view>
		</view>
	</view>
</template>

<script>
	import {
		SLOTS,
		formatDate,
		getAvailability,
		getMonthAvailability,
		lockRooms,
		ensureInventory
	} from '../../common/room-inventory.js'
	import { prependOrder } from '../../common/orders-store.js'

	const STORE_MAP = {
		shibo: {
			id: 'shibo',
			name: '天天俱乐部上海世博店',
			cover: '/static/stores/shibo.png',
			address: '上海市浦东新区长清路92号 中邻上钢里3楼'
		},
		xinzhuang: {
			id: 'xinzhuang',
			name: '天天俱乐部上海莘庄店',
			cover: '/static/stores/xinzhuang.png',
			address: '上海市闵行区都市路5001号5楼'
		},
		yaxin: {
			id: 'yaxin',
			name: '天天俱乐部上海亚新店',
			cover: '/static/stores/yaxin.png',
			address: '上海市普陀区长寿路401号3号楼2楼'
		},
		gongkang: {
			id: 'gongkang',
			name: '天天俱乐部上海共康店',
			cover: '/static/stores/gongkang.png',
			address: '上海市宝山区共和新路5000弄绿地新都会1号楼二楼'
		},
		ningbo: {
			id: 'ningbo',
			name: '宁波天天俱乐部天一店',
			cover: '/static/stores/ningbo.png',
			address: '浙江省宁波市海曙区中山路220号第二百货商店7楼'
		}
	}

	export default {
		data() {
			const now = new Date()
			return {
				storeId: 'shibo',
				date: '',
				slot: 'dinner',
				name: '',
				phone: '',
				people: 8,
				remark: '',
				slots: SLOTS,
				calendarVisible: false,
				viewYear: now.getFullYear(),
				viewMonth: now.getMonth() + 1,
				draftDate: '',
				monthMap: {},
				weeks: ['日', '一', '二', '三', '四', '五', '六'],
				tick: 0
			}
		},
		computed: {
			store() {
				return STORE_MAP[this.storeId] || STORE_MAP.shibo
			},
			currentAvail() {
				this.tick
				if (!this.date) return null
				return getAvailability(this.storeId, this.date, this.slot)
			},
			canSubmit() {
				return !!(this.date && this.currentAvail && !this.currentAvail.full)
			},
			barStatus() {
				if (!this.date) return '请先选日期'
				if (!this.currentAvail) return '—'
				if (this.currentAvail.full) return '已满'
				return `剩余 ${this.currentAvail.remain} 间`
			},
			calendarCells() {
				this.tick
				const year = this.viewYear
				const month = this.viewMonth
				const map = this.monthMap || {}
				const firstWeek = new Date(year, month - 1, 1).getDay()
				const daysInMonth = new Date(year, month, 0).getDate()
				const prevDays = new Date(year, month - 1, 0).getDate()
				const cells = []
				for (let i = firstWeek; i > 0; i--) {
					cells.push({
						key: 'p-' + year + '-' + month + '-' + i,
						day: prevDays - i + 1,
						muted: true,
						open: false
					})
				}
				for (let d = 1; d <= daysInMonth; d++) {
					const key = year + '-' + this.pad2(month) + '-' + this.pad2(d)
					const info = map[key] || {}
					cells.push({
						key,
						day: d,
						muted: !info.open,
						open: !!info.open,
						full: !!info.full,
						remain: info.remain || 0
					})
				}
				let next = 1
				while (cells.length % 7 !== 0) {
					cells.push({
						key: 'n-' + year + '-' + month + '-' + next,
						day: next,
						muted: true,
						open: false
					})
					next++
				}
				return cells
			}
		},
		onLoad(query) {
			const id = (query && query.storeId) || 'shibo'
			this.storeId = STORE_MAP[id] ? id : 'shibo'
			ensureInventory(Object.keys(STORE_MAP))
			const tomorrow = new Date()
			tomorrow.setDate(tomorrow.getDate() + 1)
			this.date = formatDate(tomorrow)
			this.viewYear = tomorrow.getFullYear()
			this.viewMonth = tomorrow.getMonth() + 1
			this.refreshMonth()
			this.tick++
		},
		onShow() {
			this.refreshMonth()
			this.tick++
		},
		methods: {
			pad2(n) {
				return String(n).padStart(2, '0')
			},
			refreshMonth() {
				this.monthMap = getMonthAvailability(this.storeId, this.viewYear, this.viewMonth)
			},
			slotInfo(key) {
				this.tick
				if (!this.date) {
					return { remain: 0, full: false, statusText: '请先选日期' }
				}
				return getAvailability(this.storeId, this.date, key)
			},
			pickSlot(item) {
				this.slot = item.key
			},
			changePeople(step) {
				const next = this.people + step
				if (next < 1 || next > 30) return
				this.people = next
			},
			openCalendar() {
				if (this.date) {
					const parts = this.date.split('-')
					this.viewYear = Number(parts[0])
					this.viewMonth = Number(parts[1])
					this.draftDate = this.date
				} else {
					this.draftDate = ''
				}
				this.refreshMonth()
				this.calendarVisible = true
			},
			closeCalendar() {
				this.calendarVisible = false
			},
			shiftMonth(delta) {
				let y = this.viewYear
				let m = this.viewMonth + delta
				if (m < 1) {
					m = 12
					y -= 1
				} else if (m > 12) {
					m = 1
					y += 1
				}
				this.viewYear = y
				this.viewMonth = m
				this.refreshMonth()
			},
			pickDate(cell) {
				if (!cell.open || cell.muted) return
				this.draftDate = cell.key
			},
			confirmDate() {
				if (!this.draftDate) {
					uni.showToast({ title: '请选择日期', icon: 'none' })
					return
				}
				this.date = this.draftDate
				this.calendarVisible = false
				this.tick++
				const lunch = getAvailability(this.storeId, this.date, 'lunch')
				const dinner = getAvailability(this.storeId, this.date, 'dinner')
				if (this.slot === 'lunch' && lunch.full && !dinner.full) this.slot = 'dinner'
				if (this.slot === 'dinner' && dinner.full && !lunch.full) this.slot = 'lunch'
			},
			onSubmit() {
				if (!this.date) {
					uni.showToast({ title: '请选择日期', icon: 'none' })
					return
				}
				const avail = getAvailability(this.storeId, this.date, this.slot)
				if (avail.full) {
					uni.showToast({ title: '该时段包房已满', icon: 'none' })
					return
				}
				if (!String(this.name || '').trim()) {
					uni.showToast({ title: '请填写姓名', icon: 'none' })
					return
				}
				const phone = String(this.phone || '').trim()
				if (!/^1\d{10}$/.test(phone)) {
					uni.showToast({ title: '请填写正确手机号', icon: 'none' })
					return
				}

				const orderId = 'rb_' + Date.now()
				const slotMeta = SLOTS.find((s) => s.key === this.slot) || SLOTS[1]
				const result = lockRooms({
					storeId: this.storeId,
					date: this.date,
					slot: this.slot,
					qty: 1,
					orderId
				})
				if (!result.ok) {
					uni.showToast({ title: result.message || '预约失败', icon: 'none' })
					this.tick++
					return
				}

				prependOrder({
					id: orderId,
					type: 'room',
					storeId: this.storeId,
					storeName: this.store.name,
					status: 'paid',
					statusText: '待核销',
					cover: this.store.cover,
					title: `${this.store.name.replace('天天俱乐部', '')}-包房预约`,
					spec: `${this.date} ${slotMeta.name}（${slotMeta.time}）·${this.people}人`,
					quantity: 1,
					price: 0,
					amount: 0,
					roomDate: this.date,
					roomSlot: this.slot,
					contactName: this.name,
					contactPhone: phone,
					remark: this.remark
				})

				this.tick++
				uni.showToast({ title: '预约成功', icon: 'success' })
				setTimeout(() => {
					uni.navigateTo({ url: '/pages/orders/orders' })
				}, 600)
			}
		}
	}
</script>

<style>
	.page {
		min-height: 100vh;
		box-sizing: border-box;
		padding: 24rpx 24rpx calc(140rpx + env(safe-area-inset-bottom));
		background: #f5f5f5;
	}

	.sec {
		background: #fff;
		border-radius: 16rpx;
		padding: 28rpx 24rpx;
		margin-bottom: 20rpx;
	}

	.sec-title {
		display: flex;
		align-items: center;
		font-size: 30rpx;
		font-weight: 700;
		color: #222;
		margin-bottom: 20rpx;
	}

	.mark {
		width: 8rpx;
		height: 28rpx;
		border-radius: 4rpx;
		background: #e54148;
		margin-right: 12rpx;
	}

	.store-card {
		display: flex;
		gap: 20rpx;
	}

	.store-cover {
		width: 160rpx;
		height: 120rpx;
		border-radius: 12rpx;
		flex-shrink: 0;
		background: #eee;
	}

	.store-info {
		flex: 1;
		min-width: 0;
		display: flex;
		flex-direction: column;
		justify-content: center;
		gap: 12rpx;
	}

	.store-name {
		font-size: 28rpx;
		font-weight: 700;
		color: #222;
	}

	.store-addr {
		font-size: 24rpx;
		color: #888;
		line-height: 1.4;
	}

	.row {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.row .sec-title {
		margin-bottom: 0;
	}

	.date {
		display: flex;
		align-items: center;
		gap: 8rpx;
		font-size: 28rpx;
		color: #666;
	}

	.arrow {
		width: 14rpx;
		height: 14rpx;
		border-top: 3rpx solid #bbb;
		border-right: 3rpx solid #bbb;
		transform: rotate(45deg);
	}

	.slots {
		display: flex;
		gap: 20rpx;
	}

	.slot {
		flex: 1;
		border: 2rpx solid #e8e8e8;
		border-radius: 16rpx;
		padding: 24rpx 20rpx;
		display: flex;
		flex-direction: column;
		gap: 8rpx;
		background: #fafafa;
	}

	.slot.on {
		border-color: #e54148;
		background: #fff5f5;
	}

	.slot.full {
		opacity: 0.55;
	}

	.slot-name {
		font-size: 30rpx;
		font-weight: 700;
		color: #222;
	}

	.slot-time {
		font-size: 22rpx;
		color: #999;
	}

	.slot-remain {
		margin-top: 8rpx;
		font-size: 24rpx;
		color: #e54148;
		font-weight: 600;
	}

	.slot-remain.danger {
		color: #e54148;
	}

	.hint {
		margin-top: 20rpx;
		font-size: 24rpx;
		color: #888;
		line-height: 1.5;
	}

	.form .field {
		display: flex;
		align-items: center;
		min-height: 88rpx;
		border-bottom: 1rpx solid #f0f0f0;
	}

	.form .field.last {
		border-bottom: none;
	}

	.label {
		width: 160rpx;
		font-size: 28rpx;
		color: #333;
		flex-shrink: 0;
	}

	.input {
		flex: 1;
		font-size: 28rpx;
		color: #222;
	}

	.ph {
		color: #ccc;
	}

	.stepper {
		display: flex;
		align-items: center;
		gap: 24rpx;
		margin-left: auto;
	}

	.step {
		width: 52rpx;
		height: 52rpx;
		border-radius: 50%;
		border: 1rpx solid #ddd;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 32rpx;
		color: #333;
		background: #fff;
	}

	.step.mute {
		opacity: 0.35;
	}

	.step-num {
		min-width: 40rpx;
		text-align: center;
		font-size: 30rpx;
		color: #222;
	}

	.tip {
		padding: 8rpx 8rpx 24rpx;
		font-size: 22rpx;
		color: #aaa;
		line-height: 1.6;
	}

	.bar {
		position: fixed;
		left: 0;
		right: 0;
		bottom: 0;
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 16rpx 24rpx calc(16rpx + env(safe-area-inset-bottom));
		background: #fff;
		box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.06);
	}

	.bar-left {
		display: flex;
		flex-direction: column;
		gap: 4rpx;
	}

	.bar-label {
		font-size: 22rpx;
		color: #999;
	}

	.bar-val {
		font-size: 30rpx;
		font-weight: 700;
		color: #e54148;
	}

	.bar-val.danger {
		color: #999;
	}

	.submit {
		min-width: 280rpx;
		height: 80rpx;
		line-height: 80rpx;
		text-align: center;
		border-radius: 40rpx;
		background: #e54148;
		color: #fff;
		font-size: 30rpx;
		font-weight: 700;
	}

	.submit.mute {
		background: #ccc;
	}

	.cal-mask {
		position: fixed;
		inset: 0;
		background: rgba(0, 0, 0, 0.45);
		z-index: 100;
		display: flex;
		align-items: flex-end;
	}

	.cal-sheet {
		width: 100%;
		background: #fff;
		border-radius: 24rpx 24rpx 0 0;
		padding: 32rpx 28rpx calc(28rpx + env(safe-area-inset-bottom));
	}

	.cal-head {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.cal-title {
		font-size: 34rpx;
		font-weight: 700;
		color: #222;
	}

	.cal-close {
		font-size: 26rpx;
		color: #999;
	}

	.cal-nav {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-top: 28rpx;
	}

	.cal-nav-btn {
		min-width: 132rpx;
		height: 56rpx;
		line-height: 56rpx;
		text-align: center;
		border: 1rpx solid #e5e5e5;
		border-radius: 8rpx;
		font-size: 24rpx;
		color: #666;
	}

	.cal-month {
		font-size: 32rpx;
		font-weight: 700;
		color: #222;
	}

	.cal-week,
	.cal-grid {
		display: flex;
		flex-wrap: wrap;
	}

	.cal-week {
		margin-top: 28rpx;
	}

	.cal-week text,
	.cal-cell {
		width: 14.285%;
		text-align: center;
	}

	.cal-week text {
		font-size: 24rpx;
		color: #c8c8c8;
		line-height: 48rpx;
	}

	.cal-cell {
		height: 120rpx;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.cal-box {
		width: 88rpx;
		height: 100rpx;
		border-radius: 12rpx;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 4rpx;
	}

	.cal-box.on {
		background: #e54148;
	}

	.cal-box.on .cal-day,
	.cal-box.on .cal-remain {
		color: #fff;
	}

	.cal-box.off {
		opacity: 0.35;
	}

	.cal-box.full:not(.on) .cal-remain {
		color: #999;
	}

	.cal-day {
		font-size: 30rpx;
		font-weight: 600;
		color: #222;
	}

	.cal-remain {
		font-size: 20rpx;
		color: #e54148;
	}

	.cal-remain.danger {
		color: #999;
	}

	.cal-ok {
		margin-top: 24rpx;
		height: 80rpx;
		line-height: 80rpx;
		text-align: center;
		border-radius: 40rpx;
		background: #e54148;
		color: #fff;
		font-size: 30rpx;
		font-weight: 700;
	}
</style>
