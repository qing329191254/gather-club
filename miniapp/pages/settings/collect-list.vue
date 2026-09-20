<template>
	<view class="page">
		<text class="intro">{{ intro }}</text>

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
				intro: '',
				sections: []
			}
		},
		onLoad() {
			api.privacyCollect()
				.then((res) => {
					if (res && res.intro) this.intro = res.intro
					if (res && res.sections && res.sections.length) {
						this.sections = res.sections
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
