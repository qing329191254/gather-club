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
		<view v-if="!loading && !options.length" class="empty">暂无可选兴趣，请稍后再试</view>
		<view class="footer">
			<view class="done" @tap="onDone">完成</view>
		</view>
	</view>
</template>

<script>
	import { api } from '../../common/api.js'
	import { getUser, isLoggedIn, saveLogin, silentLogin } from '../../common/auth.js'

	const PROFILE_KEY = 'gather_profile'
	const HOBBY_KEY = 'gather_hobbies'
	const FALLBACK_OPTIONS = [
		{ name: '旅游', color: '#f08a3a' },
		{ name: '美食', color: '#5aa8e8' },
		{ name: '酒店', color: '#3cbf7a' },
		{ name: '休闲娱乐', color: '#8b6bc9' },
		{ name: '线下活动', color: '#3d6fd9' },
		{ name: '老年大学', color: '#e24b4b' }
	]

	export default {
		data() {
			return {
				loading: false,
				selected: [],
				options: []
			}
		},
		onLoad() {
			this.loadSelected()
			this.loadOptions()
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
					const hobby = (profile && profile.hobby) || (getUser() && getUser().hobby) || ''
					if (hobby) {
						this.selected = String(hobby)
							.split(/[、,，/\s]+/)
							.map((s) => s.trim())
							.filter(Boolean)
					}
				} catch (e) {}
			},
			async loadOptions() {
				this.loading = true
				try {
					const res = await api.hobbyOptions()
					const items = (res && res.items) || []
					this.options = items.length
						? items.map((i) => ({
								name: i.name,
								color: i.color || '#e85a4a'
						  }))
						: FALLBACK_OPTIONS.slice()
				} catch (e) {
					this.options = FALLBACK_OPTIONS.slice()
				} finally {
					this.loading = false
				}
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
			async onDone() {
				const hobby = this.selected.join('、')
				uni.setStorageSync(HOBBY_KEY, this.selected)
				try {
					const profile = uni.getStorageSync(PROFILE_KEY) || {}
					profile.hobby = hobby
					uni.setStorageSync(PROFILE_KEY, profile)
				} catch (e) {}
				uni.showLoading({ title: '保存中', mask: true })
				try {
					if (!isLoggedIn()) await silentLogin()
					const res = await api.updateProfile({ hobby })
					saveLogin(
						Object.assign({}, getUser(), {
							hobby: (res && res.hobby) || hobby
						})
					)
					uni.hideLoading()
					uni.navigateBack({ fail() {} })
				} catch (e) {
					uni.hideLoading()
					uni.showToast({ title: (e && e.message) || '保存失败', icon: 'none' })
				}
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

	.empty {
		margin-top: 40rpx;
		text-align: center;
		color: #999999;
		font-size: 28rpx;
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
