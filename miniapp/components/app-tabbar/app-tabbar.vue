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
						iconPath: '/static/tab/home-v3.png',
						selectedIconPath: '/static/tab/home-v3-active.png'
					},
					{
						pagePath: '/pages/gather/gather',
						text: '聚餐',
						iconPath: '/static/tab/gather-v3.png',
						selectedIconPath: '/static/tab/gather-v3-active.png'
					},
					{
						pagePath: '/pages/video/video',
						text: '视频号',
						iconPath: '/static/tab/video-v3.png',
						selectedIconPath: '/static/tab/video-v3-active.png'
					},
					{
						pagePath: '/pages/mine/mine',
						text: '我的',
						iconPath: '/static/tab/mine-v3.png',
						selectedIconPath: '/static/tab/mine-v3-active.png'
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
		border-radius: 0;
		border-top: 1rpx solid #E6E1DA;
		box-shadow: none;
		padding: 16rpx 0 calc(16rpx + env(safe-area-inset-bottom));
	}

	.item {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.item image {
		width: 52rpx;
		height: 52rpx;
	}

	.item text {
		margin-top: 6rpx;
		font-size: 22rpx;
		line-height: 30rpx;
		color: #8A847C;
	}

	.item text.on {
		color: #C6453C;
		font-weight: 600;
	}
</style>
