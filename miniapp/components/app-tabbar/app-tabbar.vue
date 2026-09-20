<template>
	<view class="tabbar">
		<view
			v-for="(item, index) in list"
			:key="item.pagePath"
			class="item"
			@tap="onTap(index)"
		>
			<image
				:src="current === index ? item.selectedIconPath : item.iconPath"
				mode="aspectFit"
			/>
			<text :class="{ on: current === index }">{{ item.text }}</text>
		</view>
	</view>
</template>

<script>
	export default {
		name: 'AppTabbar',
		props: {
			current: {
				type: Number,
				default: 0
			}
		},
		data() {
			return {
				list: [
					{
						pagePath: '/pages/index/index',
						text: '首页',
						iconPath: '/static/tab/home-v2.png',
						selectedIconPath: '/static/tab/home-v2-active.png'
					},
					{
						pagePath: '/pages/gather/gather',
						text: '去哪聚',
						iconPath: '/static/tab/gather-v2.png',
						selectedIconPath: '/static/tab/gather-v2-active.png'
					},
					{
						pagePath: '/pages/video/video',
						text: '视频号',
						iconPath: '/static/tab/video-v2.png',
						selectedIconPath: '/static/tab/video-v2-active.png'
					},
					{
						pagePath: '/pages/mine/mine',
						text: '我的',
						iconPath: '/static/tab/mine-v2.png',
						selectedIconPath: '/static/tab/mine-v2-active.png'
					}
				]
			}
		},
		methods: {
			onTap(index) {
				if (index === this.current) return
				uni.switchTab({ url: this.list[index].pagePath })
			}
		}
	}
</script>

<style>
	.tabbar {
		position: fixed;
		left: 0;
		right: 0;
		bottom: 0;
		z-index: 900;
		display: flex;
		align-items: flex-start;
		background: #ffffff;
		border-radius: 36rpx 36rpx 0 0;
		box-shadow: 0 -6rpx 28rpx rgba(0, 0, 0, 0.08);
		padding: 28rpx 0 calc(25rpx + env(safe-area-inset-bottom));
	}

	.item {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.item image {
		width: 64rpx;
		height: 64rpx;
	}

	.item text {
		margin-top: 7rpx;
		font-size: 28rpx;
		line-height: 34rpx;
		color: #1A1C20;
	}

	.item text.on {
		color: #e64750;
		font-weight: 600;
	}
</style>
