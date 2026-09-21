<template>
	<app-loading />
	<view class="page">
		<view class="tabs">
			<view
				v-for="tab in tabs"
				:key="tab.key"
				class="tab"
				:class="{ on: currentTab === tab.key }"
				@tap="switchTab(tab.key)"
			>
				<text>{{ tab.name }}</text>
			</view>
		</view>

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
				<text class="order-status" :class="'st-' + order.status">{{ order.statusText }}</text>
			</view>

			<view class="order-body">
				<image v-if="order.cover" class="thumb" :src="order.cover" mode="aspectFill" />
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
						<text class="price">¥{{ order.amount != null ? order.amount : order.price }}</text>
					</view>
				</view>
			</view>

			<view v-if="order.status === 'paid' && order.type !== 'mall' && order.verifyCode" class="order-actions" @tap.stop>
				<view class="btn solid" @tap="onShowCode(order)">去核销</view>
			</view>

			<view v-if="order.status === 'pending'" class="order-actions" @tap.stop>
				<view class="btn ghost" :class="{ 'tap-busy': isTapBusy('cancel-' + order.id) }" @tap="onCancel(order)">取消订单</view>
				<view class="btn solid" :class="{ 'tap-busy': isTapBusy('pay-' + order.id) }" @tap="onPay(order)">立即支付</view>
			</view>
		</view>

		<view v-if="loaded && !orders.length && !loading" class="empty">暂无订单</view>

		<view class="end-line">
			<view class="end-rule" />
			<text class="end-text">{{ !loaded || loading ? '加载中…' : (hasMore ? '上拉加载更多' : '没有更多了') }}</text>
			<view class="end-rule" />
		</view>
		<verify-code-modal
			:visible="verifyVisible"
			:code="verifyCode"
			:expire="verifyExpire"
			place-label="适用门店："
			:places="verifyPlaces"
			@close="closeVerify"
		/>
	</view>
</template>

<script>
	import { api } from '../../common/api.js'
	import { settlePay } from '../../common/pay.js'
	import { isLoggedIn, silentLogin } from '../../common/auth.js'

	export default {
		data() {
			return {
				tabs: [
					{ key: '', name: '全部' },
					{ key: 'pending', name: '待支付' },
					{ key: 'paid', name: '待核销' },
					{ key: 'completed', name: '已完成' },
					{ key: 'closed', name: '已关闭' }
				],
				currentTab: '',
				orders: [],
				page: 1,
				pageSize: 20,
				hasMore: true,
				loading: false,
				loaded: false,
				verifyVisible: false,
				verifyCode: '',
				verifyExpire: '',
				verifyPlaces: [],
				verifyOrderId: '',
				verifyTimer: null
			}
		},
		onShow() {
			this.reloadOrders()
			if (this.verifyVisible && this.verifyOrderId) this.startVerifyPoll()
		},
		onHide() {
			this.stopVerifyPoll()
		},
		onUnload() {
			this.stopVerifyPoll()
		},
		onReachBottom() {
			this.loadMoreOrders()
		},
		methods: {
			switchTab(key) {
				if (this.currentTab === key) return
				this.currentTab = key
				this.reloadOrders()
			},
			mapOrder(row) {
				return {
					id: row.id,
					type: row.type,
					storeId: row.storeId,
					storeName: row.storeName,
					status: row.status,
					statusText: row.statusText,
					cover: row.cover || '',
					title: row.title,
					spec: row.spec,
					quantity: row.quantity || 1,
					price: row.price,
					amount: row.amount,
					roomDate: row.roomDate,
					roomSlot: row.roomSlot,
					verifyCode: row.verifyCode || ''
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
					const params = { page: this.page, page_size: this.pageSize }
					if (this.currentTab) params.status = this.currentTab
					const res = await api.orders(params)
					const rows = (res.list || []).map((row) => this.mapOrder(row))
					this.orders = reset || this.page === 1 ? rows : this.orders.concat(rows)
					this.hasMore = !!res.has_more
					if (this.hasMore) this.page += 1
				} catch (e) {
					uni.showToast({ title: '订单加载失败', icon: 'none' })
				} finally {
					this.loading = false
					this.loaded = true
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
							detail.roomDate ? `用餐：${detail.roomDate} ${this.slotName(detail.roomSlot)}` : '',
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
			slotName(slot) {
				if (slot === 'lunch') return '午市'
				if (slot === 'dinner') return '晚市'
				return slot || ''
			},
			onShowCode(order) {
				if (!order.verifyCode) return
				const slot = this.slotName(order.roomSlot)
				this.verifyOrderId = order.id
				this.verifyCode = order.verifyCode
				this.verifyExpire = order.roomDate ? `用餐时间：${order.roomDate}${slot ? ' ' + slot : ''}` : ''
				this.verifyPlaces = order.storeName
					? [{ id: order.storeId || order.storeName, name: order.storeName }]
					: []
				this.verifyVisible = true
				this.startVerifyPoll()
			},
			closeVerify() {
				this.verifyVisible = false
				this.verifyOrderId = ''
				this.stopVerifyPoll()
			},
			startVerifyPoll() {
				this.stopVerifyPoll()
				this.pollVerifyOrder()
				this.verifyTimer = setInterval(() => {
					this.pollVerifyOrder()
				}, 2000)
			},
			stopVerifyPoll() {
				if (this.verifyTimer) {
					clearInterval(this.verifyTimer)
					this.verifyTimer = null
				}
			},
			async pollVerifyOrder() {
				const id = this.verifyOrderId
				if (!this.verifyVisible || !id) return
				try {
					const detail = await api.orderDetail(id)
					if (!this.verifyVisible || this.verifyOrderId !== id) return
					if (detail && detail.status && detail.status !== 'paid') {
						this.applyVerifiedOrder(detail)
					}
				} catch (e) {
					/* 网络抖动时继续下一轮 */
				}
			},
			applyVerifiedOrder(detail) {
				const mapped = this.mapOrder(detail)
				this.closeVerify()
				if (this.currentTab && this.currentTab !== mapped.status) {
					this.orders = this.orders.filter((item) => item.id !== mapped.id)
				} else {
					const idx = this.orders.findIndex((item) => item.id === mapped.id)
					if (idx >= 0) this.orders.splice(idx, 1, mapped)
				}
				uni.showToast({ title: mapped.statusText || '已核销', icon: 'none' })
			},
			onCancel(order) {
				const key = 'cancel-' + order.id
				if (!this.holdTap(key)) return
				uni.showModal({
					title: '取消订单',
					content: '确定取消该订单吗？取消后不可恢复',
					confirmColor: '#e54148',
					success: async (res) => {
						if (!res.confirm) {
							this.releaseTap(key)
							return
						}
						try {
							await api.cancelOrder(order.id)
							uni.showToast({ title: '订单已取消', icon: 'none' })
							this.loadOrders()
						} catch (e) {
							uni.showToast({ title: (e && e.message) || '取消失败', icon: 'none' })
						} finally {
							this.releaseTap(key)
						}
					},
					fail: () => this.releaseTap(key)
				})
			},
			onPay(order) {
				const key = 'pay-' + order.id
				if (!this.holdTap(key)) return
				const amount = order.amount || order.price || 0
				uni.showModal({
					title: '确认支付',
					content: `需支付 ¥${amount}`,
					confirmText: '立即支付',
					confirmColor: '#e54148',
					success: async (res) => {
						if (!res.confirm) {
							this.releaseTap(key)
							return
						}
						try {
							const payRes = await api.payOrder(order.id)
							await settlePay(payRes)
							uni.showToast({ title: '支付成功', icon: 'success' })
							this.loadOrders()
						} catch (e) {
							uni.showToast({ title: (e && e.message) || '支付失败', icon: 'none' })
						} finally {
							this.releaseTap(key)
						}
					},
					fail: () => this.releaseTap(key)
				})
			}
		}
	}
</script>

<style>
	.page {
		min-height: 100vh;
		box-sizing: border-box;
		padding: 0 24rpx calc(40rpx + env(safe-area-inset-bottom));
		background: #f5f5f5;
	}

	.tabs {
		display: flex;
		align-items: center;
		margin: 0 -24rpx 8rpx;
		padding: 0 8rpx;
		background: #fff;
		position: sticky;
		top: 0;
		z-index: 5;
	}

	.tab {
		flex: 1;
		height: 84rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 28rpx;
		color: #666;
		position: relative;
	}

	.tab.on {
		color: #e54148;
		font-weight: 600;
	}

	.tab.on::after {
		content: '';
		position: absolute;
		left: 50%;
		bottom: 10rpx;
		width: 40rpx;
		height: 6rpx;
		margin-left: -20rpx;
		border-radius: 6rpx;
		background: #e54148;
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
		margin-top: 24rpx;
		margin-bottom: 0;
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

	.order-status.st-completed {
		color: #16a34a;
	}

	.order-status.st-cancelled,
	.order-status.st-refund_pending,
	.order-status.st-refunded {
		color: #999999;
	}

	.order-status.st-paid {
		color: #d97706;
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
