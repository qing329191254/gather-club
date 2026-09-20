<template>
	<app-loading />
	<view class="page">
		<view
			v-for="item in menus"
			:key="item.key"
			class="row"
			@tap="onMenu(item)"
		>
			<text class="name">{{ item.name }}</text>
			<view class="arrow" />
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				menus: [
					{ key: 'agreements', name: '查询协议' },
					{ key: 'cancel', name: '注销账号' },
					{ key: 'collect', name: '个人信息收集清单' },
					{ key: 'share', name: '个人信息三方共享清单' }
				]
			}
		},
		methods: {
			onMenu(item) {
				if (item.key === 'agreements') {
					uni.navigateTo({ url: '/pages/settings/agreements' })
					return
				}
				if (item.key === 'cancel') {
					uni.navigateTo({ url: '/pages/settings/cancel-account' })
					return
				}
				if (item.key === 'collect') {
					uni.navigateTo({ url: '/pages/settings/collect-list' })
					return
				}
				if (item.key === 'share') {
					uni.navigateTo({ url: '/pages/settings/share-list' })
					return
				}
				uni.showToast({ title: (item.name || '功能') + '即将开放', icon: 'none' })
			}
		}
	}
</script>

<style>
	.page {
		min-height: 100vh;
		background: #ffffff;
	}

	.row {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 36rpx 32rpx;
	}

	.name {
		flex: 1;
		font-size: 30rpx;
		font-weight: 600;
		color: #111111;
		line-height: 1.4;
		padding-right: 24rpx;
	}

	.arrow {
		width: 14rpx;
		height: 14rpx;
		border-top: 3rpx solid #c8c8c8;
		border-right: 3rpx solid #c8c8c8;
		transform: rotate(45deg);
		flex-shrink: 0;
	}
</style>
