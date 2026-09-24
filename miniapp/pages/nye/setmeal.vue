<template>
	<page-meta :page-style="'overflow:' + (stewardVisible || calendarVisible || couponVisible ? 'hidden' : 'visible')"></page-meta>
	<app-loading />
	<view v-if="detail" class="page">
		<view class="sec">
			<view class="sec-title">
				<view class="mark" />
				<text>选择规格</text>
			</view>
			<view
				v-for="item in packages"
				:key="item.id"
				class="spec"
				:class="{ on: item.id === specId, off: item.disabled }"
				@tap="pickSpec(item)"
			>
				<text class="spec-name">{{ item.name }}</text>
				<text class="spec-price">¥{{ item.price }}起</text>
			</view>
		</view>

		<view class="sec">
			<view class="row" @tap="includeOpen = !includeOpen">
				<view class="sec-title">
					<view class="mark" />
					<text>已包含</text>
				</view>
				<view class="more">
					<text>{{ includeOpen ? '收起' : '展开' }}</text>
					<view class="chev" :class="{ up: includeOpen }" />
				</view>
			</view>
			<view v-if="includeOpen && current" class="include">
				<view class="inc-card" :key="current.id">
					<image class="inc-cover" :src="current.cover || detail.cover" mode="aspectFill" />
					<view class="inc-cap">
						<view class="inc-line">【{{ current.time }}】</view>
						<view class="inc-line">{{ current.meal }}</view>
					</view>
				</view>
			</view>
		</view>

		<view class="sec">
			<view class="row">
				<view class="sec-title">
					<view class="mark" />
					<text>选择数量</text>
				</view>
				<view class="stepper">
					<view class="step" :class="{ mute: quantity <= 1 }" @tap="changeQty(-1)">－</view>
					<text class="step-num">{{ quantity }}</text>
					<view class="step" @tap="changeQty(1)">＋</view>
				</view>
			</view>
		</view>

		<view class="sec">
			<view class="row" @tap="openCalendar">
				<view class="sec-title">
					<view class="mark" />
					<text>选择日期</text>
				</view>
				<view class="date">
					<text>{{ dateText }}</text>
					<view class="arrow" />
				</view>
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
				<input class="input" v-model="phone" type="number" maxlength="11" placeholder="请输入联系方式" placeholder-class="ph" />
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
				<input class="input" v-model="remark" placeholder="请输入" placeholder-class="ph" />
			</view>
		</view>

		<view class="points">
			<view class="mark" />
			<text>本单预计获取<text class="points-num">{{ points }}</text>积分</text>
		</view>

		<view class="bar">
			<view class="service" @tap.stop="openSteward">
				<image src="/static/icons/service.png" mode="aspectFit" />
				<text>客服</text>
			</view>
			<text class="total">¥{{ total }}</text>
			<view class="pay" :class="{ 'tap-busy': isTapBusy('pay') }" @tap="onPay">立即支付</view>
		</view>

		<steward-dialog :visible="stewardVisible" @close="closeSteward" />
		<coupon-dialog
			:visible="couponVisible"
			@know="onCouponKnow"
			@go="onCouponGo"
			@close="closeCoupon"
		/>

		<view v-if="calendarVisible" class="cal-mask" @tap="closeCalendar">
			<view class="cal-sheet" @tap.stop>
				<view class="cal-head">
					<text class="cal-title">选择日期</text>
					<text class="cal-later" @tap="deferDate">稍后再选</text>
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
						<view class="cal-box" :class="{ on: cell.key === draftDate, off: cell.muted || cell.full }">
							<text class="cal-day">{{ cell.day }}</text>
							<text v-if="cell.open && cell.full" class="cal-price muted">已满</text>
							<text v-else-if="cell.open && cell.remainText" class="cal-price">{{ cell.remainText }}</text>
							<text v-else-if="cell.open" class="cal-price">¥{{ cell.price }}</text>
						</view>
					</view>
				</view>
				<view class="cal-ok" @tap="confirmDate">确认</view>
			</view>
		</view>
	</view>
</template>

<script>
	import { api, settlePay } from '../../common/api.js'
	import { isLoggedIn, silentLogin, getUser } from '../../common/auth.js'

	export default {
		data() {
			return {
				detail: null,
				packages: [],
				specId: 1,
				includeOpen: false,
				quantity: 1,
				people: 12,
				date: '',
				dateDeferred: false,
				name: '',
				phone: '',
				remark: '',
				stewardVisible: false,
				couponVisible: false,
				couponHintShown: false,
				calendarVisible: false,
				viewYear: 2027,
				viewMonth: 2,
				draftDate: '',
				monthMap: {},
				weeks: ['日', '一', '二', '三', '四', '五', '六'],
				loyalty: null
			}
		},
		computed: {
			current() {
				return this.packages.find((item) => item.id === this.specId) || this.packages[0] || null
			},
			roomSlot() {
				const cur = this.current
				if (!cur) return 'dinner'
				const text = String(cur.name || '') + String(cur.time || '')
				if (text.indexOf('晚') >= 0 || text.indexOf('17:') >= 0) return 'dinner'
				return 'lunch'
			},
			total() {
				return this.current ? this.current.price * this.quantity : 0
			},
			points() {
				const amt = this.total || 0
				if (amt <= 0) return 0
				const cfg = this.loyalty || {}
				const user = getUser() || {}
				const level = String(user.vipLevel || user.vip_level || 'V0').toUpperCase()
				let rate = Number(cfg.earnRateDefault != null ? cfg.earnRateDefault : 0.5)
				if (level === 'V3') rate = Number(cfg.earnRateV3 != null ? cfg.earnRateV3 : 1)
				const bday = String(user.birthday || '')
				const now = new Date()
				const bm = bday.length >= 7 ? parseInt(bday.slice(5, 7), 10) : 0
				if (bm && bm === now.getMonth() + 1) {
					rate *= Number(cfg.birthdayMultiplier != null ? cfg.birthdayMultiplier : 2)
				}
				return Math.max(0, Math.round(amt * rate))
			},
			dateText() {
				if (this.date) return this.date
				if (this.dateDeferred) return '以后再选'
				return '立即选择'
			},
			calendarCells() {
				const year = this.viewYear
				const month = this.viewMonth
				const price = this.current ? this.current.price : 0
				const slot = this.roomSlot
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
					const open = this.isNyeOpenDate(key)
					let full = false
					let remainText = ''
					if (open) {
						const dayInfo = map[key]
						const avail = dayInfo && dayInfo[slot]
						if (avail) {
							full = !!avail.full
							remainText = full ? '已满' : '剩' + (avail.remain || 0)
						}
					}
					cells.push({
						key,
						day: d,
						muted: !open || full,
						open,
						full,
						remainText,
						price
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
			const id = (query && query.id) || ''
			api.loyaltyConfig().then((cfg) => {
				this.loyalty = cfg || null
			}).catch(() => {})
			if (!id) {
				uni.showToast({ title: '加载失败', icon: 'none' })
				setTimeout(() => {
					uni.navigateBack({ fail() {} })
				}, 400)
				return
			}
			api
				.nyeDetail(id)
				.then((res) => {
					if (!res) {
						uni.showToast({ title: '加载失败', icon: 'none' })
						setTimeout(() => {
							uni.navigateBack({ fail() {} })
						}, 400)
						return
					}
					this.detail = {
						id: res.id,
						storeId: res.storeId || res.id,
						name: res.name,
						cover: res.cover,
						price: res.price,
						address: res.address,
						route: res.route,
						lat: res.lat,
						lng: res.lng,
						banners: res.banners || [],
						detailImages: res.detailImages || [],
						openStart: res.openStart || '',
						openEnd: res.openEnd || ''
					}
					this.packages = Array.isArray(res.packages) ? res.packages : []
					const ok = this.packages.find((item) => !item.disabled)
					if (ok) {
						this.specId = ok.id
						this.people = ok.people
					}
					if (this.detail.openStart) {
						const parts = String(this.detail.openStart).split('-')
						if (parts.length >= 2) {
							this.viewYear = Number(parts[0]) || this.viewYear
							this.viewMonth = Number(parts[1]) || this.viewMonth
						}
					}
				})
				.catch(() => {
					uni.showToast({ title: '加载失败', icon: 'none' })
					setTimeout(() => {
						uni.navigateBack({ fail() {} })
					}, 400)
				})
		},
		methods: {
			isNyeOpenDate(key) {
				const start = (this.detail && this.detail.openStart) || ''
				const end = (this.detail && this.detail.openEnd) || ''
				if (!key || !start || !end) return false
				return key >= start && key <= end
			},
			async loadMonthMap() {
				const storeId = (this.detail && (this.detail.storeId || this.detail.id)) || ''
				if (!storeId) {
					this.monthMap = {}
					return
				}
				try {
					const res = await api.roomMonth(storeId, this.viewYear, this.viewMonth)
					this.monthMap = res && typeof res === 'object' ? res : {}
				} catch (e) {
					this.monthMap = {}
					uni.showToast({ title: '加载失败', icon: 'none' })
				}
			},
			pickSpec(item) {
				if (item.disabled) {
					uni.showToast({ title: '当前规格已售罄～', icon: 'none' })
					return
				}
				this.specId = item.id
				this.people = item.people
				this.includeOpen = true
			},
			changeQty(step) {
				const next = this.quantity + step
				if (next < 1) return
				this.quantity = next
			},
			changePeople(step) {
				const next = this.people + step
				if (next < 1) return
				this.people = next
			},
			onPay() {
				if (!String(this.name || '').trim()) {
					uni.showToast({ title: '请填写姓名～', icon: 'none' })
					return
				}
				const phone = String(this.phone || '').trim()
				if (!phone) {
					uni.showToast({ title: '请填写联系方式～', icon: 'none' })
					return
				}
				if (!/^1\d{10}$/.test(phone)) {
					uni.showToast({ title: '请填写正确的联系方式～', icon: 'none' })
					return
				}
				if (!this.date && !this.dateDeferred) {
					uni.showToast({ title: '请选择日期～', icon: 'none' })
					return
				}
				if (this.people < 1) {
					uni.showToast({ title: '请填写预计人数～', icon: 'none' })
					return
				}
				// 原版：第一次点支付先出优惠券弹窗；知道了后再点才进支付
				if (!this.couponHintShown) {
					this.couponHintShown = true
					this.couponVisible = true
					return
				}
				this.continuePay()
			},
			async continuePay() {
				if (this.isTapBusy('pay')) return
				return this.tapGuard('pay', async () => {
				const productId = (this.detail && this.detail.id) || ''
				const roomStoreId = (this.detail && (this.detail.storeId || this.detail.id)) || ''
				const storeName = (this.detail && this.detail.name) || '天天俱乐部'
				const cur = this.current
				if (!cur || !productId) return

				if (this.date) {
					try {
						const avail = await api.roomAvailability(roomStoreId, this.date, this.roomSlot)
						if (avail && avail.full) {
							uni.showToast({ title: '该日期包房已满，请换一天', icon: 'none' })
							return
						}
					} catch (e) {
						uni.showToast({ title: '库存校验失败', icon: 'none' })
						return
					}
				}

				const amount = this.total
				let member = false
				try {
					if (!isLoggedIn()) await silentLogin()
					const profile = await api.profile()
					member = !!(profile && profile.isMember)
				} catch (e) {}
				const ok = await this.askModal({
					title: member ? '确认预约' : '确认支付',
					content: member
						? `会员免费预约，到店应收约 ¥${(amount * 0.9).toFixed(2)}（以门店对账为准）`
						: `需支付 ¥${amount}`,
					confirmText: member ? '确认预约' : '立即支付',
					confirmColor: '#C6453C'
				})
				if (!ok) return
				try {
					if (!isLoggedIn()) await silentLogin()
					const created = await api.createOrder({
						type: 'nye',
						store_id: productId,
						store_name: storeName,
						title: storeName,
						spec: cur.name + (this.date ? ' · ' + this.date : ''),
						cover: cur.cover || (this.detail && this.detail.cover) || '',
						quantity: this.quantity,
						price: amount,
						amount,
						package_id: String(cur.id || ''),
						contact_name: this.name,
						contact_phone: this.phone,
						people: this.people,
						remark: this.remark,
						room_date: this.date || '',
						room_slot: this.date ? this.roomSlot : ''
					})
					if (created && created.id && created.status === 'pending') {
						const payRes = await api.payOrder(created.id)
						await settlePay(payRes)
					}
					uni.showToast({ title: member ? '预约成功' : '支付成功', icon: 'success' })
					setTimeout(() => {
						uni.navigateTo({ url: '/pages/orders/orders' })
					}, 600)
				} catch (e) {
					uni.showToast({ title: (e && e.message) || '支付失败', icon: 'none' })
				}
				})
			},
			closeCoupon() {
				this.couponVisible = false
			},
			onCouponKnow() {
				this.couponVisible = false
			},
			onCouponGo() {
				this.couponVisible = false
				uni.navigateTo({ url: '/pages/mall/mall' })
			},
			pad2(n) {
				return String(n).padStart(2, '0')
			},
			openCalendar() {
				if (this.date) {
					const parts = this.date.split('-')
					this.viewYear = Number(parts[0])
					this.viewMonth = Number(parts[1])
					this.draftDate = this.date
				} else if (this.detail && this.detail.openStart) {
					const parts = String(this.detail.openStart).split('-')
					this.viewYear = Number(parts[0]) || this.viewYear
					this.viewMonth = Number(parts[1]) || this.viewMonth
					this.draftDate = this.detail.openStart
				} else {
					const now = new Date()
					this.viewYear = now.getFullYear()
					this.viewMonth = now.getMonth() + 1
					this.draftDate = ''
				}
				this.loadMonthMap()
				this.calendarVisible = true
			},
			closeCalendar() {
				this.calendarVisible = false
			},
			deferDate() {
				this.date = ''
				this.dateDeferred = true
				this.calendarVisible = false
			},
			shiftMonth(step) {
				let month = this.viewMonth + step
				let year = this.viewYear
				if (month < 1) {
					month = 12
					year -= 1
				} else if (month > 12) {
					month = 1
					year += 1
				}
				this.viewYear = year
				this.viewMonth = month
				this.loadMonthMap()
			},
			pickDate(cell) {
				if (!cell.open || cell.full) {
					uni.showToast({ title: cell.full ? '该日期包房已满' : '该日期不可选择', icon: 'none' })
					return
				}
				this.draftDate = cell.key
			},
			confirmDate() {
				if (!this.draftDate) return
				this.date = this.draftDate
				this.dateDeferred = false
				this.calendarVisible = false
			},
			openSteward() {
				this.stewardVisible = true
			},
			closeSteward() {
				this.stewardVisible = false
			}
		}
	}
</script>

<style>
	.page {
		min-height: 100vh;
		background: #fff;
		padding: 12rpx 28rpx calc(160rpx + env(safe-area-inset-bottom));
		box-sizing: border-box;
	}

	.sec {
		margin-top: 28rpx;
	}

	.sec-title {
		display: flex;
		align-items: center;
	}

	.sec-title text {
		font-size: 34rpx;
		font-weight: 700;
		color: #222;
	}

	.mark {
		width: 8rpx;
		height: 32rpx;
		border-radius: 4rpx;
		background: #c4a06a;
		margin-right: 14rpx;
		flex-shrink: 0;
	}

	.spec {
		margin-top: 20rpx;
		min-height: 88rpx;
		padding: 20rpx 24rpx;
		border-radius: 12rpx;
		border: 2rpx solid #e6e6e6;
		background: #fff;
		display: flex;
		align-items: center;
		box-sizing: border-box;
	}

	.spec.on {
		background: #C6453C;
		border-color: #C6453C;
	}

	.spec.off {
		background: #f3f3f3;
		border-color: #f3f3f3;
	}

	.spec-name {
		flex: 1;
		min-width: 0;
		font-size: 28rpx;
		color: #333;
		line-height: 1.4;
	}

	.spec-price {
		margin-left: 16rpx;
		font-size: 28rpx;
		color: #333;
		flex-shrink: 0;
	}

	.spec.on .spec-name,
	.spec.on .spec-price {
		color: #fff;
	}

	.spec.off .spec-name,
	.spec.off .spec-price {
		color: #c8c8c8;
	}

	.row {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.more {
		display: flex;
		align-items: center;
	}

	.more text {
		font-size: 26rpx;
		color: #c4a06a;
	}

	.chev {
		width: 12rpx;
		height: 12rpx;
		margin-left: 8rpx;
		border-right: 3rpx solid #c4a06a;
		border-bottom: 3rpx solid #c4a06a;
		transform: rotate(45deg);
		margin-top: -6rpx;
	}

	.chev.up {
		transform: rotate(-135deg);
		margin-top: 6rpx;
	}

	.include {
		margin-top: 20rpx;
	}

	.inc-card {
		width: 280rpx;
		border: 1rpx solid #e6e6e6;
		border-radius: 12rpx;
		overflow: hidden;
		background: #fff;
	}

	.inc-cover {
		width: 280rpx;
		height: 210rpx;
		display: block;
	}

	.inc-cap {
		background: #e9e8e7;
		padding: 16rpx 8rpx 18rpx;
		text-align: center;
	}

	.inc-line {
		font-size: 24rpx;
		color: #222;
		line-height: 1.45;
		text-align: center;
	}

	.stepper {
		display: flex;
		align-items: center;
	}

	.step {
		width: 44rpx;
		height: 44rpx;
		border-radius: 50%;
		border: 2rpx solid #333;
		color: #333;
		font-size: 28rpx;
		line-height: 40rpx;
		text-align: center;
	}

	.step.mute {
		border-color: #ddd;
		color: #ddd;
	}

	.step-num {
		min-width: 56rpx;
		text-align: center;
		font-size: 30rpx;
		color: #222;
	}

	.date {
		display: flex;
		align-items: center;
	}

	.date text {
		font-size: 28rpx;
		color: #c4a06a;
	}

	.arrow {
		width: 12rpx;
		height: 12rpx;
		margin-left: 8rpx;
		border-right: 3rpx solid #c4a06a;
		border-top: 3rpx solid #c4a06a;
		transform: rotate(45deg);
	}

	.form {
		padding-bottom: 8rpx;
	}

	.field {
		display: flex;
		align-items: center;
		justify-content: space-between;
		min-height: 96rpx;
		padding-left: 22rpx;
		border-bottom: 1rpx solid #eee;
		box-sizing: border-box;
	}

	.field.last {
		border-bottom: none;
	}

	.label {
		font-size: 30rpx;
		color: #333;
		flex-shrink: 0;
	}

	.input {
		flex: 1;
		margin-left: 24rpx;
		text-align: right;
		font-size: 30rpx;
		color: #222;
	}

	.ph {
		color: #ccc;
	}

	.points {
		display: flex;
		align-items: center;
		margin-top: 36rpx;
		font-size: 34rpx;
		font-weight: 700;
		color: #222;
	}

	.points-num {
		color: #C6453C;
	}

	.bar {
		position: fixed;
		left: 0;
		right: 0;
		bottom: 0;
		z-index: 40;
		display: flex;
		align-items: center;
		padding: 16rpx 24rpx calc(16rpx + env(safe-area-inset-bottom));
		background: #fff;
		box-shadow: 0 -2rpx 12rpx rgba(0, 0, 0, 0.05);
	}

	.service {
		width: 72rpx;
		flex-shrink: 0;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
	}

	.service image {
		width: 44rpx;
		height: 44rpx;
	}

	.service text {
		margin-top: 2rpx;
		font-size: 22rpx;
		color: #222;
		line-height: 1.2;
	}

	.total {
		flex: 1;
		min-width: 0;
		padding: 0 20rpx 0 8rpx;
		text-align: right;
		font-size: 44rpx;
		font-weight: 700;
		color: #C6453C;
		line-height: 1;
	}

	.pay {
		width: 300rpx;
		height: 84rpx;
		line-height: 84rpx;
		text-align: center;
		border-radius: 10rpx;
		background: #C6453C;
		color: #fff;
		font-size: 32rpx;
		font-weight: 600;
		flex-shrink: 0;
	}

	.cal-mask {
		position: fixed;
		left: 0;
		right: 0;
		top: 0;
		bottom: 0;
		z-index: 80;
		background: rgba(0, 0, 0, 0.45);
		display: flex;
		align-items: flex-end;
	}

	.cal-sheet {
		width: 100%;
		background: #fff;
		border-radius: 12rpx 12rpx 0 0;
		padding: 8rpx 28rpx calc(28rpx + env(safe-area-inset-bottom));
		box-sizing: border-box;
	}

	.cal-head {
		position: relative;
		height: 88rpx;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.cal-title {
		font-size: 32rpx;
		font-weight: 600;
		color: #222;
	}

	.cal-later {
		position: absolute;
		right: 0;
		font-size: 28rpx;
		color: #c4a06a;
	}

	.cal-nav {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-top: 8rpx;
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
		width: 104rpx;
		height: 108rpx;
		border-radius: 12rpx;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
	}

	.cal-box.on {
		background: #C6453C;
	}

	.cal-day {
		font-size: 34rpx;
		color: #222;
		line-height: 1.15;
	}

	.cal-price {
		margin-top: 4rpx;
		font-size: 22rpx;
		color: #C6453C;
		line-height: 1.1;
	}

	.cal-price.muted {
		color: #999;
	}

	.cal-box.off .cal-day {
		color: #d8d8d8;
	}

	.cal-box.on .cal-day,
	.cal-box.on .cal-price {
		color: #fff;
	}

	.cal-ok {
		margin-top: 16rpx;
		height: 88rpx;
		line-height: 88rpx;
		text-align: center;
		border-radius: 10rpx;
		background: #C6453C;
		color: #fff;
		font-size: 32rpx;
		font-weight: 600;
	}
</style>
