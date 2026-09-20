<template>
	<view
		v-if="state.visible"
		class="app-loading"
		@tap.stop
		@touchmove.stop.prevent="noop"
	>
		<view class="box">
			<view class="spin" />
			<text class="label">{{ state.title || '加载中' }}</text>
		</view>
	</view>
</template>

<script>
	import { loadingState } from '../../common/loading.js'

	export default {
		computed: {
			state() {
				return loadingState
			}
		},
		methods: {
			noop() {}
		}
	}
</script>

<style>
	.app-loading {
		position: fixed;
		left: 0;
		right: 0;
		top: 0;
		bottom: 0;
		z-index: 10000;
		display: flex;
		align-items: center;
		justify-content: center;
		background: rgba(0, 0, 0, 0.35);
	}

	.box {
		min-width: 200rpx;
		padding: 36rpx 40rpx 32rpx;
		border-radius: 16rpx;
		background: rgba(0, 0, 0, 0.72);
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.spin {
		width: 48rpx;
		height: 48rpx;
		border-radius: 50%;
		border: 4rpx solid rgba(255, 255, 255, 0.28);
		border-top-color: #ffffff;
		animation: app-loading-spin 0.8s linear infinite;
	}

	.label {
		margin-top: 16rpx;
		font-size: 26rpx;
		color: #ffffff;
	}

	@keyframes app-loading-spin {
		from {
			transform: rotate(0deg);
		}
		to {
			transform: rotate(360deg);
		}
	}
</style>
