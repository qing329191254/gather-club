<template>
	<view class="page">
		<view class="hero">
			<view class="hero-row">
				<view class="slogan">
					<text>积分换好礼</text>
					<text>零元来抢购</text>
				</view>
				<image class="gift" src="/static/mall/gift-box.png" mode="aspectFit" />
			</view>
		</view>

		<view class="points-card">
			<view class="points-top">
				<text class="points-label">我的积分</text>
				<view class="rules" @tap="onRules">
					<text class="rules-i">i</text>
					<text>积分规则</text>
				</view>
			</view>
			<view class="points-bottom">
				<view class="points-num-wrap">
					<text class="points-num">{{ points }}</text>
					<image class="coin" src="/static/icons/coin.png" mode="aspectFit" />
				</view>
				<view class="record-btn" @tap="onRecord">兑换记录</view>
			</view>
		</view>

		<view class="grid">
			<view
				v-for="item in goods"
				:key="item.id"
				class="goods-card"
				@tap="onGoods(item)"
			>
				<view class="cover-wrap">
					<image class="cover" :src="item.cover" mode="aspectFill" />
					<view v-if="points < item.cost" class="lack">
						<text class="lack-i">i</text>
						<text>积分不足</text>
					</view>
				</view>
				<text class="goods-name">{{ item.name }}</text>
				<view class="cost-row">
					<image class="coin-sm" src="/static/icons/coin.png" mode="aspectFit" />
					<text class="cost">{{ item.cost }}</text>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
	import { api } from '../../common/api.js'
	import { getUser, refreshProfile, silentLogin, isLoggedIn } from '../../common/auth.js'

	export default {
		data() {
			return {
				points: 0,
				goods: []
			}
		},
		onShow() {
			this.loadData()
		},
		methods: {
			async loadData() {
				if (!isLoggedIn()) {
					await silentLogin()
				} else {
					await refreshProfile()
				}
				this.points = getUser().points || 0
				try {
					const res = await api.mallGoods()
					this.goods = Array.isArray(res.list) ? res.list : []
				} catch (e) {
					this.goods = []
					uni.showToast({ title: '加载失败', icon: 'none' })
				}
			},
			onRules() {
				uni.navigateTo({ url: '/pages/mall/rules' })
			},
			onRecord() {
				uni.navigateTo({ url: '/pages/mall/records' })
			},
			onGoods(item) {
				uni.navigateTo({ url: '/pages/mall/detail?id=' + item.id })
			}
		}
	}
</script>

<style>
	.page {
		min-height: 100vh;
		box-sizing: border-box;
		background: #f5f5f5;
		padding-bottom: calc(32rpx + env(safe-area-inset-bottom));
	}

	.hero {
		background: linear-gradient(180deg, #ff5a5f 0%, #ff7a8a 55%, #ff9aa0 100%);
		padding: 24rpx 36rpx 100rpx;
	}

	.hero-row {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.slogan {
		flex: 1;
		display: flex;
		flex-direction: column;
	}

	.slogan text {
		font-size: 48rpx;
		font-weight: 700;
		color: #fff;
		line-height: 1.35;
		letter-spacing: 2rpx;
	}

	.gift {
		width: 200rpx;
		height: 200rpx;
		flex-shrink: 0;
		margin-right: -8rpx;
	}

	.points-card {
		margin: -72rpx 24rpx 0;
		position: relative;
		z-index: 2;
		background: #fff;
		border-radius: 20rpx;
		padding: 28rpx 32rpx 32rpx;
		box-shadow: 0 8rpx 24rpx rgba(200, 60, 60, 0.1);
	}

	.points-top {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.points-label {
		font-size: 28rpx;
		color: #333;
	}

	.rules {
		display: flex;
		align-items: center;
		font-size: 24rpx;
		color: #666;
	}

	.rules-i {
		width: 28rpx;
		height: 28rpx;
		line-height: 28rpx;
		text-align: center;
		border-radius: 50%;
		border: 2rpx solid #999;
		font-size: 20rpx;
		color: #999;
		margin-right: 8rpx;
	}

	.points-bottom {
		margin-top: 20rpx;
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.points-num-wrap {
		display: flex;
		align-items: center;
	}

	.points-num {
		font-size: 64rpx;
		font-weight: 700;
		color: #222;
		line-height: 1;
	}

	.coin {
		width: 40rpx;
		height: 40rpx;
		margin-left: 12rpx;
	}

	.record-btn {
		padding: 0 28rpx;
		height: 56rpx;
		line-height: 56rpx;
		border-radius: 28rpx;
		border: 2rpx solid #ddd;
		font-size: 26rpx;
		color: #333;
	}

	.grid {
		padding: 24rpx 20rpx 0;
		display: flex;
		flex-wrap: wrap;
		justify-content: space-between;
	}

	.goods-card {
		width: 346rpx;
		background: #fff;
		border-radius: 16rpx;
		overflow: hidden;
		margin-bottom: 20rpx;
		padding-bottom: 20rpx;
	}

	.cover-wrap {
		position: relative;
		width: 100%;
		height: 300rpx;
		background: #f0f0f0;
	}

	.cover {
		width: 100%;
		height: 100%;
		display: block;
	}

	.lack {
		position: absolute;
		left: 50%;
		bottom: 20rpx;
		transform: translateX(-50%);
		display: flex;
		align-items: center;
		padding: 0 20rpx;
		height: 44rpx;
		border-radius: 22rpx;
		background: rgba(0, 0, 0, 0.55);
		white-space: nowrap;
	}

	.lack text {
		color: #fff;
		font-size: 22rpx;
	}

	.lack-i {
		width: 24rpx;
		height: 24rpx;
		line-height: 24rpx;
		text-align: center;
		border-radius: 50%;
		border: 2rpx solid #fff;
		font-size: 16rpx;
		margin-right: 8rpx;
	}

	.goods-name {
		display: block;
		margin: 16rpx 16rpx 0;
		font-size: 28rpx;
		color: #222;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.cost-row {
		display: flex;
		align-items: center;
		margin: 12rpx 16rpx 0;
	}

	.coin-sm {
		width: 32rpx;
		height: 32rpx;
		margin-right: 8rpx;
	}

	.cost {
		font-size: 32rpx;
		font-weight: 700;
		color: #e64750;
	}
</style>
