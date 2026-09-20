<template>
	<page-meta :page-style="'overflow:' + (stewardVisible || phoneLoginVisible ? 'hidden' : 'visible')"></page-meta>
	<view class="page">
		<view class="hero" :style="{ paddingTop: statusBarHeight + 'px' }">
			<image class="hero-bg" src="/static/mine-header.png" mode="aspectFill" />
			<view class="hero-space" />
		</view>

		<view class="user-card" @tap="onProfile">
			<image class="avatar" :src="user.avatar || '/static/icons/avatar-default.png'" mode="aspectFill" />
			<view class="user-main">
				<view class="hello-row">
					<text class="hello">{{ greeting }}</text>
					<text class="name">{{ user.nickname }}</text>
				</view>
				<view class="profile-link">
					<image class="edit" src="/static/icons/edit.png" mode="aspectFit" />
					<text>完善资料</text>
				</view>
			</view>
			<view class="vip-badge" @tap.stop="onVip">
				<image class="vip-icon" :src="vipInfo.icon" mode="aspectFit" />
				<view
					class="vip-pill"
					:style="'background:' + vipInfo.theme.pill + ';'"
				>
					<text class="vip-level" :style="{ color: vipInfo.theme.text }">{{ vipInfo.label }}</text>
				</view>
			</view>
		</view>

		<view class="points-card" @tap="onMenu({ key: 'points', name: '积分明细' })">
			<view class="points-left">
				<image class="coin" src="/static/icons/coin.png" mode="aspectFit" />
				<text>积分</text>
				<text class="points-num">{{ user.points }}</text>
			</view>
			<view class="points-more">
				<text>积分明细</text>
				<view class="arrow" />
			</view>
		</view>

		<view class="menu-card">
			<view v-for="item in menus" :key="item.key" class="menu-item" @tap="onMenu(item)">
				<image class="menu-icon" :src="item.icon" mode="aspectFit" />
				<text class="menu-name">{{ item.name }}</text>
				<view class="arrow" />
			</view>
		</view>
		<app-tabbar :current="3" />
		<steward-dialog :visible="stewardVisible" @close="closeSteward" />
		<phone-login-dialog
			:visible="phoneLoginVisible"
			@cancel="onPhoneCancel"
			@confirm="onPhoneConfirm"
		/>
	</view>
</template>

<script>
	import {
		getUser,
		isLoggedIn,
		needPhoneLoginPrompt,
		silentLogin
	} from '../../common/auth.js'
	import { resolveVip } from '../../common/vip-levels.js'

	export default {
		data() {
			return {
				statusBarHeight: 20,
				stewardVisible: false,
				phoneLoginVisible: false,
				user: getUser(),
				menus: [
					{ key: 'order', name: '我的订单', icon: '/static/icons/menu-order.png' },
					{ key: 'coupon', name: '优惠券', icon: '/static/icons/menu-coupon.png' },
					{ key: 'mall', name: '积分商城', icon: '/static/icons/menu-mall.png' },
					{ key: 'service', name: '联系客服', icon: '/static/icons/menu-service.png' },
					{ key: 'address', name: '收货地址', icon: '/static/icons/menu-address.png' },
					{ key: 'setting', name: '设置', icon: '/static/icons/menu-setting.png' }
				]
			}
		},
		computed: {
			greeting() {
				const h = new Date().getHours()
				if (h < 12) return '上午好！'
				if (h < 18) return '下午好！'
				return '晚上好！'
			},
			vipInfo() {
				return resolveVip(this.user)
			}
		},
		onLoad() {
			const sys = uni.getSystemInfoSync()
			this.statusBarHeight = sys.statusBarHeight || 20
		},
		onShow() {
			uni.hideTabBar({ fail() {} })
			this.refreshUser()
			this.checkPhoneLogin()
		},
		methods: {
			refreshUser() {
				this.user = getUser()
			},
			checkPhoneLogin() {
				if (needPhoneLoginPrompt()) {
					this.phoneLoginVisible = true
				} else {
					this.phoneLoginVisible = false
				}
			},
			onPhoneCancel() {
				this.phoneLoginVisible = false
			},
			onPhoneConfirm() {
				silentLogin().then(() => {
					this.phoneLoginVisible = false
					this.refreshUser()
					const app = getApp()
					if (app.globalData) app.globalData.authVersion = Date.now()
					uni.showToast({ title: '登录成功', icon: 'success' })
				})
			},
			ensureLogin() {
				if (isLoggedIn()) return true
				this.phoneLoginVisible = true
				return false
			},
			onProfile() {
				if (!this.ensureLogin()) return
				uni.navigateTo({ url: '/pages/mine/profile' })
			},
			onVip() {
				if (!this.ensureLogin()) return
				uni.navigateTo({ url: '/pages/mine/member' })
			},
			onMenu(item) {
				if (item.key === 'service') {
					this.stewardVisible = true
					return
				}
				if (!this.ensureLogin()) return
				if (item.key === 'points') {
					uni.navigateTo({ url: '/pages/mine/points' })
					return
				}
				if (item.key === 'coupon') {
					uni.navigateTo({ url: '/pages/mine/coupons' })
					return
				}
				if (item.key === 'address') {
					uni.navigateTo({ url: '/pages/mine/address' })
					return
				}
				if (item.key === 'order') {
					uni.navigateTo({ url: '/pages/orders/orders' })
					return
				}
				if (item.key === 'mall') {
					uni.navigateTo({ url: '/pages/mall/mall' })
					return
				}
				if (item.key === 'setting') {
					uni.navigateTo({ url: '/pages/settings/settings' })
					return
				}
				uni.showToast({ title: (item.name || '功能') + '即将开放', icon: 'none' })
			},
			closeSteward() {
				this.stewardVisible = false
			}
		}
	}
</script>

<style>
	.page {
		min-height: 100vh;
		box-sizing: border-box;
		background: #F4F4F4;
		padding-bottom: calc(168rpx + env(safe-area-inset-bottom));
		overflow-x: hidden;
	}

	.hero {
		position: relative;
		height: 280rpx;
		box-sizing: border-box;
		overflow: hidden;
	}

	.hero-bg {
		position: absolute;
		left: 0;
		top: 0;
		width: 100%;
		height: 420rpx;
	}

	.hero-space {
		height: 200rpx;
	}

	.user-card,
	.points-card,
	.menu-card {
		margin: 0 24rpx;
		background: #fff;
		border-radius: 24rpx;
		position: relative;
		z-index: 1;
	}

	.user-card {
		display: flex;
		align-items: center;
		margin-top: -80rpx;
		padding: 32rpx 24rpx;
	}

	.avatar {
		width: 120rpx;
		height: 120rpx;
		border-radius: 50%;
		background: #F3EDE6;
		margin-right: 20rpx;
		flex-shrink: 0;
		border: 6rpx solid #fff;
	}

	.user-main {
		flex: 1;
		min-width: 0;
	}

	.hello-row {
		display: flex;
		align-items: baseline;
		flex-wrap: wrap;
	}

	.hello {
		font-size: 36rpx;
		font-weight: 700;
		color: #1a1a1a;
		margin-right: 10rpx;
	}

	.name {
		font-size: 26rpx;
		color: #999;
	}

	.profile-link {
		display: flex;
		align-items: center;
		margin-top: 14rpx;
	}

	.edit {
		width: 24rpx;
		height: 24rpx;
		margin-right: 6rpx;
	}

	.profile-link text {
		font-size: 24rpx;
		color: #E23636;
	}

	.vip-badge {
		flex-shrink: 0;
		align-self: center;
		display: flex;
		flex-direction: row;
		align-items: flex-end;
		margin-left: 8rpx;
		height: 96rpx;
	}

	.vip-icon {
		display: block;
		width: 96rpx;
		height: 88rpx;
		margin-right: -48rpx;
		margin-bottom: -4rpx;
		flex-shrink: 0;
		z-index: 2;
		position: relative;
	}

	.vip-pill {
		height: 52rpx;
		padding: 0 28rpx 0 56rpx;
		border-radius: 999rpx;
		background: #d4e0f2;
		display: flex;
		align-items: center;
		justify-content: center;
		box-sizing: border-box;
	}

	.vip-level {
		font-size: 26rpx;
		font-weight: 700;
		line-height: 52rpx;
		height: 52rpx;
		letter-spacing: 0;
		white-space: nowrap;
	}

	.points-card {
		margin-top: 20rpx;
		padding: 28rpx 28rpx;
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.points-left {
		display: flex;
		align-items: center;
		font-size: 28rpx;
		color: #333;
	}

	.coin {
		width: 36rpx;
		height: 36rpx;
		margin-right: 10rpx;
	}

	.points-num {
		margin-left: 6rpx;
		color: #E23636;
		font-weight: 700;
		font-size: 32rpx;
	}

	.points-more {
		display: flex;
		align-items: center;
		font-size: 26rpx;
		color: #B0B0B0;
	}

	.menu-card {
		margin-top: 20rpx;
		padding: 8rpx 8rpx 8rpx 24rpx;
	}

	.menu-item {
		display: flex;
		align-items: center;
		padding: 34rpx 20rpx 34rpx 0;
	}

	.menu-icon {
		width: 40rpx;
		height: 40rpx;
		margin-right: 20rpx;
	}

	.menu-name {
		flex: 1;
		font-size: 30rpx;
		color: #222;
	}

	.arrow {
		width: 14rpx;
		height: 14rpx;
		border-top: 3rpx solid #D0D0D0;
		border-right: 3rpx solid #D0D0D0;
		transform: rotate(45deg);
		margin-left: 8rpx;
	}
</style>
