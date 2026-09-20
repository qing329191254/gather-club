<template>
	<view class="page">
		<view class="card">
			<text class="title">您可以通过以下方式联系我们帮您注销账号</text>
			<view class="divider" />
			<view class="contact">
				<text class="line" @tap="callHotline">1.客服热线： 400-920-9400</text>
				<text class="line">2.线下门店： 上海市普陀区普罗娜商务广场B幢1楼</text>
			</view>
			<text class="note">
				*账号注销后，账号中的相关信息将被清除或作废 具体包含：优惠券信息、头像信息等。其中涉及的财产性权益，视为您自愿放弃。
			</text>
			<text class="note">
				即便您后续重新以相同的手机号注册新账号，本账号及其中所有数据、权益均不可恢复，亦无法继续使用。为保障系统安全，防范滥用账号注销、注册功能的行为，您的账号注销后，如需再次以同一手机号申请注册，需要符合我们设置的时间间隔要求（以系统提示为准）。
			</text>
			<text class="foot" @tap="openCancelAgreement">*具体细则以注销协议内容为准。</text>
		</view>
	</view>
</template>

<script>
	export default {
		methods: {
			callHotline() {
				uni.makePhoneCall({ phoneNumber: '4009209400' })
			},
			openCancelAgreement() {
				uni.navigateTo({
					url: '/pages/settings/agreement-detail?type=cancel'
				})
			}
		}
	}
</script>

<style>
	.page {
		min-height: 100vh;
		background: #f5f5f5;
		padding: 24rpx 24rpx 48rpx;
		box-sizing: border-box;
	}

	.card {
		background: #ffffff;
		border-radius: 16rpx;
		padding: 36rpx 32rpx 40rpx;
	}

	.title {
		display: block;
		font-size: 30rpx;
		font-weight: 700;
		color: #111111;
		line-height: 1.5;
	}

	.divider {
		height: 1rpx;
		background: #ececec;
		margin: 28rpx 0;
	}

	.contact {
		margin-bottom: 28rpx;
	}

	.line {
		display: block;
		font-size: 28rpx;
		color: #222222;
		line-height: 1.7;
		margin-bottom: 8rpx;
	}

	.note,
	.foot {
		display: block;
		font-size: 24rpx;
		color: #666666;
		line-height: 1.7;
		margin-bottom: 16rpx;
	}

	.foot {
		margin-bottom: 0;
		margin-top: 8rpx;
	}
</style>
