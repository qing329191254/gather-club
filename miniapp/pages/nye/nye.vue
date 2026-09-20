<template>
	<app-loading />
	<view class="page">
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
				<text v-if="navSolid" class="nav-title">年夜饭</text>
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
			>
				<swiper-item v-for="(img, index) in banners" :key="index">
					<image class="hero" :src="img" mode="aspectFill" />
				</swiper-item>
			</swiper>
		</view>

		<view class="sheet">
			<view
				v-for="item in list"
				:key="item.id"
				class="card"
				@tap="onItem(item)"
			>
				<image class="thumb" :src="item.cover" mode="aspectFill" />
				<view class="body">
					<view class="top">
						<text class="name">{{ item.name }}</text>
						<view class="tag">年夜饭</view>
					</view>
					<view class="action">
						<view class="price-area">
							<text class="yen">¥</text>
							<text class="num">{{ item.price }}</text>
							<text v-if="item.originPrice" class="origin">¥{{ item.originPrice }}</text>
						</view>
						<view class="buy" @tap.stop="onItem(item)">
							<text class="buy-text">去购买</text>
						</view>
					</view>
				</view>
			</view>

			<view class="end-line">
				<view class="end-rule" />
				<text class="end-text">没有更多了</text>
				<view class="end-rule" />
			</view>
		</view>
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
				banners: [],
				list: []
			}
		},
		onLoad() {
			const sys = uni.getSystemInfoSync()
			this.statusBarHeight = sys.statusBarHeight || 20
			const width = sys.windowWidth || 375
			this.heroHeight = Math.round(width * (500 / 750))
			api
				.nyeList()
				.then((res) => {
					if (Array.isArray(res.list)) this.list = res.list
					if (Array.isArray(res.banners) && res.banners.length) {
						this.banners = res.banners
					} else if (this.list.length) {
						this.banners = this.list
							.slice(0, 3)
							.map((item) => item.cover)
							.filter(Boolean)
					}
				})
				.catch(() => {
					uni.showToast({ title: '加载失败', icon: 'none' })
				})
		},
		onPageScroll(e) {
			this.navSolid = e.scrollTop > 160
		},
		methods: {
			goBack() {
				uni.navigateBack({ fail() { uni.switchTab({ url: '/pages/index/index' }) } })
			},
			onItem(item) {
				uni.navigateTo({ url: '/pages/nye/detail?id=' + item.id })
			}
		}
	}
</script>

<style>
	.page {
		min-height: 100vh;
		background: #f5f5f5;
		padding-bottom: calc(24rpx + env(safe-area-inset-bottom));
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
		background: #ffffff;
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
		left: 0;
		right: 0;
		text-align: center;
		font-size: 34rpx;
		font-weight: 600;
		color: #222;
	}

	.hero-wrap {
		width: 100%;
		overflow: hidden;
		background: #c62828;
	}

	.hero-swiper {
		width: 100%;
	}

	.hero {
		width: 100%;
		height: 100%;
		display: block;
	}

	.sheet {
		margin-top: -36rpx;
		position: relative;
		z-index: 2;
		background: #f5f5f5;
		border-radius: 28rpx 28rpx 0 0;
		padding: 24rpx 20rpx 8rpx;
	}

	.card {
		display: flex;
		align-items: flex-start;
		background: #fff;
		border-radius: 16rpx;
		border: 1rpx solid #eee;
		padding: 24rpx;
		margin-bottom: 20rpx;
		box-sizing: border-box;
	}

	.thumb {
		width: 200rpx;
		height: 200rpx;
		border-radius: 12rpx;
		flex-shrink: 0;
		background: #eee;
	}

	.body {
		flex: 1;
		min-width: 0;
		margin-left: 20rpx;
		height: 200rpx;
		display: flex;
		flex-direction: column;
		justify-content: space-between;
		box-sizing: border-box;
	}

	.top {
		display: flex;
		flex-direction: column;
		align-items: flex-start;
	}

	.name {
		font-size: 30rpx;
		font-weight: 500;
		color: #222;
		line-height: 1.35;
		display: -webkit-box;
		-webkit-box-orient: vertical;
		-webkit-line-clamp: 2;
		overflow: hidden;
	}

	.tag {
		margin-top: 12rpx;
		padding: 0 12rpx;
		height: 36rpx;
		line-height: 36rpx;
		border-radius: 6rpx;
		background: #f0f0f0;
		font-size: 22rpx;
		color: #888;
	}

	.action {
		align-self: stretch;
		height: 68rpx;
		display: flex;
		align-items: stretch;
	}

	.price-area {
		flex: 1;
		min-width: 0;
		display: flex;
		align-items: baseline;
		padding: 0 16rpx 0 20rpx;
		background: #fef4ef;
		border-radius: 34rpx 0 0 34rpx;
		box-sizing: border-box;
	}

	.yen {
		font-size: 28rpx;
		font-weight: 700;
		color: #e03d47;
		line-height: 68rpx;
	}

	.num {
		font-size: 36rpx;
		font-weight: 700;
		color: #e03d47;
		line-height: 68rpx;
	}

	.origin {
		margin-left: 10rpx;
		font-size: 22rpx;
		color: #bbb;
		text-decoration: line-through;
		line-height: 68rpx;
	}

	.buy {
		padding: 0 28rpx;
		background: #fc4f39;
		border-radius: 8rpx;
		display: flex;
		align-items: center;
		flex-shrink: 0;
		transform: skewX(-12deg);
		margin-left: 4rpx;
	}

	.buy-text {
		color: #fff;
		font-size: 28rpx;
		font-weight: 600;
		line-height: 1;
		white-space: nowrap;
		transform: skewX(12deg);
	}

	.end-line {
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 36rpx 0 20rpx;
	}

	.end-rule {
		width: 80rpx;
		height: 1rpx;
		background: #ddd;
	}

	.end-text {
		margin: 0 20rpx;
		font-size: 24rpx;
		color: #bbb;
	}
</style>
