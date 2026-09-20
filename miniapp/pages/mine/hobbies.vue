<template>
	<view class="page">
		<text class="title">添加兴趣爱好</text>
		<view class="tags">
			<view
				v-for="item in options"
				:key="item.name"
				class="tag"
				:class="{ on: selected.indexOf(item.name) !== -1 }"
				:style="tagStyle(item)"
				@tap="toggle(item.name)"
			>
				{{ item.name }}
			</view>
		</view>
		<view class="footer">
			<view class="done" @tap="onDone">完成</view>
		</view>
	</view>
</template>

<script>
	const PROFILE_KEY = 'gather_profile'
	const HOBBY_KEY = 'gather_hobbies'

	export default {
		data() {
			return {
				selected: [],
				options: [
					{ name: '旅游', color: '#f08a3a' },
					{ name: '美食', color: '#5aa8e8' },
					{ name: '酒店', color: '#3cbf7a' },
					{ name: '休闲娱乐', color: '#8b6bc9' },
					{ name: '线下活动', color: '#3d6fd9' },
					{ name: '老年大学', color: '#e24b4b' }
				]
			}
		},
		onLoad() {
			this.loadSelected()
		},
		methods: {
			loadSelected() {
				try {
					const list = uni.getStorageSync(HOBBY_KEY)
					if (Array.isArray(list) && list.length) {
						this.selected = list.slice()
						return
					}
					const profile = uni.getStorageSync(PROFILE_KEY)
					if (profile && profile.hobby) {
						this.selected = String(profile.hobby)
							.split(/[、,，/\s]+/)
							.map((s) => s.trim())
							.filter(Boolean)
					}
				} catch (e) {}
			},
			tagStyle(item) {
				const on = this.selected.indexOf(item.name) !== -1
				return {
					color: item.color,
					borderColor: item.color,
					background: on ? this.hexToRgba(item.color, 0.12) : '#ffffff'
				}
			},
			hexToRgba(hex, alpha) {
				const h = String(hex).replace('#', '')
				const full = h.length === 3 ? h.split('').map((c) => c + c).join('') : h
				const n = parseInt(full, 16)
				const r = (n >> 16) & 255
				const g = (n >> 8) & 255
				const b = n & 255
				return 'rgba(' + r + ',' + g + ',' + b + ',' + alpha + ')'
			},
			toggle(name) {
				const idx = this.selected.indexOf(name)
				if (idx === -1) {
					this.selected.push(name)
				} else {
					this.selected.splice(idx, 1)
				}
			},
			onDone() {
				const hobby = this.selected.join('、')
				uni.setStorageSync(HOBBY_KEY, this.selected)
				try {
					const profile = uni.getStorageSync(PROFILE_KEY) || {}
					profile.hobby = hobby
					uni.setStorageSync(PROFILE_KEY, profile)
				} catch (e) {}
				uni.navigateBack({ fail() {} })
			}
		}
	}
</script>

<style>
	.page {
		min-height: 100vh;
		box-sizing: border-box;
		background: #ffffff;
		padding: 24rpx 32rpx calc(160rpx + env(safe-area-inset-bottom));
	}

	.title {
		display: block;
		font-size: 34rpx;
		font-weight: 600;
		color: #222222;
		margin: 12rpx 0 36rpx;
	}

	.tags {
		display: flex;
		flex-wrap: wrap;
	}

	.tag {
		padding: 14rpx 28rpx;
		margin: 0 20rpx 24rpx 0;
		border-width: 2rpx;
		border-style: solid;
		border-radius: 8rpx;
		font-size: 28rpx;
		line-height: 1.3;
		box-sizing: border-box;
	}

	.footer {
		position: fixed;
		left: 0;
		right: 0;
		bottom: 0;
		padding: 20rpx 48rpx calc(20rpx + env(safe-area-inset-bottom));
		background: #ffffff;
	}

	.done {
		height: 88rpx;
		border-radius: 999rpx;
		background: #e85a4a;
		color: #ffffff;
		font-size: 32rpx;
		font-weight: 600;
		display: flex;
		align-items: center;
		justify-content: center;
		box-shadow: 0 10rpx 24rpx rgba(232, 90, 74, 0.28);
	}
</style>
