<template>
	<view class="page">
		<view class="article">
			<text class="title">天天俱乐部积分规则说明</text>
			<view class="meta">
				<text class="author">天天俱乐部</text>
				<text class="dot">·</text>
				<text class="date">2026-09-19</text>
			</view>

			<view class="cover-wrap">
				<image class="cover" src="/static/mall/gift-box.png" mode="aspectFit" />
				<view class="cover-mask">
					<text class="cover-tag">POINTS</text>
					<text class="cover-line">积分换好礼 · 快乐一整天</text>
				</view>
			</view>

			<text class="lead">
				欢迎使用天天俱乐部积分体系。积分可用于商城礼品兑换、活动参与等，具体规则如下。
			</text>

			<view v-for="(sec, i) in sections" :key="i" class="section">
				<view class="sec-head">
					<view class="sec-num">{{ i + 1 }}</view>
					<text class="sec-title">{{ sec.title }}</text>
				</view>
				<view v-for="(p, j) in sec.paras" :key="j" class="sec-p">
					<text class="bullet">·</text>
					<text class="sec-text">{{ p }}</text>
				</view>
			</view>

			<view class="footer">
				<view class="footer-line" />
				<text class="footer-text">本规则由天天俱乐部解释并保留最终调整权利</text>
				<text class="footer-text">如有疑问请联系门店管家或拨打热线 4001919179</text>
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
						title: '如何获取积分',
						paras: [
							'每日签到可获得基础积分，连续签到可解锁额外奖励。',
							'完成门店预约、参与活动、关注并观看视频号直播等，可按活动规则获得积分。',
							'具体单次可获积分以活动页面或系统提示为准。'
						]
					},
					{
						title: '积分用途',
						paras: [
							'积分可在「积分商城」兑换指定礼品、饮品、桌台券等。',
							'部分活动可能支持积分抵扣或积分兑换专属权益。',
							'兑换成功后，请按商品说明到对应门店核销或领取。'
						]
					},
					{
						title: '积分有效期',
						paras: [
							'积分自到账之日起生效，默认长期有效，如有调整将提前公告。',
							'活动限时积分可能设置单独有效期，过期自动失效且不予补发。'
						]
					},
					{
						title: '兑换与核销',
						paras: [
							'兑换前请确认积分余额充足，兑换成功即扣除相应积分。',
							'除商品本身质量问题或门店原因外，已兑换订单一般不支持退换。',
							'核销时请出示兑换凭证，并遵守门店营业时间与使用限制。'
						]
					},
					{
						title: '其他说明',
						paras: [
							'积分不可转让、不可兑现现金，不可与其他优惠叠加时以页面说明为准。',
							'如发现作弊刷分、虚假交易等行为，平台有权冻结积分并取消相关权益。',
							'规则如有更新，以本小程序最新公示内容为准。'
						]
					}
				]
			}
		},
		onLoad() {
			const apply = (lines) => {
				if (!lines || !lines.length) return
				this.sections = [{ title: '积分规则', paras: lines }]
			}
			api.site()
				.then((site) => apply(site && site.mallRules))
				.catch(() => {})
			api.mallGoods()
				.then((res) => apply(res && res.rules))
				.catch(() => {})
		}
	}
</script>

<style>
	.page {
		min-height: 100vh;
		background: #f7f4ef;
		padding-bottom: calc(48rpx + env(safe-area-inset-bottom));
	}

	.article {
		padding: 40rpx 40rpx 0;
	}

	.title {
		display: block;
		font-size: 44rpx;
		font-weight: 700;
		color: #1a1a1a;
		line-height: 1.35;
		letter-spacing: 1rpx;
	}

	.meta {
		margin-top: 24rpx;
		display: flex;
		align-items: center;
	}

	.author {
		font-size: 26rpx;
		color: #e64750;
		font-weight: 600;
	}

	.dot {
		margin: 0 12rpx;
		color: #ccc;
		font-size: 24rpx;
	}

	.date {
		font-size: 24rpx;
		color: #999;
	}

	.cover-wrap {
		margin-top: 36rpx;
		height: 280rpx;
		border-radius: 20rpx;
		overflow: hidden;
		position: relative;
		background: linear-gradient(135deg, #ff6b6f 0%, #e64750 55%, #c93a42 100%);
		display: flex;
		align-items: center;
		justify-content: flex-end;
		padding-right: 24rpx;
	}

	.cover {
		width: 200rpx;
		height: 200rpx;
		opacity: 0.95;
	}

	.cover-mask {
		position: absolute;
		left: 36rpx;
		top: 0;
		bottom: 0;
		display: flex;
		flex-direction: column;
		justify-content: center;
	}

	.cover-tag {
		font-size: 22rpx;
		color: rgba(255, 255, 255, 0.75);
		letter-spacing: 4rpx;
	}

	.cover-line {
		margin-top: 12rpx;
		font-size: 32rpx;
		font-weight: 700;
		color: #fff;
		line-height: 1.4;
	}

	.lead {
		display: block;
		margin-top: 40rpx;
		font-size: 30rpx;
		color: #444;
		line-height: 1.75;
	}

	.section {
		margin-top: 48rpx;
	}

	.sec-head {
		display: flex;
		align-items: center;
		margin-bottom: 20rpx;
	}

	.sec-num {
		width: 40rpx;
		height: 40rpx;
		border-radius: 10rpx;
		background: #e64750;
		color: #fff;
		font-size: 24rpx;
		font-weight: 700;
		display: flex;
		align-items: center;
		justify-content: center;
		margin-right: 16rpx;
		flex-shrink: 0;
	}

	.sec-title {
		font-size: 32rpx;
		font-weight: 700;
		color: #222;
	}

	.sec-p {
		display: flex;
		align-items: flex-start;
		margin-bottom: 16rpx;
		padding-left: 8rpx;
	}

	.bullet {
		width: 28rpx;
		flex-shrink: 0;
		font-size: 30rpx;
		color: #e64750;
		line-height: 1.7;
	}

	.sec-text {
		flex: 1;
		font-size: 28rpx;
		color: #555;
		line-height: 1.7;
	}

	.footer {
		margin-top: 64rpx;
		padding-bottom: 40rpx;
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.footer-line {
		width: 80rpx;
		height: 4rpx;
		border-radius: 2rpx;
		background: #e0d6cc;
		margin-bottom: 28rpx;
	}

	.footer-text {
		font-size: 22rpx;
		color: #aaa;
		line-height: 1.8;
		text-align: center;
	}
</style>
