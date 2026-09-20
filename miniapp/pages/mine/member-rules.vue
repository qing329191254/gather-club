<template>
	<view class="page">
		<view class="card">
			<text class="doc-title">天天俱乐部会员章程</text>

			<view v-for="(sec, i) in sections" :key="i" class="section">
				<view class="sec-head">
					<view class="sec-icon" />
					<text class="sec-title">{{ sec.title }}</text>
				</view>

				<view v-for="(block, bi) in sec.blocks" :key="bi" class="block">
					<text v-if="block.subtitle" class="subtitle">{{ block.subtitle }}</text>
					<text
						v-for="(p, pi) in block.paras"
						:key="pi"
						class="para"
						:class="{ tip: p.tip, indent: p.indent }"
					>{{ p.text || p }}</text>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				sections: [
					{
						title: '一、会员等级体系',
						blocks: [
							{
								subtitle: '1.1 等级介绍',
								paras: [
									'会员等级根据用户近365天内在天天俱乐部小程序累计消费桌数评定，共设 V0、V1、V2、V3 四个等级。',
									{
										text: '注：视频号、抖音、美团等外部平台订单不计入会员等级统计。',
										tip: true
									}
								]
							},
							{
								subtitle: '1.2 等级标准',
								paras: [
									{ text: 'V0：仅注册，每年有效桌数为 0 桌', indent: true },
									{ text: 'V1：每年有效桌数为 1 桌', indent: true },
									{ text: 'V2：每年有效桌数为 2–4 桌', indent: true },
									{ text: 'V3：每年有效桌数为 5 桌及以上', indent: true }
								]
							}
						]
					},
					{
						title: '二、会员权益体系详解',
						blocks: [
							{
								subtitle: '2.1 积分倍率',
								paras: [
									{ text: 'V0 / V1 / V2：0.5 倍积分', indent: true },
									{ text: 'V3：1.0 倍积分', indent: true },
									{
										text: '注：首单消费固定按 0.5 倍积分计算。',
										tip: true
									}
								]
							},
							{
								subtitle: '2.2 管家服务',
								paras: [
									{ text: 'V0 / V1：基础客服服务（大众管家）', indent: true },
									{ text: 'V2：专属管家服务（银牌管家）', indent: true },
									{ text: 'V3：金牌管家 1V1 服务', indent: true }
								]
							},
							{
								subtitle: '2.3 生日礼遇',
								paras: [
									{ text: 'V0：无', indent: true },
									{ text: 'V1：门店特色生日面', indent: true },
									{ text: 'V2：特色生日面 + 生日当月出行 2 倍积分', indent: true },
									{
										text: 'V3：生日蛋糕 + 礼品 + 特色生日面 + 生日当月出行 2 倍积分',
										indent: true
									},
									{
										text: '注：生日礼遇适用于 12 人及以上预订，需提前至少 2 天告知门店。',
										tip: true
									}
								]
							},
							{
								subtitle: '2.4 门店礼遇',
								paras: [
									{ text: 'V0 / V1：无', indent: true },
									{
										text: 'V2 / V3：精修合照服务、主题欢迎语 / 活动氛围定制',
										indent: true
									}
								]
							},
							{
								subtitle: '2.5 酒水权益',
								paras: [
									{ text: 'V0 / V1：无', indent: true },
									{ text: 'V2：出行日每桌赠送 1 瓶红酒', indent: true },
									{ text: 'V3：出行日每桌赠送 1 瓶红酒 + 1 道招牌大菜', indent: true },
									{
										text: '注：适用于 12 人及以上预订。',
										tip: true
									}
								]
							},
							{
								subtitle: '2.6 扣损减免',
								paras: [
									{ text: 'V0 / V1 / V2：无', indent: true },
									{ text: 'V3：每年可享 3 次扣损减免', indent: true }
								]
							},
							{
								subtitle: '2.7 优先权益',
								paras: [
									{ text: 'V0 / V1 / V2：无', indent: true },
									{ text: 'V3：包房 / 桌位预订优先权', indent: true }
								]
							},
							{
								subtitle: '2.8 会员券包',
								paras: [
									{ text: 'V0 / V1：黄酒 5 元券 + 红酒 20 元立减券', indent: true },
									{
										text: 'V2：黄酒 5 元券 + 红酒 20 元立减券 + 工作日包房升级券 3 张/年',
										indent: true
									},
									{
										text: 'V3：黄酒 5 元券 + 红酒 20 元立减券 + 工作日包房升级券 6 张/年',
										indent: true
									}
								]
							}
						]
					},
					{
						title: '三、相关规则',
						blocks: [
							{
								subtitle: '3.1 规则调整',
								paras: [
									'天天俱乐部有权根据经营需要调整会员权益、积分规则等内容。规则变更将通过小程序公告等方式告知，自公告之日起 30 日后生效。'
								]
							},
							{
								subtitle: '3.2 合规要求',
								paras: [
									'禁止转赠、出借、倒卖会员权益；禁止使用技术手段刷单、套取积分或优惠；禁止恶意注册、虚假消费等行为。一经发现，平台有权清空相关积分、收回权益，情节严重的可限制或封禁账号。'
								]
							}
						]
					}
				]
			}
		}
	}
</script>

<style>
	.page {
		min-height: 100vh;
		background: #f3e4d2;
		padding: 24rpx 20rpx 48rpx;
		box-sizing: border-box;
	}

	.card {
		background: #ffffff;
		border-radius: 20rpx;
		padding: 40rpx 32rpx 48rpx;
	}

	.doc-title {
		display: block;
		text-align: center;
		font-size: 36rpx;
		font-weight: 700;
		color: #3a2a1a;
		margin-bottom: 36rpx;
	}

	.section {
		margin-bottom: 28rpx;
	}

	.sec-head {
		display: flex;
		align-items: center;
		margin-bottom: 18rpx;
	}

	.sec-icon {
		width: 18rpx;
		height: 18rpx;
		border-radius: 4rpx;
		background: #e67e22;
		margin-right: 12rpx;
		flex-shrink: 0;
	}

	.sec-title {
		font-size: 30rpx;
		font-weight: 700;
		color: #e67e22;
	}

	.block {
		margin-bottom: 18rpx;
	}

	.subtitle {
		display: block;
		font-size: 28rpx;
		font-weight: 600;
		color: #222222;
		margin-bottom: 10rpx;
		line-height: 1.5;
	}

	.para {
		display: block;
		font-size: 26rpx;
		color: #333333;
		line-height: 1.75;
		margin-bottom: 8rpx;
	}

	.para.indent {
		padding-left: 8rpx;
	}

	.para.tip {
		color: #e23636;
		font-size: 24rpx;
		margin-top: 4rpx;
		margin-bottom: 12rpx;
	}
</style>
