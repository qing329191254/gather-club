<template>
	<app-loading />
	<view class="page">
		<view
			v-for="item in list"
			:key="item.type"
			class="row"
			@tap="openAgreement(item)"
		>
			<text class="name">{{ item.name }}</text>
			<view class="arrow" />
		</view>
	</view>
</template>

<script>
	import { api } from '../../common/api.js'

	export default {
		data() {
			return {
				list: []
			}
		},
		onLoad() {
			api.agreements()
				.then((data) => {
					if (!data) {
						uni.showToast({ title: '加载失败', icon: 'none' })
						return
					}
					const next = []
					if (data.privacy) next.push({ type: 'privacy', name: data.privacy.title || data.privacy.navTitle || '用户隐私协议' })
					if (data.cancel) next.push({ type: 'cancel', name: data.cancel.title || data.cancel.navTitle || '注销账号协议' })
					this.list = next
					if (!next.length) uni.showToast({ title: '加载失败', icon: 'none' })
				})
				.catch(() => {
					uni.showToast({ title: '加载失败', icon: 'none' })
				})
		},
		methods: {
			openAgreement(item) {
				uni.navigateTo({
					url: '/pages/settings/agreement-detail?type=' + item.type
				})
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
