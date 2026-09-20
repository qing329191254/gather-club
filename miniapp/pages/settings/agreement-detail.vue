<template>
	<view class="page">
		<view class="article">
			<text class="title">{{ doc.title }}</text>
			<text class="intro">{{ doc.intro }}</text>

			<view v-for="(block, i) in doc.blocks" :key="i" class="block">
				<text class="heading">{{ block.heading }}</text>
				<text v-for="(p, pi) in block.paras || []" :key="'p' + pi" class="para">{{ p }}</text>
				<view v-for="(sub, si) in block.subs || []" :key="'s' + si" class="sub">
					<text class="sub-title">{{ sub.title }}</text>
					<text v-for="(sp, spi) in sub.paras" :key="'sp' + spi" class="para">{{ sp }}</text>
				</view>
			</view>

			<text v-if="doc.confirm" class="confirm">{{ doc.confirm }}</text>
		</view>
	</view>
</template>

<script>
	import { api } from '../../common/api.js'

	export default {
		data() {
			return {
				doc: {
					title: '',
					intro: '',
					blocks: [],
					confirm: ''
				}
			}
		},
		onLoad(query) {
			const type = (query && query.type) || 'privacy'
			api.agreement(type)
				.then((doc) => {
					if (!doc) {
						uni.showToast({ title: '协议不存在', icon: 'none' })
						return
					}
					this.doc = {
						title: doc.title || '',
						intro: doc.intro || '',
						blocks: doc.blocks || [],
						confirm: doc.confirm || '',
						navTitle: doc.navTitle || ''
					}
					uni.setNavigationBarTitle({ title: this.doc.navTitle || '协议' })
				})
				.catch(() => {
					uni.showToast({ title: '协议不存在', icon: 'none' })
				})
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

	.article {
		display: flex;
		flex-direction: column;
	}

	.title {
		font-size: 36rpx;
		font-weight: 700;
		color: #111111;
		line-height: 1.4;
		margin-bottom: 28rpx;
	}

	.intro,
	.para,
	.confirm {
		font-size: 28rpx;
		color: #222222;
		line-height: 1.75;
		white-space: pre-wrap;
		margin-bottom: 20rpx;
	}

	.block {
		margin-top: 12rpx;
		margin-bottom: 8rpx;
	}

	.heading {
		display: block;
		font-size: 30rpx;
		font-weight: 700;
		color: #111111;
		line-height: 1.5;
		margin: 16rpx 0 12rpx;
	}

	.sub {
		margin-bottom: 8rpx;
	}

	.sub-title {
		display: block;
		font-size: 28rpx;
		font-weight: 600;
		color: #111111;
		line-height: 1.6;
		margin: 10rpx 0 8rpx;
	}

	.confirm {
		margin-top: 28rpx;
		padding-top: 20rpx;
		border-top: 1rpx solid #eeeeee;
		font-weight: 500;
	}
</style>
