<template>
	<view class="page">
		<text class="intro">
			《天天俱乐部》小程序尊重并保护您的隐私，并将依照适用法律的要求在处理个人信息过程中采取必要的保护措施以保证您个人信息的安全性。为了向您提供本小程序的基本功能以及附加功能，我们需要收集您的个人信息，或者申请打开您设备的特定权限。以下我们将逐一说明您个人信息的收集情况，以便您快速查阅。
		</text>

		<view v-for="(sec, i) in sections" :key="i" class="section">
			<view v-if="i > 0" class="divider" />
			<text class="sec-title">{{ sec.title }}</text>
			<view class="row">
				<text class="label">信息内容：</text>
				<text class="value">{{ sec.content }}</text>
			</view>
			<view class="row">
				<text class="label">使用目的：</text>
				<text class="value">{{ sec.purpose }}</text>
			</view>
			<view class="row">
				<text class="label">使用场景：</text>
				<text class="value">{{ sec.scene }}</text>
			</view>
		</view>
	</view>
</template>

<script>
	import { api } from '../../common/api.js'

	export default {
		data() {
			return {
				sections: [
					{
						title: '账号注册与登录',
						content: '微信头像、昵称、手机号、性别',
						purpose: '创建账户，个人主页信息展示，完善网络身份标识',
						scene: '用户主动填写或授权微信头像昵称手机号'
					},
					{
						title: '位置信息',
						content: '模糊地址位置',
						purpose: '展示自提商品附近门店信息',
						scene: '下单'
					},
					{
						title: '下单与订单管理',
						content: '包括姓名、收货地址、订单信息明细',
						purpose: '创建订单，历史交易信息展示与查询',
						scene: '下单与订单查询'
					},
					{
						title: '设备信息',
						content: '操作系统版本、型号、设备标识符',
						purpose: '适配当前设备；保障账户安全；保障安全交易；分析与统计',
						scene: '进入小程序时'
					}
				]
			}
		},
		onLoad() {
			api.privacyCollect()
				.then((res) => {
					if (res && res.sections && res.sections.length) this.sections = res.sections
				})
				.catch(() => {})
		}
	}
</script>

<style>
	.page {
		min-height: 100vh;
		background: #ffffff;
		padding: 32rpx 36rpx 80rpx;
		box-sizing: border-box;
	}

	.intro {
		display: block;
		font-size: 28rpx;
		color: #222222;
		line-height: 1.75;
		margin-bottom: 36rpx;
	}

	.section {
		padding-bottom: 8rpx;
	}

	.divider {
		height: 1rpx;
		background: #ececec;
		margin: 28rpx 0 32rpx;
	}

	.sec-title {
		display: block;
		font-size: 30rpx;
		font-weight: 700;
		color: #111111;
		line-height: 1.4;
		margin-bottom: 16rpx;
	}

	.row {
		display: flex;
		align-items: flex-start;
		margin-bottom: 10rpx;
	}

	.label {
		flex-shrink: 0;
		font-size: 28rpx;
		color: #222222;
		line-height: 1.7;
	}

	.value {
		flex: 1;
		font-size: 28rpx;
		color: #222222;
		line-height: 1.7;
	}
</style>
