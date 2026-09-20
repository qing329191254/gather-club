<template>
	<view v-if="item" class="page">
		<image class="cover" :src="item.cover" mode="aspectFill" />
		<view class="body">
			<text class="title">{{ item.title }}</text>
			<view v-if="item.tag" class="tag">{{ item.tag }}</view>
			<view v-if="item.tags && item.tags.length" class="chips">
				<text v-for="chip in item.tags" :key="chip" class="chip">{{ chip }}</text>
			</view>
			<view class="price-row">
				<text class="price">¥{{ item.price }}</text>
				<text v-if="item.originPrice" class="origin">¥{{ item.originPrice }}</text>
			</view>
			<text v-if="item.soldText" class="sold">{{ item.soldText }}</text>
		</view>
		<view class="bar">
			<view class="buy" @tap="onBuy">立即购买</view>
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
				item: null
			}
		},
		onLoad(query) {
			const id = (query && query.id) || ''
			if (!id) return
			api.gatherProduct(id)
				.then((res) => {
					this.item = res
				})
				.catch(() => {
					uni.showToast({ title: '商品不存在', icon: 'none' })
				})
		},
		methods: {
			async onBuy() {
				const item = this.item
				if (!item) return
				if (!isLoggedIn()) await silentLogin()
				uni.showModal({
					title: '确认支付',
					content: `需支付 ¥${item.price}`,
					confirmText: '立即支付',
					confirmColor: '#e54148',
					success: async (res) => {
						if (!res.confirm) return
						uni.showLoading({ title: '支付中', mask: true })
						try {
							const created = await api.createOrder({
								type: 'gather',
								store_id: item.id,
								store_name: item.title,
								title: item.title,
								spec: item.tag || '去哪聚',
								cover: item.cover,
								quantity: 1,
								price: item.price,
								amount: item.price
							})
							if (created && created.id) {
								const payRes = await api.payOrder(created.id)
								await settlePay(payRes)
							}
							uni.hideLoading()
							uni.showToast({ title: '支付成功', icon: 'success' })
							setTimeout(() => {
								uni.navigateTo({ url: '/pages/orders/orders' })
							}, 600)
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
		background: #f5f5f5;
		padding-bottom: calc(140rpx + env(safe-area-inset-bottom));
	}

	.cover {
		width: 100%;
		height: 520rpx;
		background: #eee;
		display: block;
	}

	.body {
		background: #fff;
		padding: 32rpx;
	}

	.title {
		display: block;
		font-size: 36rpx;
		font-weight: 600;
		color: #222;
		line-height: 1.4;
	}

	.tag {
		display: inline-block;
		margin-top: 16rpx;
		font-size: 22rpx;
		color: #e03d47;
		background: #fef4ef;
		padding: 4rpx 12rpx;
		border-radius: 6rpx;
	}

	.chips {
		margin-top: 16rpx;
		display: flex;
		flex-wrap: wrap;
	}

	.chip {
		font-size: 22rpx;
		color: #666;
		background: #f5f5f5;
		padding: 4rpx 12rpx;
		border-radius: 6rpx;
		margin-right: 12rpx;
		margin-bottom: 8rpx;
	}

	.price-row {
		margin-top: 24rpx;
		display: flex;
		align-items: baseline;
	}

	.price {
		font-size: 44rpx;
		font-weight: 700;
		color: #e03d47;
	}

	.origin {
		margin-left: 16rpx;
		font-size: 26rpx;
		color: #bbb;
		text-decoration: line-through;
	}

	.sold {
		display: block;
		margin-top: 12rpx;
		font-size: 24rpx;
		color: #999;
	}

	.bar {
		position: fixed;
		left: 0;
		right: 0;
		bottom: 0;
		background: #fff;
		padding: 16rpx 32rpx calc(16rpx + env(safe-area-inset-bottom));
		box-shadow: 0 -2rpx 12rpx rgba(0, 0, 0, 0.06);
	}

	.buy {
		height: 88rpx;
		background: #fc4f39;
		color: #fff;
		border-radius: 12rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 32rpx;
		font-weight: 600;
	}
</style>
