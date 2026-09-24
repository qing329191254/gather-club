<template>
	<page-meta :page-style="'overflow:' + (stewardVisible || phoneLoginVisible ? 'hidden' : 'visible')"></page-meta>
	<app-loading />
	<view class="page">
		<view class="head" :style="{ paddingTop: headPadTop + 'px' }">
			<view class="head-inner">
				<view class="user-row" @tap="onProfile">
					<image class="avatar" :src="user.avatar || '/static/icons/avatar-default.png'" mode="aspectFill" />
					<view class="user-main">
						<view class="name-row">
							<text class="name">{{ user.nickname || '微信用户' }}</text>
							<view class="vip-chip" :style="vipChipStyle" @tap.stop="onVip">
								<text class="vip-chip-text" :style="vipChipTextStyle">{{ vipInfo.label }}</text>
							</view>
						</view>
						<text class="hello">{{ greeting }} · 完善资料 ›</text>
					</view>
				</view>
				<view class="points-strip" @tap="onMenu({ key: 'points', name: '积分明细' })">
					<view class="points-left">
						<image class="coin" src="/static/icons/coin.png" mode="aspectFit" />
						<text>当前积分</text>
						<text class="points-num">{{ user.points }}</text>
					</view>
					<text class="points-more">明细 ›</text>
				</view>
			</view>
		</view>

		<view class="body">
			<view class="grid-card">
				<view class="section-label">我的服务</view>
				<view class="grid">
					<view v-for="item in menus" :key="item.key" class="grid-item" @tap="onMenu(item)">
						<image class="grid-icon" :src="item.icon" mode="aspectFit" />
						<text class="grid-name">{{ item.name }}</text>
					</view>
				</view>
			</view>

			<view class="quick-card">
				<view class="section-label">快捷入口</view>
				<view class="quick-list">
					<view class="quick-item" @tap="goCheckin">
						<view class="quick-copy">
							<text class="quick-title">每日签到</text>
							<text class="quick-desc">打卡领积分</text>
						</view>
						<text class="quick-go">去签到</text>
					</view>
					<view class="quick-item" @tap="goGather">
						<view class="quick-copy">
							<text class="quick-title">去聚餐</text>
							<text class="quick-desc">看看最近有什么局</text>
						</view>
						<text class="quick-go">去看看</text>
					</view>
					<view class="quick-item" @tap="onVip">
						<view class="quick-copy">
							<text class="quick-title">会员中心</text>
							<text class="quick-desc">开通会员与权益</text>
						</view>
						<text class="quick-go">去查看</text>
					</view>
				</view>
			</view>
		</view>

		<app-tabbar :current="3" />
		<steward-dialog
			:visible="stewardVisible"
			:title="stewardProps.title"
			:tip="stewardProps.tip"
			:qr-src="stewardProps.qrSrc"
			:phone="stewardProps.phone"
			@close="closeSteward"
		/>
		<phone-login-dialog
			ref="phoneLogin"
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
		needPrivacyPrompt,
		refreshProfile,
		bindPhoneFromDetail
	} from '../../common/auth.js'
	import { resolveVip, setVipLevelsFromServer } from '../../common/vip-levels.js'
	import { stewardPropsFromSite } from '../../common/site.js'
	import { api } from '../../common/api.js'

	export default {
		data() {
			return {
				statusBarHeight: 20,
				headPadTop: 48,
				stewardVisible: false,
				phoneLoginVisible: false,
				user: getUser(),
				stewardProps: stewardPropsFromSite(),
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
				if (h < 12) return '上午好'
				if (h < 18) return '下午好'
				return '晚上好'
			},
			vipInfo() {
				return resolveVip(this.user)
			},
			vipChipStyle() {
				const t = (this.vipInfo && this.vipInfo.theme) || {}
				const style = {
					background: t.pill || 'rgba(255, 255, 255, 0.22)',
					borderColor: t.border && t.border !== 'transparent' ? t.border : 'transparent'
				}
				if (!t.pill) {
					style.borderColor = 'rgba(255, 255, 255, 0.55)'
				}
				return style
			},
			vipChipTextStyle() {
				const t = (this.vipInfo && this.vipInfo.theme) || {}
				return { color: t.text || '#ffffff' }
			}
		},
		onLoad() {
			const sys = uni.getSystemInfoSync()
			this.statusBarHeight = sys.statusBarHeight || 20
			this.headPadTop = this.statusBarHeight + 44
			try {
				const menu = uni.getMenuButtonBoundingClientRect()
				if (menu && menu.bottom) {
					// 胶囊下方再留一点间距，整块头部更紧凑
					this.headPadTop = Math.ceil(menu.bottom + 12)
				}
			} catch (e) {}
		},
		onShow() {
			uni.hideTabBar({ fail() {} })
			this.refreshUser()
			this.checkPhoneLogin()
		},
		methods: {
			refreshUser() {
				this.stewardProps = stewardPropsFromSite()
				this.user = getUser()
				api
					.memberConfig()
					.then((cfg) => {
						if (cfg && Array.isArray(cfg.levels)) setVipLevelsFromServer(cfg.levels)
						this.user = Object.assign({}, this.user)
					})
					.catch(() => {})
				if (isLoggedIn()) {
					refreshProfile().then((user) => {
						this.user = user
					})
				}
			},
			checkPhoneLogin() {
				if (needPrivacyPrompt()) {
					this.phoneLoginVisible = false
					return
				}
				if (needPhoneLoginPrompt()) {
					this.phoneLoginVisible = true
				} else {
					this.phoneLoginVisible = false
				}
			},
			onPhoneCancel() {
				this.phoneLoginVisible = false
			},
			onPhoneConfirm(detail) {
				bindPhoneFromDetail(detail)
					.then(() => {
						this.phoneLoginVisible = false
						this.refreshUser()
						const app = getApp()
						if (app.globalData) app.globalData.authVersion = Date.now()
						uni.showToast({ title: '登录成功', icon: 'success' })
					})
					.catch((e) => {
						uni.showToast({ title: (e && e.message) || '登录失败', icon: 'none' })
					})
					.finally(() => {
						const dlg = this.$refs.phoneLogin
						if (dlg && dlg.resetBusy) dlg.resetBusy()
					})
			},
			ensureLogin() {
				if (needPrivacyPrompt()) {
					uni.reLaunch({ url: '/pages/index/index' })
					return false
				}
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
			goCheckin() {
				if (!this.ensureLogin()) return
				uni.navigateTo({ url: '/pages/checkin/checkin' })
			},
			goGather() {
				uni.switchTab({ url: '/pages/gather/gather' })
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
		background: #F1EEE8;
		padding-bottom: calc(148rpx + env(safe-area-inset-bottom));
		overflow-x: hidden;
	}

	.head {
		background: linear-gradient(165deg, #A83632 0%, #C6453C 70%, #D25A48 100%);
		padding-bottom: 0;
		box-sizing: border-box;
	}

	.head-inner {
		padding: 4rpx 28rpx 0;
	}

	.user-row {
		display: flex;
		align-items: center;
		min-height: 104rpx;
	}

	.avatar {
		width: 96rpx;
		height: 96rpx;
		border-radius: 16rpx;
		background: rgba(255, 255, 255, 0.2);
		margin-right: 20rpx;
		flex-shrink: 0;
		border: 4rpx solid rgba(255, 255, 255, 0.55);
		box-sizing: border-box;
	}

	.user-main {
		flex: 1;
		min-width: 0;
		display: flex;
		flex-direction: column;
		justify-content: center;
	}

	.name-row {
		display: flex;
		align-items: center;
		flex-wrap: nowrap;
		min-width: 0;
	}

	.name {
		font-size: 34rpx;
		font-weight: 700;
		color: #fff;
		line-height: 1.25;
		max-width: 360rpx;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.vip-chip {
		flex-shrink: 0;
		margin-left: 14rpx;
		height: 36rpx;
		padding: 0 14rpx;
		border-radius: 8rpx;
		background: rgba(255, 255, 255, 0.22);
		border: 1rpx solid transparent;
		display: flex;
		align-items: center;
		justify-content: center;
		box-sizing: border-box;
	}

	.vip-chip-text {
		font-size: 20rpx;
		font-weight: 700;
		line-height: 1;
		color: #ffffff;
	}

	.hello {
		margin-top: 10rpx;
		font-size: 22rpx;
		color: rgba(255, 255, 255, 0.82);
		line-height: 1.3;
	}

	.points-strip {
		margin-top: 28rpx;
		margin-bottom: -28rpx;
		padding: 24rpx 24rpx;
		background: #fff;
		border-radius: 12rpx;
		display: flex;
		align-items: center;
		justify-content: space-between;
		border: 1rpx solid #E8E2DA;
		box-sizing: border-box;
		position: relative;
		z-index: 2;
		box-shadow: 0 8rpx 20rpx rgba(44, 42, 39, 0.06);
	}

	.points-left {
		display: flex;
		align-items: center;
		font-size: 26rpx;
		color: #6B635C;
	}

	.coin {
		width: 32rpx;
		height: 32rpx;
		margin-right: 10rpx;
	}

	.points-num {
		margin-left: 10rpx;
		color: #C6453C;
		font-weight: 700;
		font-size: 34rpx;
	}

	.points-more {
		font-size: 24rpx;
		color: #9A9288;
	}

	.body {
		margin-top: 44rpx;
		padding: 0 24rpx;
		position: relative;
		z-index: 1;
	}

	.grid-card,
	.quick-card {
		margin-top: 20rpx;
		background: #fff;
		border-radius: 12rpx;
		border: 1rpx solid #E8E2DA;
		padding: 24rpx 20rpx 12rpx;
		box-sizing: border-box;
	}

	.section-label {
		display: block;
		font-size: 28rpx;
		font-weight: 700;
		color: #2C2A27;
		margin-bottom: 8rpx;
		padding-left: 4rpx;
	}

	.grid {
		display: flex;
		flex-wrap: wrap;
	}

	.grid-item {
		width: 33.33%;
		padding: 28rpx 8rpx 24rpx;
		display: flex;
		flex-direction: column;
		align-items: center;
		box-sizing: border-box;
	}

	.grid-icon {
		width: 56rpx;
		height: 56rpx;
	}

	.grid-name {
		margin-top: 14rpx;
		font-size: 24rpx;
		color: #2C2A27;
		line-height: 1.3;
		text-align: center;
	}

	.quick-card {
		padding-bottom: 8rpx;
	}

	.quick-list {
		margin-top: 4rpx;
	}

	.quick-item {
		display: flex;
		align-items: center;
		padding: 28rpx 8rpx;
		border-top: 1rpx solid #F0EBE4;
	}

	.quick-item:first-child {
		border-top: none;
	}

	.quick-copy {
		flex: 1;
		min-width: 0;
		display: flex;
		flex-direction: column;
	}

	.quick-title {
		font-size: 28rpx;
		font-weight: 600;
		color: #2C2A27;
		line-height: 1.3;
	}

	.quick-desc {
		margin-top: 6rpx;
		font-size: 22rpx;
		color: #9A9288;
		line-height: 1.3;
	}

	.quick-go {
		flex-shrink: 0;
		padding: 0 20rpx;
		height: 52rpx;
		line-height: 52rpx;
		font-size: 22rpx;
		color: #fff;
		background: #C6453C;
		border-radius: 8rpx;
		font-weight: 600;
	}
</style>
