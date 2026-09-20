<template>
	<view class="page">
		<view
			v-for="order in orders"
			:key="order.id"
			class="order-card"
			@tap="onOrder(order)"
		>
			<view class="order-head">
				<view class="store-wrap">
					<view class="store-bar" />
					<text class="store-name">{{ order.storeName }}</text>
				</view>
				<text class="order-status">{{ order.statusText }}</text>
			</view>

			<view class="order-body">
				<image class="thumb" :src="order.cover" mode="aspectFill" />
				<view class="info">
					<view class="info-top">
						<text class="title">{{ order.title }}</text>
						<text class="qty">{{ order.quantity }}件</text>
					</view>
					<view class="info-mid">
						<text class="spec">{{ order.spec }}</text>
					</view>
					<view class="info-bottom">
						<view class="spacer" />
						<text class="price">¥{{ order.price }}</text>
					</view>
				</view>
			</view>

			<view
				v-if="order.status === 'pending' || (order.status === 'paid' && order.roomDate)"
				class="order-actions"
				@tap.stop
			>
				<view class="btn ghost" @tap="onCancel(order)">取消订单</view>
				<view v-if="order.status === 'pending'" class="btn solid" @tap="onPay(order)">立即支付</view>
			</view>
		</view>

		<view v-if="!orders.length" class="empty">暂无订单</view>

		<view class="end-line">
			<view class="end-rule" />
			<text class="end-text">{{ loading ? '加载中…' : (hasMore ? '上拉加载更多' : '没有更多了') }}</text>
			<view class="end-rule" />
		</view>
	</view>
</template>

<script>
	import { api } from '../../common/api.js'
	import { settlePay } from '../../common/pay.js'
	import { isLoggedIn, silentLogin } from '../../common/auth.js'

	export default {
		data() {
			return {
				orders: [],
				page: 1,
				pageSize: 20,
				hasMore: true,
				loading: false
			}
		},
		onShow() {
			this.reloadOrders()
		},
		onReachBottom() {
			this.loadMoreOrders()
		},
		methods: {
			mapOrder(row) {
				return {
					id: row.id,
					type: row.type,
					storeId: row.storeId,
					storeName: row.storeName,
					status: row.status,
					statusText: row.statusText,
					cover: row.cover || '/static/orders/nye-xinzhuang.png',
					title: row.title,
					spec: row.spec,
					quantity: row.quantity || 1,
					price: row.price,
					amount: row.amount,
					roomDate: row.roomDate,
					roomSlot: row.roomSlot
				}
			},
			async reloadOrders() {
				this.page = 1
				this.hasMore = true
				this.orders = []
				await this.loadMoreOrders(true)
			},
			async loadMoreOrders(reset) {
				if (this.loading || (!this.hasMore && !reset)) return
				this.loading = true
				try {
					if (!isLoggedIn()) {
						await silentLogin()
					}
					const res = await api.orders({ page: this.page, page_size: this.pageSize })
					const rows = (res.list || []).map((row) => this.mapOrder(row))
					this.orders = reset || this.page === 1 ? rows : this.orders.concat(rows)
					this.hasMore = !!res.has_more
					if (this.hasMore) this.page += 1
				} catch (e) {
					uni.showToast({ title: '订单加载失败', icon: 'none' })
				} finally {
					this.loading = false
				}
			},
			async loadOrders() {
				await this.reloadOrders()
			},
			onOrder(order) {
				if (order.status === 'pending') {
					this.onPay(order)
					return
				}
				api
					.orderDetail(order.id)
					.then((detail) => {
						const lines = [
							detail.storeName || '',
							detail.title || '',
							detail.spec || '',
							detail.statusText || '',
							detail.roomDate ? `用餐：${detail.roomDate} ${detail.roomSlot || ''}` : '',
							detail.contactPhone ? `联系人：${detail.contactName || ''} ${detail.contactPhone}` : ''
						].filter(Boolean)
						uni.showModal({
							title: '订单详情',
							content: lines.join('\n'),
							showCancel: false
						})
					})
					.catch(() => {
						uni.showToast({ title: '订单详情加载失败', icon: 'none' })
					})
			},
			onCancel(order) {
				uni.showModal({
					title: '取消订单',
					content: '确定取消该订单吗？取消后不可恢复',
					confirmColor: '#e54148',
					success: async (res) => {
						if (!res.confirm) return
						try {
							await api.cancelOrder(order.id)
							uni.showToast({ title: '订单已取消', icon: 'none' })
							this.loadOrders()
						} catch (e) {
							uni.showToast({ title: (e && e.message) || '取消失败', icon: 'none' })
						}
					}
				})
			},
			onPay(order) {
				const amount = order.amount || order.price || 0
				uni.showModal({
					title: '确认支付',
					content: `需支付 ¥${amount}`,
					confirmText: '立即支付',
					confirmColor: '#e54148',
					success: async (res) => {
						if (!res.confirm) return
						uni.showLoading({ title: '支付中', mask: true })
						try {
							const payRes = await api.payOrder(order.id)
							await settlePay(payRes)
							uni.hideLoading()
							uni.showToast({ title: '支付成功', icon: 'success' })
							this.loadOrders()
						} catch (e) {
							uni.hideLoading()
							uni.showToast({ title: (e && e.message) || '支付失败', icon: 'none' })
						}
					}
				})
			}
		}
	}
</script>

<style>
	.page {
		min-height: 100vh;
		box-sizing: border-box;
		padding: 24rpx 24rpx calc(40rpx + env(safe-area-inset-bottom));
		background: #f5f5f5;
	}

	.empty {
		text-align: center;
		color: #999;
		padding: 80rpx 0 40rpx;
		font-size: 28rpx;
	}

	.order-card {
		background: #ffffff;
		border-radius: 16rpx;
		padding: 28rpx 24rpx 28rpx;
		margin-bottom: 24rpx;
	}

	.order-head {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 24rpx;
	}

	.store-wrap {
		display: flex;
		align-items: center;
		min-width: 0;
		flex: 1;
		padding-right: 20rpx;
	}

	.store-bar {
		width: 6rpx;
		height: 28rpx;
		border-radius: 6rpx;
		background: #e54148;
		margin-right: 12rpx;
		flex-shrink: 0;
	}

	.store-name {
		font-size: 28rpx;
		color: #222;
		font-weight: 600;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.order-status {
		font-size: 26rpx;
		color: #e54148;
		flex-shrink: 0;
	}

	.order-body {
		display: flex;
	}

	.thumb {
		width: 160rpx;
		height: 160rpx;
		border-radius: 12rpx;
		background: #f0f0f0;
		flex-shrink: 0;
	}

	.info {
		flex: 1;
		margin-left: 20rpx;
		min-width: 0;
		display: flex;
		flex-direction: column;
	}

	.info-top {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
	}

	.title {
		flex: 1;
		font-size: 28rpx;
		color: #222;
		line-height: 1.4;
		padding-right: 12rpx;
	}

	.qty {
		font-size: 24rpx;
		color: #999;
		flex-shrink: 0;
	}

	.info-mid {
		margin-top: 12rpx;
	}

	.spec {
		font-size: 24rpx;
		color: #888;
	}

	.info-bottom {
		margin-top: auto;
		display: flex;
		justify-content: flex-end;
	}

	.spacer {
		flex: 1;
	}

	.price {
		font-size: 32rpx;
		color: #222;
		font-weight: 600;
	}

	.order-actions {
		margin-top: 24rpx;
		padding-top: 20rpx;
		border-top: 1rpx solid #f0f0f0;
		display: flex;
		justify-content: flex-end;
		gap: 16rpx;
	}

	.btn {
		min-width: 160rpx;
		height: 64rpx;
		line-height: 64rpx;
		text-align: center;
		border-radius: 64rpx;
		font-size: 26rpx;
		padding: 0 28rpx;
		box-sizing: border-box;
	}

	.btn.ghost {
		color: #666;
		border: 1rpx solid #ddd;
		background: #fff;
	}

	.btn.solid {
		color: #fff;
		background: #e54148;
	}

	.end-line {
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 24rpx 0 8rpx;
	}

	.end-rule {
		width: 64rpx;
		height: 1rpx;
		background: #ddd;
	}

	.end-text {
		margin: 0 16rpx;
		font-size: 22rpx;
		color: #bbb;
	}
</style>
