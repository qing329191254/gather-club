<template>
	<app-loading />
	<view class="page">
		<image class="hero" src="/static/checkin/more-gift.png" mode="aspectFit" />
		<text class="title">转发好友领取补签机会</text>
		<text class="desc">点击下方按钮，将小程序转发给好友；好友或你通过转发卡片进入后，即可完成补签领取。</text>
		<button class="share-btn" open-type="share">立即转发</button>
		<text class="tip">每日仅有一次补签机会</text>
	</view>
</template>

<script>
	export default {
		onLoad() {
			uni.showShareMenu({
				withShareTicket: true,
				menus: ['shareAppMessage', 'shareTimeline']
			})
		},
		onShareAppMessage() {
			return {
				title: '送你一次补签机会，快来领取！',
				path: '/pages/checkin/checkin?fromMakeup=1',
				imageUrl: '/static/checkin/share-cover.png'
			}
		}
	}
</script>

<style>
	.page {
		min-height: 100vh;
		box-sizing: border-box;
		padding: 80rpx 48rpx;
		background: linear-gradient(180deg, #ff565c 0%, #ffb08a 45%, #fff5ee 100%);
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.hero {
		width: 280rpx;
		height: 240rpx;
		margin-top: 80rpx;
	}

	.title {
		margin-top: 48rpx;
		font-size: 40rpx;
		font-weight: 700;
		color: #222;
	}

	.desc {
		margin-top: 24rpx;
		font-size: 28rpx;
		color: #666;
		line-height: 1.6;
		text-align: center;
	}

	.share-btn {
		margin-top: 80rpx;
		width: 100%;
		height: 88rpx;
		line-height: 88rpx;
		border-radius: 16rpx;
		background: linear-gradient(90deg, #ff9a4a, #ff7a3a);
		color: #fff;
		font-size: 32rpx;
		font-weight: 600;
		border: none;
	}

	.share-btn::after {
		border: none;
	}

	.tip {
		margin-top: 28rpx;
		font-size: 24rpx;
		color: #b09080;
	}
</style>
