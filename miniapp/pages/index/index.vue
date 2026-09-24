<template>
	<page-meta :page-style="'overflow:' + (stewardVisible || privacyVisible || phoneLoginVisible || profilePromptVisible ? 'hidden' : 'visible')"></page-meta>
	<app-loading />
	<view class="page">
		<view
			class="navbar"
			:class="{ solid: navSolid }"
			:style="{ paddingTop: statusBarHeight + 'px' }"
		>
			<view class="navbar-inner" />
		</view>

		<view class="hero-wrap" :style="{ height: heroHeight + 'px' }">
			<swiper
				class="hero"
				circular
				autoplay
				interval="4500"
				:style="{ height: heroHeight + 'px' }"
				@change="onSwiperChange"
			>
				<swiper-item v-for="item in banners" :key="item.id">
					<image class="hero-img" :src="item.image" mode="aspectFill" @tap="onBanner(item)" />
				</swiper-item>
			</swiper>
			<view class="hero-indicator">
				<view
					class="hero-thumb"
					:style="{ width: 100 / (banners.length || 1) + '%', transform: 'translateX(' + current * 100 + '%)' }"
				/>
			</view>
		</view>

		<view class="entry">
			<view
				v-if="entryFeature"
				class="entry-feature"
				@tap="onAction(entryFeature)"
			>
				<image class="entry-feature-icon" :src="entryFeature.icon" mode="aspectFit" />
				<view class="entry-feature-copy">
					<text class="entry-feature-name">{{ entryFeature.name }}</text>
					<text class="entry-feature-desc">{{ entryFeature.desc }}</text>
				</view>
				<view class="entry-feature-go">去咨询</view>
			</view>
			<view class="entry-grid">
				<view
					v-for="item in entryTiles"
					:key="item.key"
					class="entry-tile"
					@tap="onAction(item)"
				>
					<image class="entry-tile-icon" :src="item.icon" mode="aspectFit" />
					<text class="entry-tile-name">{{ item.name }}</text>
					<text v-if="item.desc" class="entry-tile-desc">{{ item.desc }}</text>
				</view>
			</view>
		</view>

		<view class="section">
			<text class="section-title">门店预约</text>
			<view v-for="store in stores" :key="store.id" class="store">
				<view class="store-head" @tap="callStore(store)">
					<view class="store-name-wrap">
						<view class="store-bar" />
						<text class="store-name">{{ store.name }}</text>
					</view>
					<view class="store-phone">
						<image src="/static/icons/phone-v2.png" mode="aspectFit" />
					</view>
				</view>
				<view class="store-card">
					<view class="store-cover-wrap" @tap="bookStore(store)">
						<image class="store-cover" :src="store.cover" mode="aspectFill" />
						<view class="book-btn">预约</view>
					</view>
					<view class="store-nav" @tap="openMap(store)">
						<view class="store-addr">
							<image class="pin" src="/static/icons/pin-v3.png" mode="aspectFit" />
							<text class="addr-text">{{ store.address }}</text>
						</view>
						<view class="store-route">
							<text>推荐路线：{{ store.route }}</text>
						</view>
					</view>
				</view>
			</view>
		</view>
		<app-tabbar :current="0" />
		<steward-dialog
			:visible="stewardVisible"
			:title="stewardProps.title"
			:tip="stewardProps.tip"
			:qr-src="stewardProps.qrSrc"
			:phone="stewardProps.phone"
			@close="closeSteward"
		/>
		<privacy-dialog
			:visible="privacyVisible"
			@agree="onPrivacyAgree"
			@disagree="onPrivacyDisagree"
		/>
		<phone-login-dialog
			ref="phoneLogin"
			:visible="phoneLoginVisible"
			@cancel="onPhoneLoginCancel"
			@confirm="onPhoneLoginConfirm"
		/>
		<profile-reward-dialog
			:visible="profilePromptVisible"
			mode="prompt"
			:points="profileRewardPoints"
			@go="onProfileGo"
			@later="onProfileLater"
			@close="onProfileLater"
		/>
	</view>
</template>

<script>
	import {
		needPrivacyPrompt,
		setPrivacyStatus,
		silentLogin,
		isLoggedIn,
		refreshProfile,
		bindPhoneFromDetail
	} from '../../common/auth.js'
	import PhoneLoginDialog from '../../components/phone-login-dialog/phone-login-dialog.vue'
	import { api } from '../../common/api.js'
	import { stewardPropsFromSite } from '../../common/site.js'
	import { isProfileComplete } from '../../common/profile.js'
	import ProfileRewardDialog from '../../components/profile-reward-dialog/profile-reward-dialog.vue'

	export default {
		components: {
			ProfileRewardDialog,
			PhoneLoginDialog
		},
		data() {
			return {
				statusBarHeight: 20,
				heroHeight: 280,
				current: 0,
				navSolid: false,
				stewardVisible: false,
				privacyVisible: false,
				phoneLoginVisible: false,
				profilePromptVisible: false,
				profileRewardPoints: 0,
				stewardProps: stewardPropsFromSite(),
				banners: [],
				primaryActions: [],
				secondaryActions: [],
				stores: []
			}
		},
		computed: {
			entryFeature() {
				return (this.primaryActions && this.primaryActions[0]) || null
			},
			entryTiles() {
				const rest = (this.primaryActions || []).slice(1)
				return rest.concat(this.secondaryActions || [])
			}
		},
		onLoad() {
			const sys = uni.getSystemInfoSync()
			this.statusBarHeight = sys.statusBarHeight || 20
			this.heroHeight = Math.round((sys.windowWidth || 375) * 0.77)
			this.loadHome()
		},
		onShow() {
			uni.hideTabBar({ fail() {} })
			this.checkPrivacy()
			this.afterPrivacy()
		},
		onPageScroll(e) {
			this.navSolid = e.scrollTop > 40
		},
		methods: {
			checkPrivacy() {
				this.privacyVisible = needPrivacyPrompt()
			},
			async maybeProfilePrompt() {
				if (this.privacyVisible || this.phoneLoginVisible || this.profilePromptVisible) return
				const app = getApp()
				if (app && app.globalData && app.globalData.profilePromptSnooze) return
				try {
					const cfg = await api.profileReward()
					const points = Number((cfg && cfg.points) || 0)
					if (!cfg || !cfg.enabled || points <= 0) return
					if (!isLoggedIn()) await silentLogin()
					const profile = await api.profile({ loading: false })
					if (!profile || profile.profileRewarded || isProfileComplete(profile)) return
					this.profileRewardPoints = points
					this.profilePromptVisible = true
				} catch (e) {}
			},
			onProfileGo() {
				this.profilePromptVisible = false
				this.snoozeProfilePrompt()
				uni.navigateTo({ url: '/pages/mine/profile' })
			},
			onProfileLater() {
				this.profilePromptVisible = false
				this.snoozeProfilePrompt()
			},
			snoozeProfilePrompt() {
				const app = getApp()
				if (app) {
					app.globalData = app.globalData || {}
					app.globalData.profilePromptSnooze = true
				}
			},
			async afterPrivacy() {
				if (this.privacyVisible || this.phoneLoginVisible || this.profilePromptVisible) return
				if (needPrivacyPrompt()) return
				const app = getApp()
				const snooze = app && app.globalData && app.globalData.phonePromptSnooze
				try {
					if (!isLoggedIn()) await silentLogin({ quiet: true })
					if (isLoggedIn()) {
						const user = await refreshProfile()
						if (user && !user.phone && !snooze) {
							this.phoneLoginVisible = true
							return
						}
					}
				} catch (e) {}
				this.maybeProfilePrompt()
			},
			onPhoneLoginCancel() {
				this.phoneLoginVisible = false
				const app = getApp()
				if (app) {
					app.globalData = app.globalData || {}
					app.globalData.phonePromptSnooze = true
				}
				this.maybeProfilePrompt()
			},
			onPhoneLoginConfirm(detail) {
				bindPhoneFromDetail(detail)
					.then(() => {
						this.phoneLoginVisible = false
						const app = getApp()
						if (app.globalData) app.globalData.authVersion = Date.now()
						this.maybeProfilePrompt()
					})
					.catch((e) => {
						uni.showToast({ title: (e && e.message) || '获取手机号失败', icon: 'none' })
					})
					.finally(() => {
						const dlg = this.$refs.phoneLogin
						if (dlg && dlg.resetBusy) dlg.resetBusy()
					})
			},
			onPrivacyAgree() {
				setPrivacyStatus('agreed')
				this.privacyVisible = false
				silentLogin()
					.then(() => {
						const app = getApp()
						if (app.globalData) app.globalData.authVersion = Date.now()
						return this.afterPrivacy()
					})
					.catch((e) => {
						// 登录失败仍保留已同意状态，可继续浏览；下次可再试登录
						this.privacyVisible = false
						uni.showToast({ title: (e && e.message) || '登录失败', icon: 'none' })
					})
			},
			onPrivacyDisagree() {
				setPrivacyStatus('declined')
				uni.showModal({
					title: '无法继续使用',
					content: '需同意《用户隐私保护协议》后才能使用天天俱乐部。若不同意，将退出小程序。',
					confirmText: '重新考虑',
					cancelText: '退出',
					success: (res) => {
						if (res.confirm) {
							// 清空 declined，继续强制弹窗，形成闭环
							setPrivacyStatus('')
							this.privacyVisible = true
							return
						}
						this.privacyVisible = true
						// #ifdef MP-WEIXIN
						if (typeof wx !== 'undefined' && wx.exitMiniProgram) {
							wx.exitMiniProgram({ fail: () => {} })
						} else {
							uni.exitMiniProgram({ fail: () => {} })
						}
						// #endif
						// #ifndef MP-WEIXIN
						uni.showToast({ title: '请同意协议后使用', icon: 'none' })
						setPrivacyStatus('')
						// #endif
					}
				})
			},
			loadHome() {
				this.primaryActions = [
					{ key: 'steward', name: '联系管家', desc: '企微一对一，帮你订场次', icon: '/static/icons/action-steward.png' },
					{ key: 'mall', name: '积分商城', desc: '积分兑好礼', icon: '/static/icons/action-mall.png' }
				]
				this.secondaryActions = [
					{ key: 'order', name: '我的订单', desc: '查看进度', icon: '/static/icons/action-order.png' },
					{ key: 'checkin', name: '每日签到', desc: '领积分', icon: '/static/icons/action-checkin.png' }
				]
				api
					.home()
					.then((res) => {
						this.banners = (res.banners || []).map((b) => ({
							id: b.id,
							image: b.image,
							link: b.link
						}))
						this.stores = res.stores || []
						const app = getApp()
						if (app.globalData) app.globalData.site = res.site || null
						this.stewardProps = stewardPropsFromSite(res.site)
					})
					.catch(() => {
						this.banners = []
						this.stores = []
						uni.showToast({ title: '首页数据加载失败', icon: 'none' })
					})
			},
			onSwiperChange(e) {
				this.current = e.detail.current
			},
			onBanner(item) {
				if (item && item.link) {
					uni.navigateTo({ url: item.link })
					return
				}
				uni.showToast({ title: '详情即将开放', icon: 'none' })
			},
			onAction(item) {
				if (item.key === 'steward') {
					this.stewardProps = stewardPropsFromSite()
					this.stewardVisible = true
					return
				}
				if (item.key === 'checkin') {
					uni.navigateTo({ url: '/pages/checkin/checkin' })
					return
				}
				if (item.key === 'order') {
					uni.navigateTo({ url: '/pages/orders/orders' })
					return
				}
				if (item.key === 'mall') {
					uni.navigateTo({ url: '/pages/mall/mall' })
					return
				}
				uni.showToast({ title: item.name + '即将开放', icon: 'none' })
			},
			closeSteward() {
				this.stewardVisible = false
			},
			bookStore() {
				const app = getApp()
				app.globalData = app.globalData || {}
				app.globalData.gatherTab = '__first__'
				uni.switchTab({ url: '/pages/gather/gather' })
			},
			callStore(store) {
				if (!store.phone) {
					uni.showToast({ title: '门店电话即将配置', icon: 'none' })
					return
				}
				uni.makePhoneCall({ phoneNumber: store.phone })
			},
			openMap(store) {
				if (!store.lat || !store.lng) {
					uni.showToast({ title: '暂无门店坐标', icon: 'none' })
					return
				}
				uni.openLocation({
					latitude: Number(store.lat),
					longitude: Number(store.lng),
					name: store.name,
					address: store.address,
					scale: 16
				})
			}
		}
	}
</script>

<style>
	.page {
		min-height: 100vh;
		background: #F1EEE8;
		padding-bottom: calc(148rpx + env(safe-area-inset-bottom));
	}

	.navbar {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		z-index: 100;
		background: transparent;
	}

	.navbar.solid {
		background: #F1EEE8;
	}

	.navbar-inner {
		height: 44px;
	}

	.hero-wrap {
		position: relative;
		width: 100%;
	}

	.hero {
		width: 100%;
		overflow: hidden;
		border-radius: 0;
		background: #DDD4C8;
	}

	.hero-img {
		width: 100%;
		height: 100%;
		display: block;
	}

	.hero-indicator {
		position: absolute;
		right: 40rpx;
		bottom: 20rpx;
		width: 72rpx;
		height: 8rpx;
		border-radius: 8rpx;
		background: rgba(255, 255, 255, 0.45);
		overflow: hidden;
		z-index: 2;
	}

	.hero-thumb {
		height: 100%;
		border-radius: 8rpx;
		background: #fff;
		transition: transform 0.3s;
	}

	.entry {
		margin: 24rpx 24rpx 0;
	}

	.entry-feature {
		display: flex;
		align-items: center;
		padding: 28rpx 24rpx;
		background: #fff;
		border-radius: 12rpx;
		border: 1rpx solid #E8E2DA;
		border-left: 8rpx solid #C6453C;
		box-sizing: border-box;
	}

	.entry-feature-icon {
		width: 88rpx;
		height: 88rpx;
		flex-shrink: 0;
		background: #F7F3EE;
		border-radius: 16rpx;
		padding: 12rpx;
		box-sizing: border-box;
	}

	.entry-feature-copy {
		flex: 1;
		min-width: 0;
		margin: 0 20rpx;
		display: flex;
		flex-direction: column;
	}

	.entry-feature-name {
		font-size: 32rpx;
		font-weight: 700;
		color: #2C2A27;
		line-height: 1.3;
	}

	.entry-feature-desc {
		margin-top: 8rpx;
		font-size: 24rpx;
		color: #8A847C;
		line-height: 1.35;
	}

	.entry-feature-go {
		flex-shrink: 0;
		padding: 0 22rpx;
		height: 56rpx;
		line-height: 56rpx;
		font-size: 24rpx;
		color: #fff;
		background: #C6453C;
		border-radius: 8rpx;
		font-weight: 600;
	}

	.entry-grid {
		margin-top: 16rpx;
		display: flex;
		gap: 12rpx;
	}

	.entry-tile {
		flex: 1;
		min-width: 0;
		background: #fff;
		border: 1rpx solid #E8E2DA;
		border-radius: 12rpx;
		padding: 24rpx 12rpx 22rpx;
		display: flex;
		flex-direction: column;
		align-items: center;
		box-sizing: border-box;
	}

	.entry-tile-icon {
		width: 64rpx;
		height: 64rpx;
	}

	.entry-tile-name {
		margin-top: 14rpx;
		font-size: 26rpx;
		font-weight: 600;
		color: #2C2A27;
		line-height: 1.2;
		text-align: center;
	}

	.entry-tile-desc {
		margin-top: 6rpx;
		font-size: 20rpx;
		color: #9A9288;
		line-height: 1.2;
		text-align: center;
	}

	.section {
		padding: 40rpx 24rpx 0;
	}

	.section-title {
		font-size: 34rpx;
		font-weight: 700;
		color: #2C2A27;
		line-height: 1.2;
	}

	.store {
		margin-top: 28rpx;
	}

	.store-head {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 8rpx 0 20rpx;
	}

	.store-name-wrap {
		display: flex;
		align-items: center;
		min-width: 0;
	}

	.store-bar {
		width: 6rpx;
		height: 28rpx;
		border-radius: 0;
		background: #C6453C;
		margin-right: 16rpx;
		flex-shrink: 0;
	}

	.store-name {
		font-size: 36rpx;
		color: #2C2A27;
		font-weight: 600;
		line-height: 1.2;
	}

	.store-phone {
		width: 48rpx;
		height: 48rpx;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.store-phone image {
		width: 44rpx;
		height: 44rpx;
	}

	.store-card {
		background: #fff;
		border-radius: 12rpx;
		overflow: hidden;
		padding-bottom: 24rpx;
		border: 1rpx solid #E8E2DA;
	}

	.store-cover-wrap {
		position: relative;
		height: 360rpx;
	}

	.store-cover {
		width: 100%;
		height: 100%;
		display: block;
	}

	.book-btn {
		position: absolute;
		right: 20rpx;
		top: 20rpx;
		background: #C6453C;
		color: #fff;
		font-size: 28rpx;
		line-height: 64rpx;
		padding: 0 32rpx;
		border-radius: 8rpx;
	}

	.store-nav {
		padding-bottom: 8rpx;
	}

	.store-addr {
		display: flex;
		align-items: flex-start;
		padding: 24rpx 24rpx 0;
	}

	.pin {
		width: 40rpx;
		height: 40rpx;
		margin-right: 14rpx;
		margin-top: 4rpx;
		flex-shrink: 0;
	}

	.addr-text {
		flex: 1;
		font-size: 32rpx;
		color: #303030;
		line-height: 1.35;
	}

	.store-route {
		margin: 16rpx 8rpx 0;
		background: #F3EEE8;
		border-radius: 8rpx;
		padding: 16rpx 14rpx;
	}

	.store-route text {
		font-size: 28rpx;
		color: #383838;
		line-height: 1.25;
	}
</style>
