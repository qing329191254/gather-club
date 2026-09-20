<template>
	<view
		v-if="visible"
		class="tip-mask"
		@tap="onClose"
		@touchmove.stop.prevent="preventTouchMove"
	>
		<view class="tip-wrap" @tap.stop @touchmove.stop.prevent="preventTouchMove">
			<view class="tip-card">
				<view class="bell-wrap">
					<image class="bell" src="/static/icons/tip-bell.png" mode="aspectFit" />
				</view>
				<text class="title">{{ title }}</text>
				<text class="msg">{{ message }}</text>
				<view class="actions">
					<view class="btn ghost" @tap="onCancel">{{ cancelText }}</view>
					<button
						v-if="phoneAuth"
						class="btn solid phone-auth-btn"
						:class="{ 'tap-busy': busy }"
						open-type="getPhoneNumber"
						@getphonenumber="onGetPhoneNumber"
					>
						{{ confirmText }}
					</button>
					<view v-else class="btn solid" :class="{ 'tap-busy': busy }" @tap="onConfirm">{{ confirmText }}</view>
				</view>
			</view>
			<view class="close" @tap="onClose">
				<text class="x">×</text>
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
			},
			title: {
				type: String,
				default: '温馨提示'
			},
			message: {
				type: String,
				default: '您仅有一次修改机会\n是否确认修改?'
			},
			cancelText: {
				type: String,
				default: '取消'
			},
			confirmText: {
				type: String,
				default: '确认'
			},
			/** 确认按钮唤起微信原生「获取手机号」底部弹层 */
			phoneAuth: {
				type: Boolean,
				default: false
			}
		},
		data() {
			return { busy: false }
		},
		methods: {
			preventTouchMove() {},
			onClose() {
				this.$emit('close')
			},
			onCancel() {
				this.$emit('cancel')
				this.$emit('close')
			},
			onConfirm() {
				if (this.busy) return
				this.busy = true
				this.$emit('confirm')
				this.$emit('close')
				this.busy = false
			},
			onGetPhoneNumber(e) {
				if (this.busy) return
				this.busy = true
				this.$emit('confirm', (e && e.detail) || {})
				this.$emit('close')
			}
		}
	}
</script>

<style>
	.tip-mask {
		position: fixed;
		left: 0;
		right: 0;
		top: 0;
		bottom: 0;
		z-index: 12000;
		background: rgba(0, 0, 0, 0.5);
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 0 88rpx;
	}

	.tip-wrap {
		width: 100%;
		display: flex;
		flex-direction: column;
		align-items: center;
		padding-top: 72rpx;
	}

	.tip-card {
		width: 100%;
		background: linear-gradient(180deg, #fff6f7 0%, #ffffff 38%);
		border-radius: 36rpx;
		padding: 108rpx 44rpx 52rpx;
		position: relative;
		box-shadow: 0 24rpx 56rpx rgba(226, 54, 54, 0.16);
		display: flex;
		flex-direction: column;
		align-items: center;
		box-sizing: border-box;
		min-height: 420rpx;
	}

	.bell-wrap {
		position: absolute;
		left: 50%;
		top: -72rpx;
		transform: translateX(-50%);
		width: 136rpx;
		height: 136rpx;
		border-radius: 50%;
		background: #ffffff;
		display: flex;
		align-items: center;
		justify-content: center;
		box-shadow: 0 12rpx 28rpx rgba(226, 54, 54, 0.14);
	}

	.bell {
		width: 108rpx;
		height: 108rpx;
	}

	.title {
		font-size: 40rpx;
		font-weight: 700;
		color: #1a1a1a;
		margin-bottom: 36rpx;
		line-height: 1.3;
	}

	.msg {
		font-size: 30rpx;
		color: #333333;
		line-height: 1.85;
		text-align: center;
		margin-bottom: 64rpx;
		padding: 0 8rpx;
		white-space: pre-line;
	}

	.actions {
		width: 100%;
		display: flex;
		gap: 24rpx;
		margin-top: auto;
	}

	.btn {
		flex: 1;
		height: 88rpx;
		border-radius: 999rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 32rpx;
		font-weight: 600;
		box-sizing: border-box;
	}

	.btn.ghost {
		background: #ffffff;
		border: 2rpx solid #e85a4a;
		color: #e85a4a;
	}

	.btn.solid {
		background: #e85a4a;
		color: #ffffff;
		border: none;
		padding: 0;
		margin: 0;
		line-height: 88rpx;
	}

	.phone-auth-btn::after {
		border: none;
	}

	.close {
		margin-top: 40rpx;
		width: 72rpx;
		height: 72rpx;
		border-radius: 50%;
		border: 2rpx solid rgba(255, 255, 255, 0.9);
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.x {
		color: #ffffff;
		font-size: 44rpx;
		line-height: 1;
		margin-top: -4rpx;
	}
</style>
