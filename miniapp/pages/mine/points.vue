<template>
	<app-loading />
	<view class="page">
		<view class="balance-card">
			<view class="balance-left">
				<text class="balance-num">{{ balance }}</text>
				<text class="balance-tip">可用于兑换通用券、大菜和好礼</text>
			</view>
			<image class="balance-coin" src="/static/icons/coin.png" mode="aspectFit" />
		</view>

		<view class="list">
			<view v-for="item in list" :key="item.id" class="item">
				<image class="item-icon" src="/static/icons/coin.png" mode="aspectFit" />
				<view class="item-main">
					<text class="item-title">{{ item.title }}</text>
					<text class="item-time">{{ item.time }}</text>
				</view>
				<text class="item-value" :class="{ minus: item.value < 0 }">
					{{ formatValue(item.value) }}
				</text>
			</view>
		</view>

		<view v-if="loaded" class="end">{{ loading ? '加载中…' : (hasMore ? '上拉加载更多' : '没有更多了') }}</view>
	</view>
</template>

<script>
	import { getUser, refreshProfile, isLoggedIn, silentLogin } from '../../common/auth.js'
	import { api } from '../../common/api.js'

	export default {
		data() {
			return {
				balance: 0,
				list: [],
				page: 1,
				pageSize: 20,
				hasMore: true,
				loading: false,
				loaded: false
			}
		},
		onShow() {
			this.reloadPoints()
		},
		onReachBottom() {
			this.loadMore()
		},
		methods: {
			formatValue(v) {
				const n = Number(v) || 0
				if (n > 0) return '+' + n
				return String(n)
			},
			async reloadPoints() {
				if (!isLoggedIn()) await silentLogin()
				else await refreshProfile()
				this.balance = getUser().points || 0
				this.page = 1
				this.hasMore = true
				this.list = []
				await this.loadMore(true)
			},
			async loadMore(reset) {
				if (this.loading || (!this.hasMore && !reset)) return
				this.loading = true
				try {
					const res = await api.points({ page: this.page, page_size: this.pageSize })
					this.balance = res.balance != null ? res.balance : this.balance
					const rows = res.list || []
					this.list = reset || this.page === 1 ? rows : this.list.concat(rows)
					this.hasMore = !!res.has_more
					if (this.hasMore) this.page += 1
				} catch (e) {
					if (reset) this.list = []
				} finally {
					this.loading = false
					this.loaded = true
				}
			},
			async loadPoints() {
				await this.reloadPoints()
			}
		}
	}
</script>

<style>
	.page {
		min-height: 100vh;
		background: #f5f5f5;
		padding: 24rpx 24rpx 48rpx;
		box-sizing: border-box;
	}

	.balance-card {
		border-radius: 20rpx;
		padding: 36rpx 32rpx;
		background: linear-gradient(105deg, #ff4d4f 0%, #ff6a3d 48%, #ff8a3a 100%);
		display: flex;
		align-items: center;
		justify-content: space-between;
		overflow: hidden;
		position: relative;
	}

	.balance-left {
		flex: 1;
		min-width: 0;
		z-index: 1;
	}

	.balance-num {
		display: block;
		font-size: 72rpx;
		font-weight: 800;
		color: #ffffff;
		line-height: 1.1;
		margin-bottom: 12rpx;
	}

	.balance-tip {
		display: block;
		font-size: 24rpx;
		color: rgba(255, 255, 255, 0.92);
		line-height: 1.4;
	}

	.balance-coin {
		width: 140rpx;
		height: 140rpx;
		flex-shrink: 0;
		opacity: 0.95;
		margin-left: 12rpx;
	}

	.list {
		margin-top: 20rpx;
	}

	.item {
		display: flex;
		align-items: center;
		background: #ffffff;
		border-radius: 16rpx;
		padding: 28rpx 24rpx;
		margin-bottom: 16rpx;
	}

	.item-icon {
		width: 48rpx;
		height: 48rpx;
		margin-right: 20rpx;
		opacity: 0.55;
		flex-shrink: 0;
	}

	.item-main {
		flex: 1;
		min-width: 0;
	}

	.item-title {
		display: block;
		font-size: 30rpx;
		color: #222222;
		font-weight: 600;
		margin-bottom: 8rpx;
	}

	.item-time {
		display: block;
		font-size: 24rpx;
		color: #999999;
	}

	.item-value {
		font-size: 34rpx;
		font-weight: 700;
		color: #e23636;
		flex-shrink: 0;
		margin-left: 16rpx;
	}

	.item-value.minus {
		color: #666666;
	}

	.end {
		text-align: center;
		font-size: 24rpx;
		color: #bbbbbb;
		padding: 24rpx 0 8rpx;
	}
</style>
