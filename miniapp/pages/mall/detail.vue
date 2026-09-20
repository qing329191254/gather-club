<template>
	<page-meta :page-style="'overflow:' + (stewardVisible ? 'hidden' : 'visible')"></page-meta>
	<view v-if="goods" class="page">
		<image class="hero" :src="goods.cover" mode="aspectFill" />

		<view class="summary">
			<text class="name">{{ goods.title }}</text>
			<view class="cost-row">
				<image class="coin" src="/static/icons/coin.png" mode="aspectFit" />
				<text class="cost">积分：{{ goods.cost }}</text>
			</view>
			<text class="usage">使用说明：{{ goods.usage }}</text>
			<text class="usage">有效期：{{ goods.valid }}</text>
		</view>

		<view class="desc">
			<text class="desc-title">产品说明</text>
			<image class="desc-img" :src="goods.cover" mode="widthFix" />
			<view class="desc-body">
				<text class="desc-name">{{ goods.title }}</text>
				<text class="desc-line">积分：{{ goods.cost }}</text>
				<text class="desc-line">有效期：{{ goods.valid }}</text>
				<text v-for="(rule, index) in rules" :key="index" class="desc-rule">{{ index + 1 }}. {{ rule }}</text>
			</view>
		</view>

		<view class="bar">
			<view class="service" @tap="openSteward">
				<image src="/static/icons/service.png" mode="aspectFit" />
				<text>客服</text>
			</view>
			<view class="action" :class="{ off: !canRedeem }" @tap="onRedeem">
				{{ canRedeem ? '立即兑换' : '积分不足' }}
			</view>
		</view>

		<steward-dialog :visible="stewardVisible" @close="closeSteward" />
	</view>
</template>

<script>
	import { findMallGoods, mallPoints, mallRules } from '../../common/mall-goods.js'

	export default {
		data() {
			return {
				points: mallPoints,
				goods: null,
				rules: mallRules,
				stewardVisible: false
			}
		},
		computed: {
			canRedeem() {
				return this.goods && this.points >= this.goods.cost
			}
		},
		onLoad(query) {
			const goods = findMallGoods(query.id)
			this.goods = goods
			if (goods) {
				uni.setNavigationBarTitle({ title: goods.title })
			}
		},
		methods: {
			openSteward() {
				this.stewardVisible = true
			},
			closeSteward() {
				this.stewardVisible = false
			},
			onRedeem() {
				if (!this.canRedeem) return
				uni.showToast({ title: '兑换即将开放', icon: 'none' })
			}
		}
	}
</script>

<style>
	.page {
		min-height: 100vh;
		background: #fff;
		padding-bottom: calc(140rpx + env(safe-area-inset-bottom));
	}

	.hero {
		width: 100%;
		height: 560rpx;
		display: block;
		background: #f6f6f6;
	}

	.summary {
		padding: 32rpx 32rpx 8rpx;
	}

	.name {
		display: block;
		font-size: 36rpx;
		font-weight: 700;
		color: #1a1a1a;
		line-height: 1.4;
	}

	.cost-row {
		margin-top: 20rpx;
		display: flex;
		align-items: center;
	}

	.coin {
		width: 36rpx;
		height: 36rpx;
		margin-right: 8rpx;
	}

	.cost {
		font-size: 30rpx;
		font-weight: 600;
		color: #e86b2a;
	}

	.usage {
		display: block;
		margin-top: 16rpx;
		font-size: 26rpx;
		line-height: 1.65;
		color: #888;
	}

	.desc {
		margin-top: 28rpx;
		border-top: 16rpx solid #f5f5f5;
	}

	.desc-title {
		display: block;
		padding: 28rpx 32rpx 20rpx;
		font-size: 32rpx;
		font-weight: 700;
		color: #1a1a1a;
	}

	.desc-img {
		width: 100%;
		display: block;
		background: #f6f6f6;
	}

	.desc-body {
		padding: 28rpx 32rpx 40rpx;
	}

	.desc-name,
	.desc-line,
	.desc-rule {
		display: block;
		font-size: 28rpx;
		line-height: 1.75;
		color: #444;
	}

	.desc-name {
		font-weight: 600;
		color: #222;
	}

	.desc-rule {
		margin-top: 12rpx;
	}

	.bar {
		position: fixed;
		left: 0;
		right: 0;
		bottom: 0;
		z-index: 20;
		display: flex;
		align-items: center;
		padding: 16rpx 24rpx calc(16rpx + env(safe-area-inset-bottom));
		background: #fff;
		border-top: 1rpx solid #eee;
		box-shadow: 0 -4rpx 16rpx rgba(0, 0, 0, 0.04);
	}

	.service {
		width: 112rpx;
		flex-shrink: 0;
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.service image {
		width: 44rpx;
		height: 44rpx;
	}

	.service text {
		margin-top: 4rpx;
		font-size: 22rpx;
		color: #333;
		line-height: 1.2;
	}

	.action {
		flex: 1;
		height: 80rpx;
		line-height: 80rpx;
		text-align: center;
		border-radius: 40rpx;
		background: #e64750;
		color: #fff;
		font-size: 32rpx;
	}

	.action.off {
		background: #c8c8c8;
	}
</style>
