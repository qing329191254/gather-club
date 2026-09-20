<template>
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
				list: [
					{ type: 'privacy', name: '天天俱乐部用户隐私协议' },
					{ type: 'cancel', name: '注销账号协议' }
				]
			}
		},
		onLoad() {
			api.agreements()
				.then((data) => {
					if (!data) return
					const next = []
					if (data.privacy) next.push({ type: 'privacy', name: data.privacy.title || data.privacy.navTitle || '用户隐私协议' })
					if (data.cancel) next.push({ type: 'cancel', name: data.cancel.title || data.cancel.navTitle || '注销账号协议' })
					if (next.length) this.list = next
				})
				.catch(() => {})
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
