<template>
	<app-loading />
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

			<text class="lead">{{ intro }}</text>

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
				intro: '',
				sections: []
			}
		},
		onLoad() {
			const apply = (lines, intro) => {
				if (intro) this.intro = intro
				if (!lines || !lines.length) return false
				this.sections = [{ title: '积分规则', paras: lines }]
				return true
			}
			Promise.all([
				api.site().catch(() => null),
				api.mallGoods().catch(() => null)
			])
				.then(([site, mall]) => {
					const fromSite = apply(site && site.mallRules, site && site.mallRulesIntro)
					const fromMall = apply(mall && mall.rules, mall && mall.rulesIntro)
					if (!fromSite && !fromMall) {
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
		color: #C6453C;
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
		background: #C6453C;
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
		background: #C6453C;
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
		color: #C6453C;
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
