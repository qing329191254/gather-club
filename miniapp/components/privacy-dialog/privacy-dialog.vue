<template>
	<view
		v-if="visible"
		class="mask"
		@touchmove.stop.prevent="preventTouchMove"
	>
		<view class="dialog" @tap.stop @touchmove.stop.prevent="preventTouchMove">
			<view class="shield">
				<text class="shield-check">✓</text>
			</view>
			<text class="title">用户隐私保护协议</text>
			<view class="body">
				<text class="p">欢迎使用天天俱乐部小程序。为向您提供注册登录、门店预约、积分兑换等服务，我们需要处理以下信息：</text>
				<text class="p">1. 注册登录：手机号码（用于账号注册与身份核验）；</text>
				<text class="p">2. 基础资料（可选）：头像、昵称；</text>
				<text class="p">3. 交易配送：收货人姓名、地址、联系电话；</text>
				<text class="p">4. 服务优化：设备信息、位置信息等。</text>
				<text class="link" @tap="openPrivacy">《天天俱乐部用户隐私保护协议》</text>
			</view>
			<view class="actions">
				<view class="btn ghost" @tap="onDisagree">不同意</view>
				<view class="btn solid" :class="{ 'tap-busy': busy }" @tap="onAgree">同意并使用</view>
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
		watch: {
			visible(value) {
				if (!value) this.busy = false
			}
		},
		methods: {
			preventTouchMove() {},
			openPrivacy() {
				// 仅允许阅读协议正文，返回后若仍未同意会继续弹窗
				uni.navigateTo({
					url: '/pages/settings/agreement-detail?type=privacy'
				})
			},
			onDisagree() {
				this.$emit('disagree')
			},
			onAgree() {
				if (this.busy) return
				this.busy = true
				this.$emit('agree')
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
		padding: 0 48rpx;
	}

	.dialog {
		width: 100%;
		background: #ffffff;
		border-radius: 24rpx;
		padding: 40rpx 36rpx 36rpx;
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.shield {
		width: 88rpx;
		height: 88rpx;
		border-radius: 50% 50% 46% 46%;
		background: linear-gradient(160deg, #ff8a6b, #e23636);
		display: flex;
		align-items: center;
		justify-content: center;
		margin-bottom: 20rpx;
		box-shadow: 0 8rpx 18rpx rgba(226, 54, 54, 0.28);
	}

	.shield-check {
		color: #ffffff;
		font-size: 44rpx;
		font-weight: 700;
		line-height: 1;
	}

	.title {
		font-size: 34rpx;
		font-weight: 700;
		color: #1a1a1a;
		margin-bottom: 24rpx;
	}

	.body {
		width: 100%;
		margin-bottom: 32rpx;
	}

	.p {
		display: block;
		font-size: 26rpx;
		color: #444444;
		line-height: 1.7;
		margin-bottom: 8rpx;
	}

	.link {
		display: block;
		margin-top: 12rpx;
		font-size: 26rpx;
		color: #e23636;
		text-decoration: underline;
	}

	.actions {
		width: 100%;
		display: flex;
		justify-content: space-between;
		gap: 20rpx;
	}

	.btn {
		flex: 1;
		height: 80rpx;
		border-radius: 999rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 28rpx;
		font-weight: 600;
		box-sizing: border-box;
	}

	.btn.ghost {
		border: 2rpx solid #f0a0a0;
		color: #e23636;
		background: #ffffff;
	}

	.btn.solid {
		background: linear-gradient(90deg, #ff6b7a, #e23636);
		color: #ffffff;
	}
</style>
