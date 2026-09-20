<template>
	<view
		v-if="visible"
		class="mask"
		@touchmove.stop.prevent="preventTouchMove"
	>
		<view class="dialog" @tap.stop @touchmove.stop.prevent="preventTouchMove">
			<text class="title">手机号快捷登录</text>
			<text class="desc">为了给您提供更好的服务，请授权您的手机号</text>
			<view class="actions">
				<view class="btn ghost" @tap="onCancel">取消</view>
				<!-- 真机可换 open-type="getPhoneNumber"；演示环境用确认完成登录 -->
				<button class="btn solid phone-btn" @tap="onConfirm">确认</button>
			</view>
		</view>
	</view>
</template>

<script>
	export default {
		props: {
			visible: {
				type: Boolean,
				default: false
			}
		},
		methods: {
			preventTouchMove() {},
			onCancel() {
				this.$emit('cancel')
			},
			onConfirm() {
				this.$emit('confirm')
			}
		}
	}
</script>

<style>
	.mask {
		position: fixed;
		left: 0;
		right: 0;
		top: 0;
		bottom: 0;
		z-index: 11000;
		background: rgba(0, 0, 0, 0.55);
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 0 72rpx;
	}

	.dialog {
		width: 100%;
		background: #ffffff;
		border-radius: 20rpx;
		padding: 44rpx 36rpx 36rpx;
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.title {
		font-size: 34rpx;
		font-weight: 700;
		color: #1a1a1a;
		margin-bottom: 28rpx;
	}

	.desc {
		font-size: 28rpx;
		color: #333333;
		line-height: 1.6;
		text-align: center;
		margin-bottom: 40rpx;
	}

	.actions {
		width: 100%;
		display: flex;
		justify-content: space-between;
		gap: 20rpx;
	}

	.btn {
		flex: 1;
		height: 76rpx;
		border-radius: 999rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 28rpx;
		font-weight: 600;
		box-sizing: border-box;
		margin: 0;
		padding: 0;
		line-height: 76rpx;
	}

	.btn.ghost {
		border: 2rpx solid #d8d8d8;
		color: #888888;
		background: #ffffff;
	}

	.btn.solid,
	.phone-btn {
		background: #e23636;
		color: #ffffff;
		border: none;
	}

	.phone-btn::after {
		border: none;
	}
</style>
