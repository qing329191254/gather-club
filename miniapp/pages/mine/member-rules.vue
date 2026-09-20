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
	import { api } from '../../common/api.js'

	export default {
		data() {
			return {
				sections: []
			}
		},
		onLoad() {
			api.memberConfig()
				.then((cfg) => {
					if (cfg && cfg.rules && cfg.rules.length) {
						this.sections = cfg.rules.map((block) => ({
							...block,
							blocks: block.blocks || [],
							paras: block.paras || []
						}))
					} else {
						uni.showToast({ title: '加载失败', icon: 'none' })
					}
				})
				.catch(() => {
					uni.showToast({ title: '加载失败', icon: 'none' })
				})
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
