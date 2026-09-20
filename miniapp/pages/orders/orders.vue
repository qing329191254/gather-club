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

		<view class="end-line">
			<view class="end-rule" />
			<text class="end-text">没有更多了</text>
			<view class="end-rule" />
		</view>
	</view>
</template>

<script>
	import { releaseRooms } from '../../common/room-inventory.js'

	const ORDERS_KEY = 'gather_orders_v3'
	const COVER = '/static/orders/nye-xinzhuang.png'

	const defaultOrders = [
		{
			id: 'o-pending-1',
			storeName: '天天俱乐部上海莘庄店',
			status: 'pending',
			statusText: '待支付',
			cover: COVER,
			title: '上海莘庄店-天天俱乐部-2027年夜饭',
			spec: '三羊开泰宴 (10-12人)',
			quantity: 1,
			price: 2688,
			amount: 2688
		},
		{
			id: 'o-cancel-1',
			storeName: '天天俱乐部上海共康店',
			status: 'cancelled',
			statusText: '已取消',
			cover: COVER,
			title: '上海共康店-天天俱乐部-2027年夜饭',
			spec: '喜气羊羊宴 (10-12人)',
			quantity: 1,
			price: 0,
			amount: 1988
		},
		{
			id: 'o-cancel-2',
			storeName: '天天俱乐部上海共康店',
			status: 'cancelled',
			statusText: '已取消',
			cover: COVER,
			title: '上海共康店-天天俱乐部-2027年夜饭',
			spec: '喜气羊羊宴 (10-12人)',
			quantity: 1,
			price: 0,
			amount: 1988
		},
		{
			id: 'o-cancel-3',
			storeName: '天天俱乐部上海共康店',
			status: 'cancelled',
			statusText: '已取消',
			cover: COVER,
			title: '上海共康店-天天俱乐部-2027年夜饭',
			spec: '喜气羊羊宴 (10-12人)',
			quantity: 1,
			price: 0,
			amount: 1988
		}
	]

	export default {
		data() {
			return {
				orders: []
			}
		},
		onShow() {
			this.loadOrders()
		},
		methods: {
			loadOrders() {
				try {
					const raw = uni.getStorageSync(ORDERS_KEY)
					if (Array.isArray(raw) && raw.length) {
						this.orders = raw
						return
					}
				} catch (e) {}
				this.orders = defaultOrders.map((item) => Object.assign({}, item))
				this.persist()
			},
			persist() {
				uni.setStorageSync(ORDERS_KEY, this.orders)
			},
			onOrder(order) {
				if (order.status === 'pending') {
					this.onPay(order)
					return
				}
				uni.showToast({ title: '订单详情即将开放', icon: 'none' })
			},
			onCancel(order) {
				uni.showModal({
					title: '取消订单',
					content: '确定取消该订单吗？取消后不可恢复',
					confirmColor: '#e54148',
					success: (res) => {
						if (!res.confirm) return
						if (order.roomDate && order.roomSlot && order.storeId) {
							releaseRooms({
								storeId: order.storeId,
								date: order.roomDate,
								slot: order.roomSlot,
								qty: order.quantity || 1
							})
						}
						order.status = 'cancelled'
						order.statusText = '已取消'
						order.price = 0
						this.persist()
						uni.showToast({ title: '订单已取消', icon: 'none' })
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
					success: (res) => {
						if (!res.confirm) return
						uni.showLoading({ title: '支付中', mask: true })
						setTimeout(() => {
							uni.hideLoading()
							order.status = 'paid'
							order.statusText = '待核销'
							order.price = amount
							this.persist()
							uni.showToast({ title: '支付成功', icon: 'success' })
						}, 700)
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
		border-radius: 3rpx;
		background: #f08a3a;
		margin-right: 12rpx;
		flex-shrink: 0;
	}

	.store-name {
		font-size: 28rpx;
		color: #333333;
		font-weight: 600;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.order-status {
		font-size: 28rpx;
		color: #f08a3a;
		flex-shrink: 0;
	}

	.order-body {
		display: flex;
		align-items: stretch;
	}

	.thumb {
		width: 160rpx;
		height: 160rpx;
		border-radius: 12rpx;
		flex-shrink: 0;
		background: #eeeeee;
	}

	.info {
		flex: 1;
		min-width: 0;
		margin-left: 20rpx;
		display: flex;
		flex-direction: column;
		justify-content: space-between;
		padding: 2rpx 0;
		min-height: 160rpx;
	}

	.info-top,
	.info-bottom {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
	}

	.info-mid {
		margin-top: 8rpx;
	}

	.title {
		flex: 1;
		min-width: 0;
		font-size: 28rpx;
		color: #222222;
		line-height: 1.4;
		display: -webkit-box;
		-webkit-box-orient: vertical;
		-webkit-line-clamp: 2;
		overflow: hidden;
		padding-right: 16rpx;
		word-break: break-all;
	}

	.qty {
		font-size: 26rpx;
		color: #999999;
		flex-shrink: 0;
		line-height: 1.4;
	}

	.spec {
		font-size: 24rpx;
		color: #999999;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.spacer {
		flex: 1;
	}

	.price {
		font-size: 32rpx;
		color: #e54148;
		font-weight: 700;
		flex-shrink: 0;
		line-height: 1;
	}

	.order-actions {
		margin-top: 28rpx;
		display: flex;
		justify-content: flex-end;
		align-items: center;
	}

	.btn {
		min-width: 168rpx;
		height: 64rpx;
		padding: 0 28rpx;
		border-radius: 12rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 28rpx;
		box-sizing: border-box;
	}

	.btn.ghost {
		margin-right: 16rpx;
		background: #f3f3f3;
		color: #333333;
	}

	.btn.solid {
		background: #e54148;
		color: #ffffff;
	}

	.end-line {
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 40rpx 0 20rpx;
	}

	.end-rule {
		width: 80rpx;
		height: 1rpx;
		background: #dddddd;
	}

	.end-text {
		margin: 0 20rpx;
		font-size: 24rpx;
		color: #bbbbbb;
	}
</style>
