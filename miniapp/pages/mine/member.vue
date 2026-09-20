<template>
	<page-meta :page-style="'overflow:' + (stewardVisible ? 'hidden' : 'visible')"></page-meta>
	<view class="page" :style="pageStyle">
		<image class="page-bg" :src="current.pageBgImage" mode="aspectFill" />
		<view class="page-shade" />

		<view class="navbar" :style="{ paddingTop: statusBarHeight + 'px' }">
			<view class="navbar-inner" :style="{ height: navBarHeight + 'px' }">
				<view class="back" @tap="goBack">
					<view class="back-arrow" />
				</view>
				<text class="nav-title">会员中心</text>
			</view>
		</view>

		<view class="top">
			<view class="avatar-block">
				<image
					class="avatar"
					:src="avatar || '/static/icons/avatar-default.png'"
					mode="aspectFill"
				/>
				<view class="lock-tag" :class="{ on: unlocked }">
					{{ unlocked ? '已解锁' : '未解锁' }}
				</view>
			</view>

			<view class="level-rail">
				<image class="rail-arc-img" src="/static/icons/member-rail-arc.png?v=4" mode="scaleToFill" />
				<view
					v-for="(lv, i) in levels"
					:key="lv.id"
					class="rail-item"
					:class="{ active: i === activeIndex }"
					:style="railStyle(i)"
					@tap="onRailTap(i)"
				>
					<view class="dot-wrap">
						<view class="dot" />
					</view>
					<text class="lv-name">{{ lv.id }}</text>
				</view>
			</view>
		</view>

		<swiper
			class="level-swiper"
			:current="activeIndex"
			previous-margin="40rpx"
			next-margin="40rpx"
			:duration="300"
			@change="onLevelSwipe"
		>
			<swiper-item v-for="lv in levels" :key="lv.id">
				<view class="level-card">
					<image class="card-bg" :src="lv.cardBgImage" mode="aspectFill" />
					<view class="card-left">
						<text class="lv-big" :style="{ color: lv.levelColor }">{{ lv.id }}</text>
						<text class="need" :style="{ color: lv.needColor }">{{ lv.needText }}</text>
						<view class="bar">
							<view
								v-if="cardProgress(lv) > 0"
								class="bar-fill"
								:style="{
									width: cardProgress(lv) + '%',
									background: lv.barColor,
									minWidth: cardProgress(lv) >= 28 ? '56rpx' : '0'
								}"
							>
								<text v-if="cardProgress(lv) >= 28" class="bar-pct">{{ cardProgress(lv) }}%</text>
							</view>
						</view>
						<text class="bar-tip" :style="{ color: lv.needColor }">
							{{
								lv.doneText
									? lv.progressLabel
									: lv.progressLabel + '：' + progress + '/' + lv.need
							}}
						</text>
					</view>
					<image class="crown-img" :src="lv.crownIcon" mode="aspectFit" />
				</view>
			</swiper-item>
		</swiper>

		<view class="sec-head">
			<view class="sec-lines">
				<view class="sec-line" :style="{ background: current.secLine }" />
				<view class="sec-line" :style="{ background: current.secLine }" />
				<view class="sec-line" :style="{ background: current.secLine }" />
			</view>
			<text class="sec-title">权益说明</text>
			<view class="sec-lines">
				<view class="sec-line" :style="{ background: current.secLine }" />
				<view class="sec-line" :style="{ background: current.secLine }" />
				<view class="sec-line" :style="{ background: current.secLine }" />
			</view>
			<text class="rules" @tap="onRules">{{ rulesLabel }}</text>
		</view>

		<view class="benefit-grid">
			<view
				v-for="(b, i) in current.benefits"
				:key="i"
				class="benefit"
				:style="{ background: current.benefitBg, borderColor: current.benefitBorder }"
			>
				<view class="b-icon">
					<image class="b-icon-img" :src="b.icon" mode="aspectFit" />
				</view>
				<view class="b-text">
					<text class="b-title">{{ b.title }}</text>
					<text class="b-desc">{{ b.desc }}</text>
				</view>
			</view>
		</view>

		<view
			class="coupon-box"
			:style="{ background: current.couponBg, borderColor: current.couponBorder }"
		>
			<view
				class="coupon-deco"
				:style="{
					background:
						'radial-gradient(ellipse at 20% 0%, ' +
						current.couponDeco +
						' 0%, transparent 55%), radial-gradient(ellipse at 80% 0%, ' +
						current.couponDeco +
						' 0%, transparent 50%)'
				}"
			/>
			<view class="coupon-tab">本月券包</view>
			<view class="coupon-row">
				<view class="coupon-ticket">
					<text class="ticket-text">{{ coupon.tag }}</text>
				</view>
				<view class="coupon-dash" />
				<view class="coupon-info">
					<text class="c-title">{{ coupon.title }}</text>
					<text class="c-tip">{{ coupon.tip }}</text>
				</view>
				<view class="use-btn" @tap="onCouponAction">
					{{ couponClaimed ? '去使用' : '领取' }}
				</view>
			</view>
		</view>

		<view class="cta-row">
			<view class="cta cta-steward" @tap="openSteward">
				<text class="cta-main">扫码加我！</text>
				<text class="cta-sub">添加您的专属管家！</text>
			</view>
			<view class="cta cta-group" @tap="openGroup">
				<text class="cta-main">扫码入群！</text>
				<text class="cta-sub">优惠活动提前知道！</text>
			</view>
		</view>

		<steward-dialog
			:visible="stewardVisible"
			:title="stewardProps.title"
			:tip="stewardProps.tip"
			:qr-src="stewardProps.qrSrc"
			:phone="stewardProps.phone"
			@close="closeSteward"
		/>
		<steward-dialog
			:visible="groupVisible"
			title="扫码入群"
			tip="优惠活动提前知道"
			qr-src="/static/common/group-qr.png"
			:show-phone="false"
			@close="closeGroup"
		/>
	</view>
</template>

<script>
	import { memberLevels, monthCoupon } from '../../common/member-levels.js'
	import { setVipLevelsFromServer } from '../../common/vip-levels.js'
	import StewardDialog from '../../components/steward-dialog/steward-dialog.vue'
	import { api } from '../../common/api.js'
	import { isLoggedIn, silentLogin, getUser } from '../../common/auth.js'
	import { stewardPropsFromSite } from '../../common/site.js'

	const PROFILE_KEY = 'gather_profile'
	const COUPON_CLAIM_KEY = 'gather_member_month_coupon'

	function currentMonthKey() {
		const now = new Date()
		const m = String(now.getMonth() + 1).padStart(2, '0')
		return `${now.getFullYear()}-${m}`
	}

	export default {
		components: {
			StewardDialog
		},
		data() {
			return {
				rulesLabel: '规则 >',
				levels: memberLevels,
				activeIndex: 0,
				userLevelIndex: 0,
				progress: 0,
				avatar: '',
				statusBarHeight: 20,
				navBarHeight: 44,
				coupon: monthCoupon,
				couponClaimed: false,
				stewardVisible: false,
				groupVisible: false,
				stewardProps: stewardPropsFromSite()
			}
		},
		computed: {
			current() {
				return this.levels[this.activeIndex] || this.levels[0]
			},
			unlocked() {
				return this.activeIndex <= this.userLevelIndex
			},
			progressPercent() {
				const cur = this.current
				if (cur.doneText || !cur.need) return 100
				const p = Math.min(100, Math.round((this.progress / cur.need) * 100))
				return p
			},
			pageStyle() {
				const cur = this.current
				return {
					backgroundColor: cur.pageBg || '#0b1423',
					paddingTop: this.statusBarHeight + this.navBarHeight + 'px'
				}
			}
		},
		onLoad() {
			const sys = uni.getSystemInfoSync()
			this.statusBarHeight = sys.statusBarHeight || 20
			try {
				const menu = uni.getMenuButtonBoundingClientRect()
				if (menu && menu.height && menu.top) {
					this.navBarHeight = (menu.top - this.statusBarHeight) * 2 + menu.height
				}
			} catch (e) {}
			try {
				const raw = uni.getStorageSync(PROFILE_KEY)
				if (raw && raw.avatar) this.avatar = raw.avatar
			} catch (e) {}
			const user = getUser()
			if (user.avatar) this.avatar = user.avatar
			const vip = String(user.vipLevel || 'V0').toUpperCase()
			const idx = this.levels.findIndex((row) => row.id === vip)
			if (idx >= 0) {
				this.userLevelIndex = idx
				this.activeIndex = idx
			}
			this.loadCouponClaim()
			this.loadMember()
		},
		onShow() {
			this.loadCouponClaim()
			this.loadMember()
		},
		methods: {
			async loadMember() {
				try {
					const cfg = await api.memberConfig()
					if (cfg && Array.isArray(cfg.levels) && cfg.levels.length) {
						this.levels = cfg.levels
						setVipLevelsFromServer(cfg.levels)
					}
					if (cfg && cfg.monthCoupon) {
						this.coupon = Object.assign({}, monthCoupon, cfg.monthCoupon)
					}
				} catch (e) {}
				try {
					if (!isLoggedIn()) await silentLogin()
					const profile = await api.profile()
					if (profile) {
						if (typeof profile.tableCount === 'number') this.progress = profile.tableCount
						if (profile.avatar) this.avatar = profile.avatar
						const vip = String(profile.vipLevel || 'V0').toUpperCase()
						const idx = this.levels.findIndex((row) => row.id === vip)
						if (idx >= 0) {
							this.userLevelIndex = idx
							this.activeIndex = idx
						}
					}
				} catch (e) {}
				this.preloadThemeImages()
			},
			goBack() {
				const pages = getCurrentPages()
				if (pages && pages.length > 1) {
					uni.navigateBack()
					return
				}
				uni.switchTab({ url: '/pages/mine/mine' })
			},
			preloadThemeImages() {
				;(this.levels || []).forEach((lv) => {
					if (lv.pageBgImage) uni.getImageInfo({ src: lv.pageBgImage })
					if (lv.cardBgImage) uni.getImageInfo({ src: lv.cardBgImage })
				})
			},
			railStyle(i) {
				// 当前等级始终落在弧线正中（头像下方最低点），其余等级相对偏移沿弧排布
				const offset = i - this.activeIndex
				const step = 0.24
				const t = 0.5 + offset * step
				const tt = Math.min(1, Math.max(0, t))
				// 与 member-rail-arc.png 完全同一条抛物线：y = 21 + 46 * 4t(1-t)
				const left = 1 + tt * 98
				const top = 21 + 46 * 4 * tt * (1 - tt)
				const onArc = t >= 0.02 && t <= 0.98
				return {
					left: left + '%',
					top: top + '%',
					opacity: onArc ? 1 : 0,
					pointerEvents: onArc ? 'auto' : 'none'
				}
			},
			cardProgress(lv) {
				if (!lv) return 0
				if (lv.doneText || !lv.need) return 100
				return Math.min(100, Math.round((this.progress / lv.need) * 100))
			},
			onRailTap(i) {
				this.activeIndex = i
			},
			onLevelSwipe(e) {
				const i = e && e.detail && e.detail.current
				if (typeof i === 'number') this.activeIndex = i
			},
			async loadCouponClaim() {
				try {
					if (!isLoggedIn()) await silentLogin()
					const res = await api.coupons()
					const month = currentMonthKey()
					const unused = res.unused || []
					this.couponClaimed = unused.some((c) => String(c.expire) === month)
					if (!this.couponClaimed) {
						const raw = uni.getStorageSync(COUPON_CLAIM_KEY)
						this.couponClaimed = !!(raw && raw.month === month && raw.claimed)
					}
				} catch (e) {
					try {
						const raw = uni.getStorageSync(COUPON_CLAIM_KEY)
						this.couponClaimed = !!(raw && raw.month === currentMonthKey() && raw.claimed)
					} catch (err) {
						this.couponClaimed = false
					}
				}
			},
			onRules() {
				uni.navigateTo({ url: '/pages/mine/member-rules' })
			},
			async onCouponAction() {
				if (!this.couponClaimed) {
					try {
						if (!isLoggedIn()) await silentLogin()
						const res = await api.claimCoupon({ month: currentMonthKey() })
						if (res && res.ok === false) {
							this.couponClaimed = true
							uni.showToast({ title: res.message || '本月已领取', icon: 'none' })
							return
						}
						this.couponClaimed = true
						uni.setStorageSync(COUPON_CLAIM_KEY, {
							month: currentMonthKey(),
							claimed: true
						})
						uni.showToast({ title: '领取成功', icon: 'success' })
					} catch (e) {
						uni.showToast({ title: (e && e.message) || '领取失败', icon: 'none' })
					}
					return
				}
				uni.navigateTo({ url: '/pages/mine/coupons' })
			},
			openSteward() {
				this.stewardProps = stewardPropsFromSite()
				this.groupVisible = false
				this.stewardVisible = true
			},
			openGroup() {
				this.stewardVisible = false
				this.groupVisible = true
			},
			closeSteward() {
				this.stewardVisible = false
			},
			closeGroup() {
				this.groupVisible = false
			}
		}
	}
</script>

<style>
	.page {
		min-height: 100vh;
		padding: 16rpx 24rpx calc(40rpx + env(safe-area-inset-bottom));
		box-sizing: border-box;
		color: #ffffff;
		position: relative;
		overflow: hidden;
		transition: background-color 0.35s ease;
	}

	.page-bg {
		position: fixed;
		left: 0;
		top: 0;
		width: 100%;
		height: 100%;
		z-index: 0;
		pointer-events: none;
	}

	.page-shade {
		position: fixed;
		left: 0;
		right: 0;
		top: 0;
		bottom: 0;
		z-index: 0;
		pointer-events: none;
		background: linear-gradient(180deg, rgba(0, 0, 0, 0.06) 0%, rgba(0, 0, 0, 0.22) 100%);
	}

	.navbar {
		position: fixed;
		left: 0;
		right: 0;
		top: 0;
		z-index: 20;
		background: transparent;
	}

	.navbar-inner {
		position: relative;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.back {
		position: absolute;
		left: 16rpx;
		top: 0;
		bottom: 0;
		width: 72rpx;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.back-arrow {
		width: 18rpx;
		height: 18rpx;
		border-left: 4rpx solid #ffffff;
		border-bottom: 4rpx solid #ffffff;
		transform: rotate(45deg);
		margin-left: 8rpx;
	}

	.nav-title {
		font-size: 34rpx;
		font-weight: 600;
		color: #ffffff;
		line-height: 1;
	}

	.top {
		display: flex;
		flex-direction: column;
		align-items: center;
		position: relative;
		z-index: 1;
	}

	.avatar-block {
		display: flex;
		flex-direction: column;
		align-items: center;
		margin-bottom: 12rpx;
	}

	.avatar {
		width: 120rpx;
		height: 120rpx;
		border-radius: 50%;
		background: #f0e6dc;
		border: 4rpx solid rgba(255, 255, 255, 0.85);
	}

	.lock-tag {
		margin-top: -16rpx;
		padding: 6rpx 22rpx;
		border-radius: 999rpx;
		font-size: 20rpx;
		background: rgba(90, 70, 45, 0.75);
		color: rgba(255, 255, 255, 0.85);
		z-index: 1;
		border: 1rpx solid rgba(232, 208, 160, 0.45);
	}

	.lock-tag.on {
		background: rgba(180, 140, 80, 0.92);
		color: #ffffff;
		border-color: rgba(255, 230, 180, 0.55);
	}

	.level-rail {
		position: relative;
		width: 100%;
		height: 0;
		padding-bottom: 22.22%;
		margin-bottom: 56rpx;
		box-sizing: border-box;
	}

	.rail-arc-img {
		position: absolute;
		left: 0;
		top: 0;
		width: 100%;
		height: 100%;
		z-index: 0;
		pointer-events: none;
	}

	.rail-item {
		position: absolute;
		transform: translateX(-50%);
		display: flex;
		flex-direction: column;
		align-items: center;
		z-index: 1;
		width: 88rpx;
		padding-top: 0;
		transition: left 0.35s cubic-bezier(0.22, 0.8, 0.28, 1), top 0.35s cubic-bezier(0.22, 0.8, 0.28, 1),
			opacity 0.25s ease;
	}

	.dot-wrap {
		width: 44rpx;
		height: 44rpx;
		margin-top: -22rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		position: relative;
	}

	.dot {
		width: 20rpx;
		height: 20rpx;
		border-radius: 50%;
		background: rgba(226, 232, 238, 0.9);
		position: relative;
		z-index: 1;
	}

	.rail-item.active .dot {
		width: 24rpx;
		height: 24rpx;
		background: #ffffff;
		box-shadow: 0 0 0 8rpx rgba(255, 255, 255, 0.16), 0 0 18rpx rgba(255, 255, 255, 0.55);
	}

	.lv-name {
		margin-top: 12rpx;
		font-size: 30rpx;
		color: rgba(255, 255, 255, 0.82);
		font-style: italic;
		font-weight: 700;
		letter-spacing: 1rpx;
		line-height: 1;
	}

	.rail-item.active .lv-name {
		color: #ffffff;
		font-weight: 800;
		font-size: 38rpx;
	}

	.level-swiper {
		height: 280rpx;
		margin: 0 -8rpx;
		z-index: 1;
		position: relative;
	}

	.level-card {
		margin: 0 8rpx;
		border-radius: 24rpx;
		padding: 36rpx 28rpx 36rpx 32rpx;
		display: flex;
		align-items: center;
		justify-content: space-between;
		height: 260rpx;
		box-sizing: border-box;
		position: relative;
		overflow: hidden;
	}

	.card-bg {
		position: absolute;
		left: 0;
		top: 0;
		width: 100%;
		height: 100%;
		z-index: 0;
		pointer-events: none;
	}

	.card-left {
		flex: 1;
		min-width: 0;
		z-index: 1;
	}

	.lv-big {
		font-size: 76rpx;
		font-weight: 800;
		font-style: italic;
		line-height: 1;
		display: block;
		margin-bottom: 14rpx;
	}

	.need {
		display: block;
		font-size: 24rpx;
		margin-bottom: 24rpx;
	}

	.bar {
		height: 28rpx;
		border-radius: 999rpx;
		background: rgba(255, 255, 255, 0.55);
		overflow: hidden;
		margin-bottom: 14rpx;
	}

	.bar-fill {
		height: 100%;
		border-radius: 999rpx;
		display: flex;
		align-items: center;
		justify-content: flex-end;
		padding-right: 12rpx;
		box-sizing: border-box;
	}

	.bar-pct {
		font-size: 18rpx;
		color: #ffffff;
		font-weight: 700;
		line-height: 1;
	}

	.bar-tip {
		font-size: 22rpx;
	}

	.crown-img {
		width: 168rpx;
		height: 168rpx;
		flex-shrink: 0;
		margin-left: 8rpx;
		margin-right: -8rpx;
		position: relative;
		z-index: 1;
	}

	.sec-head {
		margin-top: 40rpx;
		margin-bottom: 24rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		position: relative;
		padding-right: 100rpx;
		padding-left: 20rpx;
		z-index: 1;
	}

	.sec-lines {
		display: flex;
		flex-direction: column;
		justify-content: center;
		gap: 6rpx;
		margin: 0 14rpx;
	}

	.sec-line {
		width: 28rpx;
		height: 2rpx;
		background: rgba(212, 175, 120, 0.85);
		transition: background 0.3s ease;
	}

	.sec-title {
		font-size: 30rpx;
		color: #ffffff;
		font-weight: 600;
	}

	.rules {
		position: absolute;
		right: 0;
		top: 50%;
		transform: translateY(-50%);
		padding: 8rpx 18rpx;
		border-radius: 999rpx;
		border: 1rpx solid rgba(255, 255, 255, 0.4);
		background: rgba(255, 255, 255, 0.08);
		font-size: 22rpx;
		color: rgba(255, 255, 255, 0.9);
		line-height: 1;
	}

	.benefit-grid {
		display: flex;
		flex-direction: row;
		flex-wrap: wrap;
		justify-content: space-between;
		position: relative;
		z-index: 1;
	}

	.benefit {
		width: calc((100% - 16rpx) / 2);
		height: 128rpx;
		background: linear-gradient(180deg, #1a2438 0%, #0e1524 100%);
		border: 1rpx solid rgba(255, 255, 255, 0.08);
		border-radius: 16rpx;
		padding: 0 18rpx;
		box-sizing: border-box;
		display: flex;
		flex-direction: row;
		align-items: center;
		margin-bottom: 16rpx;
		overflow: hidden;
		flex-grow: 0;
		flex-shrink: 0;
		transition: background 0.3s ease, border-color 0.3s ease;
	}

	.b-icon {
		width: 72rpx;
		height: 72rpx;
		border-radius: 50%;
		background: radial-gradient(circle at 50% 78%, #e8d4b0 0%, #fff5e6 48%, #fffaf2 100%);
		box-shadow: inset 0 -4rpx 8rpx rgba(180, 140, 80, 0.18);
		display: flex;
		align-items: center;
		justify-content: center;
		margin-right: 14rpx;
		flex-shrink: 0;
	}

	.b-icon-img {
		width: 44rpx;
		height: 44rpx;
	}

	.b-text {
		flex: 1;
		min-width: 0;
		height: 64rpx;
		display: flex;
		flex-direction: column;
		justify-content: center;
	}

	.b-title {
		font-size: 26rpx;
		font-weight: 600;
		color: #ffffff;
		margin-bottom: 6rpx;
		line-height: 1.2;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.b-desc {
		font-size: 20rpx;
		color: rgba(255, 255, 255, 0.55);
		line-height: 1.3;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.coupon-box {
		margin-top: 12rpx;
		background: linear-gradient(180deg, #152038 0%, #0f1830 100%);
		border-radius: 20rpx;
		padding: 0 20rpx 28rpx;
		border: 1rpx solid rgba(255, 255, 255, 0.08);
		position: relative;
		overflow: hidden;
		z-index: 1;
		transition: background 0.3s ease, border-color 0.3s ease;
	}

	.coupon-deco {
		position: absolute;
		left: 0;
		right: 0;
		top: 0;
		height: 48rpx;
		pointer-events: none;
		transition: background 0.3s ease;
	}

	.coupon-tab {
		display: inline-flex;
		margin: 0 auto 24rpx;
		padding: 12rpx 36rpx 14rpx;
		background: linear-gradient(180deg, #f4e8d0 0%, #e4d0a8 100%);
		color: #3a2a12;
		font-size: 24rpx;
		font-weight: 700;
		border-radius: 0 0 18rpx 18rpx;
		position: relative;
		left: 50%;
		transform: translateX(-50%);
		z-index: 1;
		box-shadow: 0 6rpx 12rpx rgba(0, 0, 0, 0.2);
	}

	.coupon-tab::before,
	.coupon-tab::after {
		content: '';
		position: absolute;
		top: 0;
		width: 0;
		height: 0;
		border-style: solid;
	}

	.coupon-tab::before {
		left: -10rpx;
		border-width: 0 10rpx 12rpx 0;
		border-color: transparent #c4a878 transparent transparent;
	}

	.coupon-tab::after {
		right: -10rpx;
		border-width: 0 0 12rpx 10rpx;
		border-color: transparent transparent transparent #c4a878;
	}

	.coupon-row {
		display: flex;
		align-items: center;
		position: relative;
		z-index: 1;
	}

	.coupon-ticket {
		width: 118rpx;
		height: 118rpx;
		border-radius: 12rpx;
		background: linear-gradient(145deg, #ff6b7a, #e23636);
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 10rpx;
		box-sizing: border-box;
		flex-shrink: 0;
	}

	.ticket-text {
		font-size: 22rpx;
		color: #ffffff;
		text-align: center;
		line-height: 1.35;
		font-weight: 700;
		white-space: pre-line;
	}

	.coupon-dash {
		width: 0;
		height: 88rpx;
		margin: 0 18rpx;
		border-left: 2rpx dashed rgba(255, 255, 255, 0.28);
		flex-shrink: 0;
	}

	.coupon-info {
		flex: 1;
		min-width: 0;
		margin-right: 12rpx;
	}

	.c-title {
		display: block;
		font-size: 28rpx;
		font-weight: 600;
		color: #ffffff;
		margin-bottom: 8rpx;
	}

	.c-tip {
		font-size: 22rpx;
		color: rgba(255, 255, 255, 0.5);
	}

	.use-btn {
		padding: 14rpx 28rpx;
		border-radius: 999rpx;
		background: linear-gradient(180deg, #f7f0e0 0%, #e8d8b0 100%);
		color: #3a2a12;
		font-size: 24rpx;
		font-weight: 700;
		flex-shrink: 0;
	}

	.cta-row {
		display: flex;
		justify-content: space-between;
		align-items: stretch;
		margin-top: 28rpx;
		gap: 18rpx;
		position: relative;
		z-index: 1;
	}

	.cta {
		flex: 1;
		min-height: 108rpx;
		border-radius: 999rpx;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		text-align: center;
		padding: 16rpx 18rpx;
		box-sizing: border-box;
		box-shadow: 0 10rpx 24rpx rgba(0, 0, 0, 0.35);
	}

	.cta-main {
		font-size: 28rpx;
		font-weight: 700;
		line-height: 1.25;
		color: #ffffff;
	}

	.cta-sub {
		margin-top: 4rpx;
		font-size: 22rpx;
		font-weight: 500;
		line-height: 1.3;
		color: #ffffff;
	}

	.cta-steward {
		background: linear-gradient(90deg, #ff8c57 0%, #f24f56 100%);
	}

	.cta-group {
		background: linear-gradient(90deg, #d98f2f 0%, #8b552c 100%);
	}
</style>
