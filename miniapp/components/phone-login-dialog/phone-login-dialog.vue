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
				<button
					class="btn solid phone-btn"
					:class="{ 'tap-busy': busy }"
					open-type="getPhoneNumber"
					@getphonenumber="onGetPhoneNumber"
				>
					确认
				</button>
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
		data() {
			return { busy: false }
		},
		methods: {
			preventTouchMove() {},
			onCancel() {
				this.$emit('cancel')
			},
			onGetPhoneNumber(e) {
				if (this.busy) return
				this.busy = true
				this.$emit('confirm', (e && e.detail) || {})
			},
			resetBusy() {
				this.busy = false
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
		flex-direction: row;
		gap: 20rpx;
	}

	.btn {
		flex: 1;
		height: 80rpx;
		line-height: 80rpx;
		text-align: center;
		border-radius: 12rpx;
		font-size: 30rpx;
		font-weight: 500;
	}

	.ghost {
		background: #f3f3f3;
		color: #666;
	}

	.phone-btn {
		background: #e23636;
		color: #fff;
		padding: 0;
		margin: 0;
		border: none;
	}

	.phone-btn::after {
		border: none;
	}
</style>
