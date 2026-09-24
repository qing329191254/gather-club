<template>
	<view
		v-if="visible"
		class="coupon-mask"
		@tap="onKnow"
		@touchmove.stop.prevent="preventTouchMove"
	>
		<view class="coupon-wrap" @tap.stop @touchmove.stop.prevent="preventTouchMove">
			<image
				class="coupon-illust"
				src="/static/common/coupon-tickets.png"
				mode="widthFix"
			/>
			<view class="coupon-dialog">
				<view class="coupon-msg">
					<text>您有优惠券可兑换，</text>
					<text>是否前往兑换？</text>
				</view>
				<view class="coupon-actions">
					<view class="coupon-btn ghost" @tap="onKnow">知道了</view>
					<view class="coupon-btn solid" @tap="onGo">去兑换</view>
				</view>
			</view>
			<view class="coupon-close" @tap="onClose">
				<text class="coupon-x">×</text>
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
			onKnow() {
				this.$emit('know')
			},
			onGo() {
				this.$emit('go')
			},
			onClose() {
				this.$emit('close')
			}
		}
	}
</script>

<style>
	.coupon-mask {
		position: fixed;
		left: 0;
		right: 0;
		top: 0;
		bottom: 0;
		z-index: 1100;
		background: rgba(0, 0, 0, 0.5);
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 0 64rpx;
		box-sizing: border-box;
	}

	.coupon-wrap {
		width: 100%;
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.coupon-illust {
		position: relative;
		z-index: 2;
		width: 300rpx;
		margin-bottom: -80rpx;
		background: transparent;
	}

	.coupon-dialog {
		width: 100%;
		border-radius: 12rpx;
		padding: 100rpx 36rpx 40rpx;
		box-sizing: border-box;
		display: flex;
		flex-direction: column;
		align-items: center;
		background: #fff;
		box-shadow: none;
		border: 1rpx solid #E8E2DA;
	}

	.coupon-msg {
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.coupon-msg text {
		display: block;
		font-size: 34rpx;
		font-weight: 700;
		color: #2a2a2a;
		line-height: 1.55;
		text-align: center;
	}

	.coupon-actions {
		width: 100%;
		margin-top: 44rpx;
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.coupon-btn {
		width: 48%;
		height: 84rpx;
		line-height: 84rpx;
		text-align: center;
		border-radius: 10rpx;
		font-size: 30rpx;
		font-weight: 600;
		box-sizing: border-box;
	}

	.coupon-btn.ghost {
		border: 2rpx solid #D8D0C6;
		color: #6B635C;
		background: #fff;
		line-height: 80rpx;
	}

	.coupon-btn.solid {
		background: #C6453C;
		color: #fff;
		box-shadow: none;
	}

	.coupon-close {
		margin-top: 40rpx;
		width: 68rpx;
		height: 68rpx;
		border-radius: 50%;
		border: 3rpx solid rgba(255, 255, 255, 0.95);
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.coupon-x {
		color: #fff;
		font-size: 48rpx;
		line-height: 1;
		font-weight: 300;
		margin-top: -4rpx;
	}
</style>
