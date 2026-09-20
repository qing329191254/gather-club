<template>
	<view class="page">
		<view class="header">
			<view class="header-avatar-wrap">
				<image class="header-avatar" :src="profile.avatar" mode="aspectFill" />
				<view v-if="living" class="live-badge">直播中</view>
			</view>
			<text class="header-name">{{ profile.name }}</text>
		</view>

		<view class="channel-card">
			<view class="cover-wrap">
				<image class="cover" :src="profile.cover" mode="aspectFill" />
			</view>
			<view class="channel">
				<view class="channel-row">
					<image class="channel-avatar" :src="profile.avatar" mode="aspectFill" />
					<text class="channel-name">{{ profile.name }}</text>
					<view class="follow" @tap="onFollow">关注视频号</view>
				</view>
				<text class="intro">{{ profile.intro }}</text>
			</view>
		</view>

		<!-- 直播中 -->
		<view v-if="living" class="live-onair" @tap="onWatch(living)">
			<view class="live-onair-glow"></view>
			<view class="live-onair-inner">
				<view class="onair-badge">
					<view class="eq">
						<view class="eq-bar eq-bar--1"></view>
						<view class="eq-bar eq-bar--2"></view>
						<view class="eq-bar eq-bar--3"></view>
					</view>
					<text>直播中</text>
				</view>
				<view class="live-body">
					<image class="live-avatar" :src="living.avatar || profile.avatar" mode="aspectFill" />
					<view class="live-title">
						<text>{{ living.line1 }}</text>
						<text>{{ living.line2 }}</text>
					</view>
					<view class="watch">
						<view class="watch-heart"><text>♥</text></view>
						<text>看直播</text>
					</view>
				</view>
			</view>
		</view>

		<!-- 预约列表 -->
		<view v-for="item in lives" :key="item.id" class="live" @tap="onReserve(item)">
			<view class="points-flare"></view>
			<view class="live-head">
				<view class="live-schedule">
					<text class="live-tag">开播</text>
					<text class="live-time">{{ item.time }}</text>
				</view>
				<view class="points">
					<view class="coin"><view class="coin-ring"></view></view>
					<text>+{{ item.points }}</text>
				</view>
			</view>
			<view class="live-body">
				<image class="live-avatar" :src="item.avatar || profile.avatar" mode="aspectFill" />
				<view class="live-title">
					<text>{{ item.line1 }}</text>
					<text>{{ item.line2 }}</text>
				</view>
				<view class="reserve">预约直播</view>
			</view>
		</view>

		<app-tabbar :current="2" />
	</view>
</template>

<script>
	export default {
		data() {
			return {
				profile: {
					name: '天天俱乐部',
					avatar: '/static/icons/brand.png',
					cover: '/static/banners/video-cover.png',
					intro: '天天俱乐部！天天都有局！关注直播间，给您带来更多超高性价比的聚会餐，酒店直播！'
				},
				living: null,
				lives: []
			}
		},
		onLoad() {
			this.loadList()
		},
		onShow() {
			uni.hideTabBar({ fail() {} })
		},
		methods: {
			loadList() {
				this.living = {
					id: 0,
					line1: '新锦江4+6+10人',
					line2: '中餐',
					points: 10
				}
				this.lives = [
					{ id: 1, time: '09月20 11:30', line1: '天鹅宾馆下午茶/', line2: '中餐', points: 10 },
					{ id: 2, time: '09月20 16:00', line1: '外高桥喜来登中餐+', line2: '自助下午茶', points: 10 },
					{ id: 3, time: '09月21 11:30', line1: '海伦宾馆4/6/8人', line2: '中餐', points: 10 },
					{ id: 4, time: '09月21 16:00', line1: '虹桥宾馆', line2: '大闸蟹自助', points: 10 },
					{ id: 5, time: '09月22 11:30', line1: '静安洲际大闸蟹晚市自助', line2: '（新品）', points: 10 }
				]
			},
			onFollow() {
				uni.showToast({ title: '关注视频号即将开放', icon: 'none' })
			},
			onWatch() {
				uni.showToast({ title: '直播间即将开放', icon: 'none' })
			},
			onReserve() {
				uni.showToast({ title: '预约直播即将开放', icon: 'none' })
			}
		}
	}
</script>

<style>
	.page {
		min-height: 100vh;
		background: #FDECEC;
		padding-bottom: calc(168rpx + env(safe-area-inset-bottom));
	}

	.header {
		background: linear-gradient(180deg, #F25B5B 0%, #EF4E4E 100%);
		padding: 20rpx 40rpx 48rpx;
		display: flex;
		flex-direction: column;
		align-items: flex-start;
	}

	.header-avatar-wrap {
		position: relative;
		width: 128rpx;
		height: 128rpx;
	}

	.header-avatar {
		width: 128rpx;
		height: 128rpx;
		border-radius: 50%;
		background: #fff;
		border: 6rpx solid rgba(255, 255, 255, 0.9);
		box-sizing: border-box;
	}

	.live-badge {
		position: absolute;
		left: 50%;
		bottom: -6rpx;
		transform: translateX(-50%);
		background: linear-gradient(90deg, #8B6BFF 0%, #E85CFF 55%, #FF6BA8 100%);
		color: #fff;
		font-size: 20rpx;
		line-height: 32rpx;
		padding: 0 14rpx;
		border-radius: 999rpx;
		white-space: nowrap;
		z-index: 1;
		font-weight: 500;
	}

	.header-name {
		margin-top: 22rpx;
		font-size: 28rpx;
		color: #fff;
		width: 140rpx;
		line-height: 1.35;
		font-weight: 500;
	}

	.channel-card {
		margin: -20rpx 24rpx 0;
		border-radius: 20rpx;
		overflow: hidden;
		background: #fff;
		box-shadow: 0 8rpx 24rpx rgba(226, 54, 54, 0.08);
	}

	.cover-wrap {
		height: 320rpx;
		background: #8B1A1A;
	}

	.cover {
		width: 100%;
		height: 100%;
		display: block;
	}

	.channel {
		padding: 24rpx 28rpx 28rpx;
	}

	.channel-row {
		display: flex;
		align-items: center;
	}

	.channel-avatar {
		width: 48rpx;
		height: 48rpx;
		border-radius: 50%;
		margin-right: 12rpx;
		flex-shrink: 0;
		background: #E23636;
	}

	.channel-name {
		flex: 1;
		font-size: 30rpx;
		font-weight: 600;
		color: #1a1a1a;
	}

	.follow {
		background: #E23636;
		color: #fff;
		font-size: 24rpx;
		line-height: 56rpx;
		padding: 0 22rpx;
		border-radius: 28rpx;
	}

	.intro {
		display: block;
		margin-top: 16rpx;
		font-size: 26rpx;
		line-height: 1.55;
		color: #666;
	}

	/* —— 直播中：红色外框选中态，紫色只在标签上 —— */
	.live-onair {
		position: relative;
		margin: 24rpx 24rpx 0;
		padding: 14rpx 12rpx 12rpx;
		border-radius: 24rpx;
		background: linear-gradient(180deg, #FF7A45 0%, #FF9A58 55%, #FFB06A 100%);
		box-sizing: border-box;
		overflow: hidden;
	}

	.live-onair-glow {
		display: none;
	}

	.live-onair-inner {
		position: relative;
		z-index: 1;
		background: #fff;
		border-radius: 16rpx;
		overflow: hidden;
	}

	.onair-badge {
		position: absolute;
		left: 0;
		top: 0;
		display: flex;
		flex-direction: row;
		align-items: center;
		height: 40rpx;
		padding: 0 16rpx 0 12rpx;
		border-radius: 0 0 18rpx 0;
		background: linear-gradient(90deg, #9B5CFF 0%, #FF6BA8 70%, #FF8A5C 100%);
		z-index: 2;
	}

	.onair-badge text {
		font-size: 22rpx;
		color: #fff;
		line-height: 1;
	}

	.eq {
		display: flex;
		flex-direction: row;
		align-items: flex-end;
		height: 18rpx;
		margin-right: 8rpx;
	}

	.eq-bar {
		width: 4rpx;
		border-radius: 2rpx;
		background: #fff;
		margin-right: 3rpx;
		transform-origin: bottom center;
		animation: eq-bounce 0.9s ease-in-out infinite;
	}

	.eq-bar:last-child {
		margin-right: 0;
	}

	.eq-bar--1 {
		height: 8rpx;
		animation-delay: 0s;
	}

	.eq-bar--2 {
		height: 16rpx;
		animation-delay: 0.18s;
	}

	.eq-bar--3 {
		height: 11rpx;
		animation-delay: 0.36s;
	}

	@keyframes eq-bounce {
		0%,
		100% {
			transform: scaleY(0.45);
		}
		35% {
			transform: scaleY(1);
		}
		65% {
			transform: scaleY(0.7);
		}
	}

	/* —— 预约 —— */
	.live {
		position: relative;
		margin: 20rpx 24rpx 0;
		background: #fff;
		border-radius: 20rpx;
		overflow: hidden;
		border: 1rpx solid #F6D5D8;
	}

	.points-flare {
		position: absolute;
		right: 0;
		top: 0;
		width: 220rpx;
		height: 96rpx;
		background: radial-gradient(130% 160% at 100% 0%, #FFF3C4 0%, #FFF6DE 42%, rgba(255, 246, 222, 0) 74%);
		pointer-events: none;
	}

	.live-head {
		display: flex;
		flex-direction: row;
		align-items: center;
		justify-content: space-between;
		padding: 18rpx 20rpx 0;
	}

	.live-schedule {
		display: flex;
		flex-direction: row;
		align-items: center;
		min-width: 0;
	}

	.live-tag {
		font-size: 22rpx;
		color: #fff;
		background: #8B6BFF;
		line-height: 40rpx;
		padding: 0 14rpx;
		border-radius: 10rpx 0 0 10rpx;
		flex-shrink: 0;
	}

	.live-time {
		font-size: 22rpx;
		color: #6A6A88;
		line-height: 40rpx;
		padding: 0 16rpx;
		background: #EFEBF8;
		border-radius: 0 10rpx 10rpx 0;
	}

	.points {
		position: relative;
		z-index: 1;
		display: flex;
		flex-direction: row;
		align-items: center;
		flex-shrink: 0;
		margin-left: 12rpx;
		padding-right: 4rpx;
	}

	.coin {
		width: 36rpx;
		height: 36rpx;
		border-radius: 50%;
		margin-right: 6rpx;
		background: radial-gradient(circle at 32% 28%, #FFF4C2 0%, #F8D56A 28%, #F0B429 58%, #D4890B 100%);
		box-shadow: 0 2rpx 4rpx rgba(180, 110, 0, 0.28), inset 0 2rpx 2rpx rgba(255, 255, 255, 0.85);
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
	}

	.coin-ring {
		width: 20rpx;
		height: 20rpx;
		border-radius: 50%;
		border: 2rpx solid rgba(255, 236, 170, 0.95);
		box-shadow: inset 0 0 0 2rpx rgba(176, 104, 8, 0.4);
		box-sizing: border-box;
	}

	.points text {
		font-size: 26rpx;
		color: #1a1a1a;
		font-weight: 700;
	}

	.live-body {
		display: flex;
		flex-direction: row;
		align-items: center;
		padding: 22rpx 24rpx 28rpx;
	}

	.live-onair .live-body {
		padding: 48rpx 24rpx 28rpx;
	}

	.live-avatar {
		width: 104rpx;
		height: 104rpx;
		border-radius: 50%;
		margin-right: 20rpx;
		flex-shrink: 0;
		background: #E23636;
	}

	.live-title {
		flex: 1;
		min-width: 0;
		display: flex;
		flex-direction: column;
		justify-content: center;
	}

	.live-title text {
		font-size: 30rpx;
		line-height: 1.4;
		color: #1a1a1a;
		font-weight: 500;
	}

	.reserve {
		margin-left: 12rpx;
		background: linear-gradient(90deg, #FF8A28 0%, #FFB24A 100%);
		color: #fff;
		font-size: 24rpx;
		line-height: 60rpx;
		padding: 0 20rpx;
		border-radius: 12rpx;
		flex-shrink: 0;
	}

	.watch {
		margin-left: 12rpx;
		background: #E23636;
		color: #fff;
		font-size: 24rpx;
		line-height: 60rpx;
		padding: 0 18rpx 0 12rpx;
		border-radius: 12rpx;
		flex-shrink: 0;
		display: flex;
		flex-direction: row;
		align-items: center;
	}

	.watch-heart {
		width: 28rpx;
		height: 28rpx;
		border-radius: 50%;
		border: 2rpx solid #fff;
		margin-right: 8rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		box-sizing: border-box;
	}

	.watch-heart text {
		font-size: 14rpx;
		color: #fff;
		line-height: 1;
	}
</style>
