<template>
	<page-meta :page-style="'overflow:' + (successVisible ? 'hidden' : 'visible')"></page-meta>
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
				<view class="success-btn" @tap="onClaimPoints">
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
	const WEEK_CN = ['日', '一', '二', '三', '四', '五', '六']
	const STORAGE_KEY = 'checkin_makeup_claimed_date'

	function todayKey() {
		const n = new Date()
		return n.getFullYear() + '-' + String(n.getMonth() + 1).padStart(2, '0') + '-' + String(n.getDate()).padStart(2, '0')
	}

	export default {
		data() {
			return {
				signedToday: true,
				monthPoints: 2,
				signedDays: 1,
				makeupDay: 18,
				makeupClaimed: false,
				successVisible: false,
				weeks: ['日', '一', '二', '三', '四', '五', '六'],
				milestones: [
					{ label: '签到5天', points: 2 },
					{ label: '签到15天', points: 15 },
					{ label: '签到25天', points: 25 },
					{ label: '整月满签', points: 30 }
				],
				dayNum: '',
				dateLabel: '',
				monthTitle: '',
				calendarCells: []
			}
		},
		onLoad(options) {
			this.refreshClaimed()
			this.buildCalendar(new Date())
			if (options && String(options.fromMakeup) === '1') {
				this.handleShareEntry()
			}
		},
		onShow() {
			this.refreshClaimed()
			this.buildCalendar(new Date())
		},
		methods: {
			refreshClaimed() {
				this.makeupClaimed = uni.getStorageSync(STORAGE_KEY) === todayKey()
			},
			markClaimed() {
				uni.setStorageSync(STORAGE_KEY, todayKey())
				this.makeupClaimed = true
			},
			handleShareEntry() {
				this.markClaimed()
				this.successVisible = true
				this.buildCalendar(new Date())
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
					let mark = ''
					let markText = ''
					if (day === d) {
						mark = 'today'
						markText = '今'
					} else if (day === this.makeupDay && day < d) {
						mark = this.makeupClaimed ? 'done' : 'makeup'
						markText = '补'
					}
					cells.push({ day, mark, markText })
				}
				while (cells.length % 7 !== 0) {
					cells.push({ day: 0, mark: '', markText: '' })
				}
				this.calendarCells = cells
				this.signedDays = this.makeupClaimed ? 2 : 1
			},
			onRules() {
				uni.showModal({
					title: '签到规则',
					content: '每日签到可领取积分，连续签到可解锁额外奖励。漏签可用补签机会补回，每日仅一次。',
					showCancel: false
				})
			},
			onDayTap(cell) {
				if (cell.mark === 'makeup') {
					this.onMakeup()
				} else if (cell.mark === 'done') {
					uni.showToast({ title: '已领取补签', icon: 'none' })
				}
			},
			onMakeup() {
				if (this.makeupClaimed) {
					uni.showToast({ title: '已领取补签', icon: 'none' })
					return
				}
				uni.navigateTo({ url: '/pages/checkin/share' })
			},
			closeSuccess() {
				this.successVisible = false
			},
			onClaimPoints() {
				this.successVisible = false
				uni.reLaunch({ url: '/pages/video/video' })
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
		background: linear-gradient(180deg, #ff565c 0%, #ff8a5c 28%, #ffc08a 55%, #ffe8d0 78%, #fff8f2 100%);
	}

	.hero-card,
	.cal-card {
		position: relative;
		background: #ffffff;
		border-radius: 24rpx;
		box-shadow: 0 8rpx 24rpx rgba(200, 60, 40, 0.12);
	}

	.hero-card {
		margin-top: 28rpx;
		padding: 48rpx 36rpx 40rpx;
		overflow: hidden;
		background: linear-gradient(135deg, #fff8f6 0%, #ffe8e0 55%, #ffe0d4 100%);
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
		border-radius: 32rpx;
		background: #fff0ee;
		border: 2rpx solid #f0b0a8;
		color: #8a3a36;
		font-size: 30rpx;
		font-weight: 600;
	}

	.rules {
		margin-top: 16rpx;
		display: flex;
		align-items: center;
		font-size: 24rpx;
		color: #8a3a36;
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
		background: linear-gradient(90deg, #ff9a4a, #ff7a3a);
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
		color: #e84a3a;
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
		color: #e84a3a;
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
		background: #e84a3a;
	}

	.day-mark.makeup {
		background: transparent;
		border: 3rpx dashed #ff8a3a;
		box-sizing: border-box;
	}

	.day-mark.makeup text {
		color: #ff8a3a;
	}

	.day-mark.done {
		background: #ff8a3a;
	}

	.today-bar {
		width: 28rpx;
		height: 6rpx;
		border-radius: 3rpx;
		background: #e84a3a;
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
		border-radius: 28rpx;
		background: linear-gradient(180deg, #ff8a7a 0%, #f25b4a 100%);
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
		border-radius: 16rpx;
		background: linear-gradient(90deg, #ff9a4a, #ff7a3a);
		box-shadow: 0 8rpx 20rpx rgba(255, 120, 50, 0.35);
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
		border-radius: 16rpx;
		background: linear-gradient(90deg, #ff9a4a, #ff7a3a);
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
