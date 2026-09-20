<template>
	<view class="page">
		<text class="intro">
			《天天俱乐部》小程序可能在向您提供服务的过程中，委托或与第三方共享必要的个人信息。我们仅会出于合法、正当、必要、特定的目的共享信息，并要求接收方按照法律法规与约定保护您的信息。以下为当前涉及的第三方共享情况，便于您查阅。
		</text>

		<view v-for="(sec, i) in sections" :key="i" class="section">
			<view v-if="i > 0" class="divider" />
			<text class="sec-title">{{ sec.title }}</text>
			<view class="row">
				<text class="label">第三方名称：</text>
				<text class="value">{{ sec.name }}</text>
			</view>
			<view class="row">
				<text class="label">共享信息：</text>
				<text class="value">{{ sec.info }}</text>
			</view>
			<view class="row">
				<text class="label">使用目的：</text>
				<text class="value">{{ sec.purpose }}</text>
			</view>
			<view class="row">
				<text class="label">使用场景：</text>
				<text class="value">{{ sec.scene }}</text>
			</view>
			<view class="row">
				<text class="label">共享方式：</text>
				<text class="value">{{ sec.method }}</text>
			</view>
		</view>

		<view class="divider" />
		<text class="foot">
			如第三方变更或新增，我们将适时更新本清单。更多说明可参阅《天天俱乐部用户隐私协议》。
		</text>
	</view>
</template>

<script>
	import { api } from '../../common/api.js'

	export default {
		data() {
			return {
				sections: [
					{
						title: '微信支付',
						name: '财付通支付科技有限公司',
						info: '订单金额、订单号、支付状态等支付必要信息',
						purpose: '完成在线支付、退款及对账',
						scene: '用户下单支付、申请退款时',
						method: '接口调用（SDK / 服务端）'
					},
					{
						title: '微信登录与开放能力',
						name: '深圳市腾讯计算机系统有限公司',
						info: '微信昵称、头像、OpenID/UnionID 等授权标识',
						purpose: '账号登录、身份识别与服务触达',
						scene: '用户授权登录或使用微信相关能力时',
						method: '接口调用（微信开放平台）'
					},
					{
						title: '地图与定位服务',
						name: '腾讯科技（深圳）有限公司（腾讯位置服务）',
						info: '模糊位置信息、门店坐标相关信息',
						purpose: '展示附近门店、路线导航与到店指引',
						scene: '用户查看门店、发起导航或下单自提时',
						method: '接口调用（地图 / 定位 SDK）'
					},
					{
						title: '短信通知服务',
						name: '第三方短信服务商（以实际合作方为准）',
						info: '手机号码、短信模板相关业务变量',
						purpose: '发送验证码、订单/预约等业务通知',
						scene: '需要短信验证或业务提醒时',
						method: '接口调用（服务端）'
					}
				]
			}
		},
		onLoad() {
			api.privacyShare()
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

	.intro,
	.foot {
		display: block;
		font-size: 28rpx;
		color: #222222;
		line-height: 1.75;
		margin-bottom: 36rpx;
	}

	.foot {
		margin-bottom: 0;
		margin-top: 8rpx;
		color: #666666;
		font-size: 26rpx;
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
