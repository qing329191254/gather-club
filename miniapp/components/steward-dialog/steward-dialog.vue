<template>
	<view
		v-if="visible"
		class="qr-mask"
		@tap="onClose"
		@touchmove.stop.prevent="preventTouchMove"
	>
		<view class="qr-dialog" @tap.stop @touchmove.stop.prevent="preventTouchMove">
			<text class="qr-title">{{ title }}</text>
			<image
				class="qr-img"
				:src="qrSrc"
				mode="aspectFit"
				:show-menu-by-longpress="true"
			/>
			<text class="qr-tip">{{ tip }}</text>
			<template v-if="showPhone">
				<view class="qr-line" />
				<text class="qr-phone" @tap="callHotline">热线电话：{{ phone }}</text>
			</template>
			<view v-else class="qr-bottom-space" />
		</view>
	</view>
</template>

<script>
	export default {
		props: {
			visible: {
				type: Boolean,
				default: false
			},
			title: {
				type: String,
				default: '添加管家企业微信'
			},
			tip: {
				type: String,
				default: '长按二维码添加管家微信'
			},
			qrSrc: {
				type: String,
				default: '/static/common/steward-qr.png'
			},
			showPhone: {
				type: Boolean,
				default: true
			},
			phone: {
				type: String,
				default: '4001919179'
			}
		},
		methods: {
			onClose() {
				this.$emit('close')
			},
			preventTouchMove() {},
			callHotline() {
				uni.makePhoneCall({ phoneNumber: String(this.phone).replace(/-/g, '') })
			}
		}
	}
</script>

<style>
	.qr-mask {
		position: fixed;
		left: 0;
		right: 0;
		top: 0;
		bottom: 0;
		z-index: 10000;
		background: rgba(0, 0, 0, 0.55);
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 0 56rpx;
	}

	.qr-dialog {
		width: 100%;
		background: #ffffff;
		border-radius: 20rpx;
		padding: 48rpx 40rpx 0;
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.qr-title {
		font-size: 34rpx;
		font-weight: 600;
		color: #1a1a1a;
		line-height: 1.3;
	}

	.qr-img {
		width: 508rpx;
		height: 508rpx;
		margin-top: 40rpx;
	}

	.qr-tip {
		margin-top: 36rpx;
		font-size: 28rpx;
		color: #303030;
		line-height: 1.3;
	}

	.qr-line {
		width: 100%;
		height: 1rpx;
		background: #e8e8e8;
		margin-top: 40rpx;
	}

	.qr-phone {
		width: 100%;
		text-align: center;
		font-size: 32rpx;
		color: #e64750;
		line-height: 96rpx;
	}

	.qr-bottom-space {
		height: 48rpx;
	}
</style>
