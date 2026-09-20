<template>
	<view class="page">
		<view class="tabs">
			<view
				v-for="tab in tabs"
				:key="tab.key"
				class="tab"
				:class="{ active: current === tab.key }"
				@tap="current = tab.key"
			>
				<text>{{ tab.name }}</text>
				<view v-if="current === tab.key" class="tab-line" />
			</view>
		</view>

		<view v-if="!currentList.length" class="empty">
			<image class="empty-img" src="/static/common/coupon-tickets.png" mode="aspectFit" />
			<text class="empty-text">暂无优惠券</text>
		</view>

		<view v-else class="list">
			<view v-for="item in currentList" :key="item.id" class="coupon">
				<view class="coupon-left">
					<text class="amount">
						<text class="yen">¥</text>{{ item.amount }}
					</text>
					<text class="cond">{{ item.condition }}</text>
				</view>
				<view class="coupon-right">
					<text class="name">{{ item.name }}</text>
					<text class="expire">{{ item.expire }}</text>
					<text v-if="current === 'unused' && item.verifyCode" class="code">核销码 {{ item.verifyCode }}</text>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
	import { api } from '../../common/api.js'
	import { isLoggedIn, silentLogin } from '../../common/auth.js'

	export default {
		data() {
			return {
				current: 'unused',
				tabs: [
					{ key: 'unused', name: '未使用' },
					{ key: 'used', name: '已使用' },
					{ key: 'expired', name: '已过期' }
				],
				coupons: {
					unused: [],
					used: [],
					expired: []
				}
			}
		},
		computed: {
			currentList() {
				return this.coupons[this.current] || []
			}
		},
		onShow() {
			this.loadCoupons()
		},
		methods: {
			async loadCoupons() {
				if (!isLoggedIn()) await silentLogin()
				try {
					const res = await api.coupons()
					this.coupons = {
						unused: res.unused || [],
						used: res.used || [],
						expired: res.expired || []
					}
				} catch (e) {}
			}
		}
	}
</script>

<style>
	.page {
		min-height: 100vh;
		background: #ffffff;
		box-sizing: border-box;
	}

	.tabs {
		display: flex;
		align-items: stretch;
		border-bottom: 1rpx solid #f0f0f0;
		background: #ffffff;
	}

	.tab {
		flex: 1;
		height: 88rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		position: relative;
		font-size: 30rpx;
		color: #333333;
	}

	.tab.active {
		color: #e23636;
		font-weight: 600;
	}

	.tab-line {
		position: absolute;
		left: 50%;
		bottom: 0;
		width: 48rpx;
		height: 6rpx;
		border-radius: 6rpx;
		background: #e23636;
		transform: translateX(-50%);
	}

	.empty {
		padding-top: 180rpx;
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.empty-img {
		width: 320rpx;
		height: 240rpx;
		opacity: 0.85;
	}

	.empty-text {
		margin-top: 28rpx;
		font-size: 28rpx;
		color: #999999;
	}

	.list {
		padding: 24rpx;
	}

	.coupon {
		display: flex;
		background: #fff5f5;
		border-radius: 16rpx;
		overflow: hidden;
		margin-bottom: 20rpx;
		border: 1rpx solid #ffe0e0;
	}

	.coupon-left {
		width: 200rpx;
		padding: 28rpx 16rpx;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		background: linear-gradient(160deg, #ff6b6b, #e23636);
		flex-shrink: 0;
	}

	.amount {
		color: #ffffff;
		font-size: 48rpx;
		font-weight: 800;
		line-height: 1.1;
	}

	.yen {
		font-size: 26rpx;
		font-weight: 600;
		margin-right: 2rpx;
	}

	.cond {
		margin-top: 8rpx;
		font-size: 20rpx;
		color: rgba(255, 255, 255, 0.9);
	}

	.coupon-right {
		flex: 1;
		padding: 28rpx 24rpx;
		display: flex;
		flex-direction: column;
		justify-content: center;
		min-width: 0;
	}

	.name {
		font-size: 28rpx;
		font-weight: 600;
		color: #222222;
		margin-bottom: 10rpx;
	}

	.expire {
		font-size: 22rpx;
		color: #999999;
	}

	.code {
		margin-top: 12rpx;
		font-size: 30rpx;
		font-weight: 700;
		letter-spacing: 2rpx;
		color: #e85a4a;
	}
</style>
