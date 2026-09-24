<template>
	<page-meta :page-style="'overflow:' + (successVisible ? 'hidden' : 'visible')"></page-meta>
	<app-loading />
	<view class="page">
		<view class="hero-card">
			<image class="ring ring-l" src="/static/checkin/ring.png" mode="aspectFit" />
			<image class="ring ring-r" src="/static/checkin/ring.png" mode="aspectFit" />
			<image class="hero-deco" src="/static/checkin/top-deco.png" mode="widthFix" />
			<view class="hero-body">
				<view class="hero-left">
					<text class="hero-day">{{ dayNum }}</text>
					<text class="hero-date">{{ dateLabel }}</text>
				</view>
				<view class="hero-right">
					<view class="status-pill" :class="{ done: signedToday }">
						<text>{{ signedToday ? '今日已签' : '今日签到' }}</text>
					</view>
					<view class="rules" @tap="onRules">
						<text>查看规则</text>
						<text class="rules-arrow">›</text>
					</view>
				</view>
			</view>
		</view>

		<view class="milestones">
			<view v-for="item in milestones" :key="item.label" class="mile-card">
				<text class="mile-label">{{ item.label }}</text>
				<view class="mile-points">
					<text class="mile-plus">+{{ item.points }}</text>
					<text class="mile-unit">积分</text>
				</view>
			</view>
		</view>

		<view class="month-got">
			<text>本月已领取 </text>
			<text class="got-num">{{ monthPoints }}</text>
			<text> 积分</text>
		</view>

		<view class="cal-card">
			<image class="ring ring-l" src="/static/checkin/ring.png" mode="aspectFit" />
			<image class="ring ring-r" src="/static/checkin/ring.png" mode="aspectFit" />
			<view class="cal-head">
				<text class="cal-month">{{ monthTitle }}</text>
				<view class="cal-count">
					<text>您已签到 </text>
					<text class="got-num">{{ signedDays }}</text>
					<text> 天</text>
				</view>
			</view>
			<view class="cal-table">
				<view class="week-row">
					<view v-for="(w, i) in weeks" :key="'w' + i" class="cal-cell week-cell">
						<text>{{ w }}</text>
					</view>
				</view>
				<view class="day-grid">
					<view
						v-for="(cell, index) in calendarCells"
						:key="'d' + index"
						class="cal-cell day-cell"
						:class="{ 'tap-busy': cell.mark === 'today' && isTapBusy('checkin') }"
						@tap="onDayTap(cell)"
					>
						<template v-if="cell.day">
							<view
								v-if="cell.mark"
								class="day-mark"
								:class="cell.mark"
							>
								<text>{{ cell.markText }}</text>
							</view>
							<text v-else class="day-num">{{ cell.day }}</text>
							<view v-if="cell.mark === 'today'" class="today-bar" />
						</template>
					</view>
				</view>
			</view>
		</view>

		<view class="more-fixed" @tap="goVideo">
			<image class="more-gift" src="/static/checkin/more-gift.png" mode="widthFix" />
			<view class="more-btn">
				<text>更多积分</text>
			</view>
		</view>

		<template v-if="!makeupClaimed">
			<view class="makeup-btn" @tap="onMakeup">
				<text>赠送您一次补签的机会，点击领取</text>
			</view>
			<text class="makeup-tip">每日仅有一次补签机会</text>
		</template>

		<view
			v-if="successVisible"
			class="success-mask"
			@touchmove.stop.prevent="preventTouchMove"
		>
			<view class="success-dialog" @tap.stop>
				<image class="success-icon" src="/static/checkin/success-icon.png" mode="aspectFit" />
				<text class="success-title">恭喜您成功补签</text>
				<view class="success-btn" :class="{ 'tap-busy': isTapBusy('claim') }" @tap="onClaimPoints">
					<text>点击领取一大波积分</text>
				</view>
			</view>
			<view class="success-close" @tap="closeSuccess">
				<text>×</text>
			</view>
		</view>
	</view>
</template>

<script>
	import { api } from '../../common/api.js'
	import { isLoggedIn, silentLogin, refreshProfile, getUser, saveLogin, getOpenid } from '../../common/auth.js'

	const WEEK_CN = ['日', '一', '二', '三', '四', '五', '六']
	const STORAGE_KEY = 'checkin_makeup_claimed_date'

	function todayKey() {
		const n = new Date()
		return n.getFullYear() + '-' + String(n.getMonth() + 1).padStart(2, '0') + '-' + String(n.getDate()).padStart(2, '0')
	}

	export default {
		data() {
			return {
				signedToday: false,
				monthPoints: 0,
				signedDays: 0,
				makeupDay: 0,
				makeupClaimed: false,
				successVisible: false,
				signedDates: [],
				weeks: ['日', '一', '二', '三', '四', '五', '六'],
				milestones: [
					{ label: '签到5天', points: 2 },
					{ label: '签到15天', points: 15 },
					{ label: '签到25天', points: 25 },
					{ label: '整月满签', points: 30 }
				],
				dailyPoints: 2,
				rulesText: '每日签到可领取积分，当月累计签到可解锁额外奖励。漏签可用补签机会补回，每日仅一次。',
				dayNum: '',
				dateLabel: '',
				monthTitle: '',
				calendarCells: []
			}
		},
		onLoad(options) {
			this.refreshClaimed()
			this.buildCalendar(new Date())
			this.loadMonth()
			if (options && String(options.fromMakeup) === '1') {
				this.handleShareEntry()
			}
		},
		onShow() {
			this.refreshClaimed()
			this.loadMonth()
		},
		methods: {
			refreshClaimed() {
				this.makeupClaimed = uni.getStorageSync(STORAGE_KEY) === todayKey()
			},
			markClaimed() {
				uni.setStorageSync(STORAGE_KEY, todayKey())
				this.makeupClaimed = true
			},
			async ensureLogin() {
				if (!isLoggedIn()) await silentLogin()
			},
			applyConfig(cfg) {
				if (!cfg || typeof cfg !== 'object') return
				if (cfg.dailyPoints != null) this.dailyPoints = Number(cfg.dailyPoints) || 0
				if (cfg.rules) this.rulesText = cfg.rules
				if (Array.isArray(cfg.milestones) && cfg.milestones.length) {
					this.milestones = cfg.milestones.map((m) => ({
						label: m.label || ('签到' + (m.days || '') + '天'),
						points: Number(m.points) || 0
					}))
				}
			},
			async loadMonth() {
				await this.ensureLogin()
				const now = new Date()
				try {
					const res = await api.checkinMonth(now.getFullYear(), now.getMonth() + 1)
					this.signedDates = res.dates || []
					this.signedDays = res.signedDays || this.signedDates.length
					this.monthPoints = res.monthPoints || 0
					this.signedToday = this.signedDates.indexOf(todayKey()) >= 0
					this.applyConfig(res.config)
					const makeup = res.makeup || {}
					this.makeupClaimed = !!makeup.claimedToday
					if (makeup.targetDate) {
						const parts = String(makeup.targetDate).split('-')
						this.makeupDay = parts.length === 3 ? Number(parts[2]) : 0
					} else {
						this.makeupDay = 0
					}
					this.buildCalendar(now)
				} catch (e) {
					this.buildCalendar(now)
				}
			},
			handleShareEntry() {
				this.successVisible = true
			},
			buildCalendar(now) {
				const y = now.getFullYear()
				const m = now.getMonth()
				const d = now.getDate()
				this.dayNum = String(d)
				this.dateLabel = y + '/' + String(m + 1).padStart(2, '0') + '/星期' + WEEK_CN[now.getDay()]
				this.monthTitle = y + '年' + String(m + 1).padStart(2, '0') + '月'

				const first = new Date(y, m, 1)
				const daysInMonth = new Date(y, m + 1, 0).getDate()
				const start = first.getDay()
				const cells = []
				for (let i = 0; i < start; i++) {
					cells.push({ day: 0, mark: '', markText: '' })
				}
				for (let day = 1; day <= daysInMonth; day++) {
					const key =
						y + '-' + String(m + 1).padStart(2, '0') + '-' + String(day).padStart(2, '0')
					let mark = ''
					let markText = ''
					if (this.signedDates.indexOf(key) >= 0) {
						mark = 'done'
						markText = '✓'
					}
					if (day === d) {
						mark = this.signedToday ? 'done' : 'today'
						markText = this.signedToday ? '✓' : '今'
					} else if (!mark && day === this.makeupDay && day < d) {
						mark = this.makeupClaimed ? 'done' : 'makeup'
						markText = '补'
					}
					cells.push({ day, mark, markText, key })
				}
				while (cells.length % 7 !== 0) {
					cells.push({ day: 0, mark: '', markText: '' })
				}
				this.calendarCells = cells
				if (!this.signedDays) {
					this.signedDays = this.signedDates.length || (this.makeupClaimed ? 2 : this.signedToday ? 1 : 0)
				}
			},
			onRules() {
				uni.showModal({
					title: '签到规则',
					content: this.rulesText || '每日签到可领取积分，当月累计签到可解锁额外奖励。漏签可用补签机会补回，每日仅一次。',
					showCancel: false
				})
			},
			onDayTap(cell) {
				if (cell.mark === 'makeup') {
					this.onMakeup()
					return
				}
				if (cell.mark === 'today' && !this.signedToday) {
					this.doCheckin(false)
					return
				}
				if (cell.mark === 'done') {
					uni.showToast({ title: '已签到', icon: 'none' })
				}
			},
			async doCheckin(makeup) {
				const key = makeup ? 'claim' : 'checkin'
				return this.tapGuard(key, async () => {
				await this.ensureLogin()
				try {
					const res = await api.checkin(!!makeup)
					const data = (res && res.data) || {}
					if (res && res.ok === false && !makeup) {
						uni.showToast({ title: res.message || '今日已签到', icon: 'none' })
						this.loadMonth()
						return
					}
					if (data.balance != null) {
						const user = getUser()
						user.points = data.balance
						saveLogin(user, getOpenid())
					}
					uni.showToast({
						title: '签到成功 +' + (data.points != null ? data.points : this.dailyPoints),
						icon: 'success'
					})
					this.loadMonth()
					await refreshProfile()
				} catch (e) {
					uni.showToast({ title: (e && e.message) || '签到失败', icon: 'none' })
				}
				})
			},
			onMakeup() {
				if (this.makeupClaimed) {
					uni.showToast({ title: '今日已补签', icon: 'none' })
					return
				}
				if (!this.makeupDay) {
					uni.showToast({ title: '暂无可补签日期', icon: 'none' })
					return
				}
				uni.navigateTo({ url: '/pages/checkin/share' })
			},
			closeSuccess() {
				this.successVisible = false
			},
			async onClaimPoints() {
				this.successVisible = false
				await this.doCheckin(true)
			},
			preventTouchMove() {},
			goVideo() {
				uni.reLaunch({ url: '/pages/video/video' })
			}
		}
	}
</script>

<style>
	.page {
		min-height: 100vh;
		box-sizing: border-box;
		padding: 24rpx 28rpx calc(48rpx + env(safe-area-inset-bottom));
		background: #F1EEE8;
	}

	.hero-card,
	.cal-card {
		position: relative;
		background: #ffffff;
		border-radius: 12rpx;
		box-shadow: none;
		border: 1rpx solid #E8E2DA;
	}

	.hero-card {
		margin-top: 28rpx;
		padding: 48rpx 36rpx 40rpx;
		overflow: hidden;
		background: #fff;
	}

	.ring {
		position: absolute;
		top: -18rpx;
		width: 36rpx;
		height: 36rpx;
		z-index: 2;
	}

	.ring-l {
		left: 72rpx;
	}

	.ring-r {
		right: 72rpx;
	}

	.hero-deco {
		position: absolute;
		right: -20rpx;
		bottom: -10rpx;
		width: 280rpx;
		opacity: 0.85;
		pointer-events: none;
		z-index: 0;
	}

	.hero-body {
		position: relative;
		z-index: 1;
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.hero-day {
		font-size: 96rpx;
		font-weight: 700;
		color: #2a2a2a;
		line-height: 1;
	}

	.hero-date {
		display: block;
		margin-top: 8rpx;
		font-size: 28rpx;
		color: #333;
	}

	.hero-right {
		display: flex;
		flex-direction: column;
		align-items: center;
		margin-right: 8rpx;
	}

	.status-pill {
		min-width: 168rpx;
		padding: 0 36rpx;
		height: 64rpx;
		line-height: 64rpx;
		text-align: center;
		border-radius: 10rpx;
		background: #F7F3EE;
		border: 2rpx solid #E8E2DA;
		color: #5C564F;
		font-size: 30rpx;
		font-weight: 600;
	}

	.rules {
		margin-top: 16rpx;
		display: flex;
		align-items: center;
		font-size: 24rpx;
		color: #8A847C;
	}

	.rules-arrow {
		margin-left: 4rpx;
		font-size: 28rpx;
		line-height: 1;
	}

	.milestones {
		margin-top: 24rpx;
		display: flex;
		justify-content: space-between;
	}

	.mile-card {
		width: 164rpx;
		background: #ffffff;
		border-radius: 16rpx;
		overflow: hidden;
		box-shadow: 0 6rpx 16rpx rgba(200, 80, 40, 0.1);
	}

	.mile-label {
		display: block;
		text-align: center;
		font-size: 22rpx;
		color: #fff;
		background: #C6453C;
		line-height: 44rpx;
	}

	.mile-points {
		display: flex;
		align-items: baseline;
		justify-content: center;
		padding: 18rpx 0 20rpx;
	}

	.mile-plus {
		font-size: 36rpx;
		font-weight: 700;
		color: #C6453C;
	}

	.mile-unit {
		margin-left: 4rpx;
		font-size: 22rpx;
		color: #333;
	}

	.month-got {
		margin: 28rpx auto 0;
		padding: 10rpx 36rpx;
		border-radius: 28rpx;
		background: rgba(255, 236, 210, 0.95);
		font-size: 26rpx;
		color: #666;
		text-align: center;
		display: flex;
		align-items: center;
		justify-content: center;
		width: fit-content;
	}

	.got-num {
		color: #C6453C;
		font-weight: 700;
	}

	.cal-card {
		margin-top: 24rpx;
		padding: 44rpx 16rpx 32rpx;
		overflow: hidden;
	}

	.cal-head {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0 16rpx 20rpx;
	}

	.cal-month {
		font-size: 32rpx;
		font-weight: 700;
		color: #222;
	}

	.cal-count {
		font-size: 26rpx;
		color: #666;
		display: flex;
		align-items: center;
	}

	.cal-table {
		width: 100%;
	}

	.week-row,
	.day-grid {
		display: flex;
		flex-direction: row;
		flex-wrap: wrap;
		width: 100%;
	}

	.cal-cell {
		width: 14.28%;
		box-sizing: border-box;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
	}

	.week-cell {
		height: 56rpx;
	}

	.week-cell text {
		font-size: 26rpx;
		color: #c45a4a;
		font-weight: 500;
		line-height: 56rpx;
	}

	.day-cell {
		height: 80rpx;
	}

	.day-num {
		font-size: 28rpx;
		color: #333;
		line-height: 52rpx;
	}

	.day-mark {
		width: 52rpx;
		height: 52rpx;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.day-mark text {
		font-size: 26rpx;
		color: #fff;
		font-weight: 600;
		line-height: 1;
	}

	.day-mark.today {
		background: #C6453C;
	}

	.day-mark.makeup {
		background: transparent;
		border: 3rpx dashed #C4B5A8;
		box-sizing: border-box;
	}

	.day-mark.makeup text {
		color: #8A847C;
	}

	.day-mark.done {
		background: #A83632;
	}

	.today-bar {
		width: 28rpx;
		height: 6rpx;
		border-radius: 3rpx;
		background: #C6453C;
		margin-top: 4rpx;
	}

	.more-fixed {
		position: fixed;
		right: 20rpx;
		bottom: calc(230rpx + env(safe-area-inset-bottom));
		z-index: 80;
		width: 200rpx;
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.more-gift {
		width: 160rpx;
		margin-bottom: -18rpx;
		position: relative;
		z-index: 2;
	}

	.more-btn {
		position: relative;
		z-index: 3;
		min-width: 168rpx;
		padding: 0 28rpx;
		height: 56rpx;
		line-height: 52rpx;
		text-align: center;
		border-radius: 10rpx;
		background: #C6453C;
		border: 3rpx solid #ffffff;
		box-sizing: border-box;
	}

	.more-btn text {
		color: #fff;
		font-size: 26rpx;
		font-weight: 600;
	}

	.makeup-btn {
		margin-top: 36rpx;
		height: 88rpx;
		border-radius: 10rpx;
		background: #C6453C;
		box-shadow: none;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.makeup-btn text {
		color: #fff;
		font-size: 30rpx;
		font-weight: 600;
	}

	.makeup-tip {
		display: block;
		margin-top: 18rpx;
		text-align: center;
		font-size: 24rpx;
		color: #b09080;
	}

	.success-mask {
		position: fixed;
		left: 0;
		right: 0;
		top: 0;
		bottom: 0;
		z-index: 200;
		background: rgba(0, 0, 0, 0.55);
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 0 72rpx;
	}

	.success-dialog {
		width: 100%;
		background: #ffffff;
		border-radius: 24rpx;
		padding: 48rpx 40rpx 40rpx;
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.success-icon {
		width: 220rpx;
		height: 190rpx;
	}

	.success-title {
		margin-top: 24rpx;
		font-size: 36rpx;
		font-weight: 700;
		color: #222;
	}

	.success-btn {
		margin-top: 48rpx;
		width: 100%;
		height: 88rpx;
		border-radius: 10rpx;
		background: #C6453C;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.success-btn text {
		color: #fff;
		font-size: 30rpx;
		font-weight: 600;
	}

	.success-close {
		margin-top: 36rpx;
		width: 64rpx;
		height: 64rpx;
		border-radius: 50%;
		border: 3rpx solid rgba(255, 255, 255, 0.85);
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.success-close text {
		color: #fff;
		font-size: 44rpx;
		line-height: 1;
		margin-top: -4rpx;
	}
</style>
