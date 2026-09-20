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
				<text v-if="navSolid" class="nav-title">订酒店</text>
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
				@tap="onBuy(item)"
			>
				<image class="thumb" :src="item.cover" mode="aspectFill" />
				<view class="body">
					<text class="name">{{ item.name }}</text>
					<view class="action">
						<view class="price-area">
							<text class="yen">¥</text>
							<text class="num">{{ item.price }}</text>
							<text class="suffix">/人起</text>
						</view>
						<view class="buy" :class="{ 'tap-busy': isTapBusy('buy-' + item.id) }" @tap.stop="onBuy(item)">
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
	import { isLoggedIn, silentLogin } from '../../common/auth.js'
	import { settlePay } from '../../common/pay.js'

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
			// 测试头图 750x500
			this.heroHeight = Math.round(width * (500 / 750))
			this.loadList()
		},
		onPageScroll(e) {
			this.navSolid = e.scrollTop > 160
		},
		methods: {
			loadList() {
				api.recommend()
					.then((res) => {
						this.banners = Array.isArray(res && res.banners) ? res.banners : []
						this.list = Array.isArray(res && res.list) ? res.list : []
					})
					.catch(() => {
						this.banners = []
						this.list = []
						uni.showToast({ title: '加载失败', icon: 'none' })
					})
			},
			goBack() {
				uni.navigateBack({ fail() { uni.switchTab({ url: '/pages/index/index' }) } })
			},
			async onBuy(item) {
				if (!item) return
				const key = 'buy-' + item.id
				return this.tapGuard(key, async () => {
					if (!isLoggedIn()) await silentLogin()
					const ok = await this.askModal({
						title: '确认支付',
						content: `需支付 ¥${item.price}`,
						confirmText: '立即支付',
						confirmColor: '#e54148'
					})
					if (!ok) return
					try {
						const created = await api.createOrder({
							type: 'recommend',
							store_id: String(item.id),
							store_name: item.name,
							title: item.name,
							spec: '订酒店',
							cover: item.cover,
							quantity: 1,
							price: item.price,
							amount: item.price
						})
						if (created && created.id) {
							const payRes = await api.payOrder(created.id)
							await settlePay(payRes)
						}
						uni.showToast({ title: '支付成功', icon: 'success' })
						setTimeout(() => {
							uni.navigateTo({ url: '/pages/orders/orders' })
						}, 600)
					} catch (e) {
						uni.showToast({ title: (e && e.message) || '支付失败', icon: 'none' })
					}
				})
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
		background: #1a1a2e;
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
		overflow: hidden;
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

	.name {
		font-size: 32rpx;
		font-weight: 500;
		color: #222;
		line-height: 1.4;
		display: -webkit-box;
		-webkit-box-orient: vertical;
		-webkit-line-clamp: 2;
		overflow: hidden;
	}

	.action {
		align-self: stretch;
		height: 68rpx;
		display: flex;
		align-items: stretch;
	}

	.price-area {
		flex: 1;
		display: flex;
		align-items: baseline;
		padding: 0 20rpx 0 24rpx;
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
		font-size: 40rpx;
		font-weight: 700;
		color: #e03d47;
		line-height: 68rpx;
	}

	.suffix {
		font-size: 24rpx;
		font-weight: 400;
		color: #e03d47;
		line-height: 68rpx;
		margin-left: 4rpx;
	}

	.buy {
		padding: 0 28rpx;
		background: #fc4f39;
		border-radius: 8rpx;
		display: flex;
		align-items: center;
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
