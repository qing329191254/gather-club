<template>
	<page-meta :page-style="'overflow:' + (stewardVisible ? 'hidden' : 'visible')"></page-meta>
	<app-loading />
	<view v-if="detail" class="page">
		<view
			class="navbar"
			:class="{ solid: navSolid }"
			:style="{ paddingTop: statusBarHeight + 'px' }"
		>
			<view class="navbar-inner">
				<view class="back" @tap="goBack">
					<view class="back-arrow" :class="{ dark: navSolid }" />
					<text :class="{ dark: navSolid }">返回</text>
				</view>
				<text v-if="navSolid" class="nav-title">{{ detail.name }}</text>
			</view>
		</view>

		<view class="hero-wrap" :style="{ height: heroHeight + 'px' }">
			<swiper
				class="hero-swiper"
				circular
				autoplay
				interval="2000"
				duration="500"
				:style="{ height: heroHeight + 'px' }"
				@change="onBannerChange"
			>
				<swiper-item v-for="(img, index) in detail.banners" :key="index">
					<image class="hero" :src="img" mode="aspectFill" />
				</swiper-item>
			</swiper>
			<view class="hero-indicator">
				<view class="hero-thumb" :style="thumbStyle" />
			</view>
		</view>

		<view class="info">
			<view class="price-row">
				<text class="yen">¥</text>
				<text class="price">{{ detail.price }}</text>
				<text class="price-suffix">起</text>
			</view>
			<text class="name">{{ detail.name }}</text>
			<text class="tag">{{ detail.tag }}</text>
		</view>

		<view class="block" @tap="openMap">
			<view class="addr-row">
				<image class="pin" src="/static/icons/pin-v3.png" mode="aspectFit" />
				<text class="addr">{{ detail.address }}</text>
			</view>
			<view class="route">{{ detail.route }}</view>
		</view>

		<view class="block buy-block">
			<text class="buy-count">{{ detail.recentBuy.countText }}</text>
			<view class="buyer-row">
				<image class="avatar" :src="detail.recentBuy.avatar" mode="aspectFill" />
				<text class="buyer-name">{{ detail.recentBuy.name }}</text>
				<text class="buyer-time">{{ detail.recentBuy.timeText }}</text>
				<view class="order-btn" @tap="onBook">去下单</view>
			</view>
		</view>

		<!-- 后台配置的详情长图 -->
		<view class="detail-imgs">
			<image
				v-for="(img, index) in detail.detailImages"
				:key="index"
				class="detail-img"
				:src="img"
				mode="widthFix"
				:show-menu-by-longpress="true"
			/>
		</view>

		<view class="bar">
			<view class="service" @tap.stop="openSteward">
				<image src="/static/icons/service.png" mode="aspectFit" />
				<text>客服</text>
			</view>
			<view class="book" @tap="onBook">
				<view class="book-half">
					<text class="book-yen">¥</text>
					<text class="book-num">{{ detail.price }}</text>
					<text class="book-qi">起</text>
				</view>
				<view class="book-line" />
				<view class="book-half">
					<text class="book-text">去预定</text>
				</view>
			</view>
		</view>

		<steward-dialog :visible="stewardVisible" @close="closeSteward" />
	</view>
</template>

<script>
	import { api } from '../../common/api.js'

	export default {
		data() {
			return {
				statusBarHeight: 20,
				heroHeight: 280,
				navSolid: false,
				bannerIndex: 0,
				stewardVisible: false,
				detail: null,
				nyeId: ''
			}
		},
		computed: {
			thumbStyle() {
				const count = (this.detail && this.detail.banners && this.detail.banners.length) || 1
				const track = 112
				const thumb = 48
				const step = count > 1 ? (track - thumb) / (count - 1) : 0
				return {
					width: thumb + 'rpx',
					transform: 'translateX(' + this.bannerIndex * step + 'rpx)'
				}
			}
		},
		onLoad(query) {
			const sys = uni.getSystemInfoSync()
			this.statusBarHeight = sys.statusBarHeight || 20
			this.heroHeight = Math.round((sys.windowWidth || 375) * (500 / 750))
			this.nyeId = (query && query.id) || ''
			if (!this.nyeId) {
				uni.showToast({ title: '加载失败', icon: 'none' })
				setTimeout(() => {
					uni.navigateBack({ fail() { uni.navigateTo({ url: '/pages/nye/nye' }) } })
				}, 400)
				return
			}
			api
				.nyeDetail(this.nyeId)
				.then((res) => {
					if (!res) {
						uni.showToast({ title: '加载失败', icon: 'none' })
						setTimeout(() => {
							uni.navigateBack({ fail() { uni.navigateTo({ url: '/pages/nye/nye' }) } })
						}, 400)
						return
					}
					this.detail = {
						id: res.id,
						name: res.name,
						cover: res.cover,
						price: res.price,
						originPrice: res.originPrice,
						tag: res.tag,
						address: res.address,
						route: res.route,
						lat: res.lat,
						lng: res.lng,
						banners: res.banners || [],
						detailImages: res.detailImages || [],
						recentBuy: res.recentBuy || {}
					}
				})
				.catch((err) => {
					uni.showToast({ title: (err && err.message) || '加载失败', icon: 'none' })
					setTimeout(() => {
						uni.navigateBack({ fail() { uni.navigateTo({ url: '/pages/nye/nye' }) } })
					}, 400)
				})
		},
		onPageScroll(e) {
			this.navSolid = e.scrollTop > 120
		},
		methods: {
			onBannerChange(e) {
				this.bannerIndex = e.detail.current
			},
			goBack() {
				uni.navigateBack({ fail() { uni.navigateTo({ url: '/pages/nye/nye' }) } })
			},
			openMap() {
				const d = this.detail
				if (!d) return
				uni.openLocation({
					latitude: d.lat,
					longitude: d.lng,
					name: d.name,
					address: d.address,
					fail() {
						uni.showToast({ title: '地图打开失败', icon: 'none' })
					}
				})
			},
			openSteward() {
				this.stewardVisible = true
			},
			closeSteward() {
				this.stewardVisible = false
			},
			onBook() {
				const id = this.detail && this.detail.id
				uni.navigateTo({ url: '/pages/nye/setmeal?id=' + (id || '') })
			}
		}
	}
</script>

<style>
	.page {
		min-height: 100vh;
		background: #f5f5f5;
		padding-bottom: calc(140rpx + env(safe-area-inset-bottom));
	}

	.navbar {
		position: fixed;
		left: 0;
		right: 0;
		top: 0;
		z-index: 50;
		transition: background 0.2s;
	}

	.navbar.solid {
		background: #fff;
		box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.06);
	}

	.navbar-inner {
		height: 88rpx;
		display: flex;
		align-items: center;
		padding: 0 24rpx;
		position: relative;
	}

	.back {
		display: flex;
		align-items: center;
		z-index: 2;
	}

	.back-arrow {
		width: 18rpx;
		height: 18rpx;
		border-left: 4rpx solid #fff;
		border-bottom: 4rpx solid #fff;
		transform: rotate(45deg);
		margin-right: 8rpx;
	}

	.back-arrow.dark {
		border-color: #333;
	}

	.back text {
		font-size: 30rpx;
		color: #fff;
		line-height: 1;
	}

	.back text.dark {
		color: #333;
	}

	.nav-title {
		position: absolute;
		left: 120rpx;
		right: 120rpx;
		text-align: center;
		font-size: 30rpx;
		font-weight: 600;
		color: #222;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.hero-wrap {
		position: relative;
		width: 100%;
		background: #ddd;
		overflow: hidden;
	}

	.hero-swiper,
	.hero {
		width: 100%;
		height: 100%;
		display: block;
	}

	.hero-indicator {
		position: absolute;
		right: 28rpx;
		bottom: 24rpx;
		width: 112rpx;
		height: 8rpx;
		border-radius: 8rpx;
		background: rgba(255, 255, 255, 0.35);
		overflow: hidden;
	}

	.hero-thumb {
		height: 100%;
		border-radius: 8rpx;
		background: #fff;
	}

	.info {
		background: #fff;
		padding: 36rpx 32rpx 40rpx;
		display: flex;
		flex-direction: column;
		align-items: flex-start;
	}

	.price-row {
		display: flex;
		align-items: baseline;
	}

	.yen {
		font-size: 36rpx;
		font-weight: 700;
		color: #e23636;
	}

	.price {
		font-size: 56rpx;
		font-weight: 700;
		color: #e23636;
		line-height: 1;
		margin-left: 4rpx;
	}

	.price-suffix {
		margin-left: 10rpx;
		font-size: 28rpx;
		font-weight: 600;
		color: #e23636;
	}

	.name {
		display: block;
		margin-top: 20rpx;
		font-size: 38rpx;
		font-weight: 700;
		color: #1a1a1a;
		line-height: 1.45;
	}

	.tag {
		margin-top: 20rpx;
		padding: 8rpx 18rpx;
		border-radius: 8rpx;
		background: #f2f2f2;
		font-size: 24rpx;
		color: #666;
		line-height: 1.2;
	}

	.block {
		margin-top: 16rpx;
		background: #fff;
		padding: 32rpx;
	}

	.addr-row {
		display: flex;
		align-items: center;
	}

	.pin {
		width: 36rpx;
		height: 36rpx;
		margin-right: 12rpx;
		flex-shrink: 0;
	}

	.addr {
		flex: 1;
		font-size: 30rpx;
		color: #333;
		line-height: 1.45;
	}

	.route {
		margin-top: 20rpx;
		padding: 24rpx 24rpx;
		border-radius: 16rpx;
		background: #fff6ee;
		font-size: 26rpx;
		color: #666;
		line-height: 1.65;
	}

	.buy-count {
		display: block;
		font-size: 28rpx;
		color: #999;
		margin-bottom: 24rpx;
	}

	.buyer-row {
		display: flex;
		align-items: center;
	}

	.avatar {
		width: 64rpx;
		height: 64rpx;
		border-radius: 50%;
		background: #eee;
		flex-shrink: 0;
	}

	.buyer-name {
		margin-left: 16rpx;
		font-size: 28rpx;
		color: #333;
		flex-shrink: 0;
	}

	.buyer-time {
		flex: 1;
		margin-left: 16rpx;
		font-size: 26rpx;
		color: #999;
	}

	.order-btn {
		padding: 0 28rpx;
		height: 56rpx;
		line-height: 56rpx;
		border-radius: 28rpx;
		background: #f6d7b8;
		color: #8a5a2b;
		font-size: 26rpx;
		flex-shrink: 0;
	}

	.detail-imgs {
		margin-top: 16rpx;
		background: #fff;
	}

	.detail-img {
		width: 100%;
		display: block;
	}

	.bar {
		position: fixed;
		left: 0;
		right: 0;
		bottom: 0;
		z-index: 40;
		display: flex;
		align-items: center;
		padding: 16rpx 28rpx calc(16rpx + env(safe-area-inset-bottom));
		background: #fff;
		border-radius: 16rpx 16rpx 0 0;
		box-shadow: 0 -2rpx 12rpx rgba(0, 0, 0, 0.05);
	}

	.service {
		width: 80rpx;
		flex-shrink: 0;
		display: flex;
		flex-direction: column;
		align-items: center;
		margin-right: 28rpx;
	}

	.service image {
		width: 48rpx;
		height: 48rpx;
	}

	.service text {
		margin-top: 4rpx;
		font-size: 24rpx;
		color: #222;
		line-height: 1.2;
	}

	.book {
		flex: 1;
		max-width: 520rpx;
		margin-left: auto;
		height: 96rpx;
		border-radius: 48rpx;
		background: #e54148;
		display: flex;
		align-items: center;
	}

	.book-half {
		flex: 1;
		display: flex;
		align-items: baseline;
		justify-content: center;
		color: #fff;
	}

	.book-yen {
		font-size: 30rpx;
		font-weight: 700;
		line-height: 1;
	}

	.book-num {
		font-size: 44rpx;
		font-weight: 700;
		line-height: 1;
		margin-left: 2rpx;
	}

	.book-qi {
		font-size: 24rpx;
		font-weight: 500;
		line-height: 1;
		margin-left: 6rpx;
	}

	.book-text {
		font-size: 34rpx;
		font-weight: 700;
		line-height: 1;
		color: #fff;
	}

	.book-line {
		width: 2rpx;
		height: 34rpx;
		background: rgba(255, 255, 255, 0.85);
		flex-shrink: 0;
	}
</style>
