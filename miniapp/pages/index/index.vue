<template>
	<page-meta :page-style="'overflow:' + (stewardVisible ? 'hidden' : 'visible')"></page-meta>
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

		<view class="actions">
			<view class="action-main">
				<view
					v-for="(item, index) in primaryActions"
					:key="item.key"
					class="action-big"
					@tap="onAction(item)"
				>
					<image class="action-icon" :src="item.icon" mode="aspectFit" />
					<text class="action-name">{{ item.name }}</text>
					<text class="action-desc">{{ item.desc }}</text>
					<view v-if="index === 0" class="action-line" />
				</view>
			</view>
			<view class="action-sub">
				<view
					v-for="item in secondaryActions"
					:key="item.key"
					class="action-small"
					@tap="onAction(item)"
				>
					<image class="sub-icon" :src="item.icon" mode="aspectFit" />
					<text>{{ item.name }}</text>
				</view>
			</view>
		</view>

		<view class="section">
			<text class="section-title">门店预定</text>
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
	</view>
</template>

<script>
	import {
		needPrivacyPrompt,
		setPrivacyStatus,
		silentLogin
	} from '../../common/auth.js'
	import { api } from '../../common/api.js'
	import { stewardPropsFromSite } from '../../common/site.js'

	export default {
		data() {
			return {
				statusBarHeight: 20,
				heroHeight: 280,
				current: 0,
				navSolid: false,
				stewardVisible: false,
				privacyVisible: false,
				stewardProps: stewardPropsFromSite(),
				banners: [],
				primaryActions: [],
				secondaryActions: [],
				stores: []
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
		},
		onPageScroll(e) {
			this.navSolid = e.scrollTop > 40
		},
		methods: {
			checkPrivacy() {
				if (needPrivacyPrompt()) {
					this.privacyVisible = true
				}
			},
			onPrivacyAgree() {
				silentLogin().then(() => {
					this.privacyVisible = false
					const app = getApp()
					if (app.globalData) app.globalData.authVersion = Date.now()
					uni.showToast({ title: '登录成功', icon: 'success' })
				})
			},
			onPrivacyDisagree() {
				setPrivacyStatus('declined')
				this.privacyVisible = false
			},
			loadHome() {
				this.primaryActions = [
					{ key: 'steward', name: '联系管家', desc: '活动详情', icon: '/static/icons/chat.png' },
					{ key: 'mall', name: '积分商城', desc: '快乐一整天', icon: '/static/icons/shop.png' }
				]
				this.secondaryActions = [
					{ key: 'order', name: '我的订单', icon: '/static/icons/order.png' },
					{ key: 'checkin', name: '每日签到', icon: '/static/icons/checkin.png' }
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
						this.banners = [
							{ id: 1, image: '/static/banners/hotel.png', link: '/pages/recommend/recommend' },
							{ id: 2, image: '/static/banners/nye.png', link: '/pages/nye/nye' }
						]
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
			bookStore(store) {
				const id = (store && store.id) || ''
				uni.navigateTo({
					url: '/pages/booking/booking' + (id ? '?storeId=' + id : '')
				})
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
		background: #F4F0E7;
		padding-bottom: calc(168rpx + env(safe-area-inset-bottom));
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
		background: #F4F0E7;
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
		border-radius: 0 0 24rpx 24rpx;
		background: #E9D7C4;
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

	.actions {
		margin: 20rpx 32rpx 0;
		background: #fff;
		border-radius: 24rpx;
		overflow: hidden;
	}

	.action-main {
		display: flex;
		padding: 48rpx 0 40rpx;
	}

	.action-big {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		position: relative;
	}

	.action-icon {
		width: 132rpx;
		height: 132rpx;
	}

	.action-name {
		margin-top: 20rpx;
		font-size: 32rpx;
		font-weight: 600;
		color: #1a1a1a;
		line-height: 1.2;
	}

	.action-desc {
		margin-top: 8rpx;
		font-size: 26rpx;
		color: #999;
		line-height: 1.2;
	}

	.action-line {
		position: absolute;
		right: 0;
		top: 12rpx;
		bottom: 4rpx;
		width: 1rpx;
		background: #E8E4DF;
	}

	.action-sub {
		display: flex;
		border-top: 1rpx solid #F0ECE8;
		padding: 32rpx 0;
	}

	.action-small {
		flex: 1;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 30rpx;
		font-weight: 400;
		color: #222;
		line-height: 1.2;
	}

	.sub-icon {
		width: 44rpx;
		height: 44rpx;
		margin-right: 14rpx;
	}

	.section {
		padding: 40rpx 32rpx 0;
	}

	.section-title {
		font-size: 40rpx;
		font-weight: 700;
		color: #1a1a1a;
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
		width: 4rpx;
		height: 32rpx;
		border-radius: 2rpx;
		background: #A87858;
		margin-right: 16rpx;
		flex-shrink: 0;
	}

	.store-name {
		font-size: 40rpx;
		color: #A87858;
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
		border-radius: 20rpx;
		overflow: hidden;
		padding-bottom: 24rpx;
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
		background: #E03D47;
		color: #fff;
		font-size: 36rpx;
		line-height: 76rpx;
		padding: 0 46rpx;
		border-radius: 38rpx;
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
		background: #FFF1E2;
		border-radius: 16rpx;
		padding: 16rpx 14rpx;
	}

	.store-route text {
		font-size: 28rpx;
		color: #383838;
		line-height: 1.25;
	}
</style>
