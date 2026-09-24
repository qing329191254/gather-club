<template>
	<page-meta :page-style="'overflow:visible'"></page-meta>
	<app-loading />
	<view class="page">
		<view class="navbar" :style="navBarStyle">
			<view class="navbar-inner" :style="{ height: navBarHeight + 'px' }">
				<view class="back" @tap="goBack">
					<view class="back-arrow" />
				</view>
				<text class="nav-title">会员中心</text>
			</view>
		</view>

		<scroll-view class="body" scroll-y :style="{ paddingTop: statusBarHeight + navBarHeight + 'px' }">
			<view class="poster">
				<view class="curtain" />
				<image v-if="cfg.heroImage" class="hero-img" :src="cfg.heroImage" mode="widthFix" />
				<view class="crest">♛</view>
				<text class="main-title">{{ cfg.title || '会员权益' }}</text>
				<view class="price-ribbon">
					<text class="price-ribbon-text">{{ cfg.priceLabel || priceText }}</text>
				</view>

				<view v-if="isMember" class="member-status">
					<text>您已是会员</text>
					<text v-if="expireAt" class="expire">有效期至 {{ expireAt }}</text>
				</view>

				<text class="subtitle">{{ cfg.subtitle || '加入后享受专属权益' }}</text>

				<view class="benefit-list">
					<view v-for="(b, i) in cfg.benefits" :key="i" class="benefit-row">
						<text class="star">★</text>
						<view class="benefit-text">
							<text class="b-title">{{ b.title }}</text>
							<text v-if="b.desc" class="b-desc">{{ b.desc }}</text>
						</view>
					</view>
				</view>

				<view v-if="cfg.reminders && cfg.reminders.length" class="remind">
					<text class="remind-title">温馨提示：</text>
					<text v-for="(t, i) in cfg.reminders" :key="i" class="remind-line">{{ i + 1 }}、{{ t }}</text>
				</view>

				<view class="rules-link" @tap="onRules">查看会员章程 ›</view>
			</view>
			<view class="safe-bottom" />
		</scroll-view>

		<view class="pay-bar">
			<view class="pay-info">
				<text class="pay-price">¥{{ displayPrice }}</text>
				<text class="pay-tip">{{ isMember ? '续费延长有效期' : '开通即享会员权益' }}</text>
			</view>
			<view
				class="pay-btn"
				:class="{ busy: paying || isTapBusy('pay') }"
				@tap="onPay"
			>
				{{ isMember ? '立即续费' : '立即支付' }}
			</view>
		</view>
	</view>
</template>

<script>
	import { api } from '../../common/api.js'
	import { settlePay } from '../../common/api.js'
	import { getUser, isLoggedIn, silentLogin, saveLogin, getOpenid } from '../../common/auth.js'
	import { withLoading } from '../../common/loading.js'

	export default {
		data() {
			return {
				statusBarHeight: 20,
				navBarHeight: 44,
				paying: false,
				cfg: {
					title: '',
					subtitle: '',
					priceLabel: '',
					price: 199,
					durationDays: 365,
					discountRate: 0.9,
					benefits: [],
					reminders: [],
					heroImage: ''
				},
				user: getUser()
			}
		},
		computed: {
			navBarStyle() {
				return { paddingTop: this.statusBarHeight + 'px' }
			},
			displayPrice() {
				const n = Number(this.cfg.price || 0)
				return n === Math.floor(n) ? String(Math.floor(n)) : n.toFixed(2)
			},
			priceText() {
				return `会员${this.displayPrice}元/年`
			},
			isMember() {
				return !!(this.user && this.user.isMember)
			},
			expireAt() {
				return (this.user && this.user.memberExpireAt) || ''
			}
		},
		onLoad() {
			const sys = uni.getSystemInfoSync()
			this.statusBarHeight = sys.statusBarHeight || 20
			this.navBarHeight = 44
			this.loadConfig()
			this.refreshUser()
		},
		onShow() {
			this.refreshUser()
		},
		methods: {
			goBack() {
				uni.navigateBack({ fail: () => uni.switchTab({ url: '/pages/mine/mine' }) })
			},
			onRules() {
				uni.navigateTo({ url: '/pages/mine/member-rules' })
			},
			async loadConfig() {
				try {
					const cfg = await api.memberConfig()
					if (cfg && typeof cfg === 'object') {
						this.cfg = Object.assign({}, this.cfg, cfg)
					}
				} catch (e) {}
			},
			async refreshUser() {
				this.user = getUser()
				if (!isLoggedIn()) return
				try {
					await silentLogin()
					const profile = await api.profile()
					if (profile) {
						const next = Object.assign({}, this.user, profile, {
							isMember: !!profile.isMember,
							memberExpireAt: profile.memberExpireAt || '',
							vip: profile.vip || (profile.isMember ? '会员' : '未开通')
						})
						saveLogin(next, getOpenid())
						this.user = next
					}
				} catch (e) {}
			},
			async onPay() {
				if (!this.holdTap('pay')) return
				if (!isLoggedIn()) {
					uni.showToast({ title: '请先登录', icon: 'none' })
					this.releaseTap('pay')
					return
				}
				if (this.paying) {
					this.releaseTap('pay')
					return
				}
				this.paying = true
				try {
					await withLoading(async () => {
						const order = await api.createOrder({
							type: 'membership',
							title: this.cfg.title || '会员开通',
							quantity: 1
						})
						const payRes = await api.payOrder(order.id)
						await settlePay(payRes)
						uni.showToast({ title: '开通成功', icon: 'success' })
						await this.refreshUser()
					})
				} catch (e) {
					const msg = (e && e.message) || '支付失败'
					if (!/cancel|取消/i.test(msg)) {
						uni.showToast({ title: msg, icon: 'none' })
					}
				} finally {
					this.paying = false
					this.releaseTap('pay')
				}
			}
		}
	}
</script>

<style scoped>
	.page {
		min-height: 100vh;
		background: #f7efe3;
		display: flex;
		flex-direction: column;
		box-sizing: border-box;
	}

	.navbar {
		position: fixed;
		left: 0;
		right: 0;
		top: 0;
		z-index: 20;
		background: linear-gradient(180deg, #8b1e1e 0%, #c0392b 100%);
	}

	.navbar-inner {
		display: flex;
		align-items: center;
		justify-content: center;
		position: relative;
	}

	.back {
		position: absolute;
		left: 16rpx;
		width: 64rpx;
		height: 64rpx;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.back-arrow {
		width: 18rpx;
		height: 18rpx;
		border-left: 4rpx solid #fff;
		border-bottom: 4rpx solid #fff;
		transform: rotate(45deg);
		margin-left: 8rpx;
	}

	.nav-title {
		color: #fff;
		font-size: 34rpx;
		font-weight: 600;
	}

	.body {
		flex: 1;
		height: 0;
		box-sizing: border-box;
	}

	.poster {
		margin: 24rpx 28rpx 0;
		padding: 48rpx 36rpx 56rpx;
		background: linear-gradient(180deg, #fff8ee 0%, #f3e6d2 55%, #efe0c8 100%);
		border-radius: 24rpx;
		border: 2rpx solid rgba(176, 120, 48, 0.28);
		position: relative;
		overflow: hidden;
		box-shadow: 0 16rpx 40rpx rgba(120, 40, 20, 0.12);
	}

	.curtain {
		position: absolute;
		left: 0;
		right: 0;
		top: 0;
		height: 120rpx;
		background: radial-gradient(ellipse at 50% -20%, rgba(180, 36, 36, 0.55) 0%, transparent 70%);
		pointer-events: none;
	}

	.hero-img {
		width: 100%;
		border-radius: 16rpx;
		margin-bottom: 24rpx;
	}

	.crest {
		text-align: center;
		font-size: 56rpx;
		color: #c9a227;
		line-height: 1.2;
		margin-bottom: 12rpx;
	}

	.main-title {
		display: block;
		text-align: center;
		font-size: 44rpx;
		font-weight: 800;
		color: #b8860b;
		letter-spacing: 2rpx;
		line-height: 1.35;
	}

	.price-ribbon {
		margin: 28rpx auto 0;
		padding: 16rpx 48rpx;
		background: linear-gradient(90deg, #d4a84b 0%, #c9a227 45%, #e0c068 100%);
		border-radius: 8rpx;
		width: fit-content;
		max-width: 90%;
		box-shadow: 0 6rpx 16rpx rgba(160, 100, 20, 0.28);
	}

	.price-ribbon-text {
		color: #fff;
		font-size: 30rpx;
		font-weight: 700;
		letter-spacing: 2rpx;
	}

	.member-status {
		margin-top: 28rpx;
		padding: 16rpx 20rpx;
		background: rgba(196, 92, 38, 0.1);
		border-radius: 12rpx;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 6rpx;
		color: #8b3a12;
		font-size: 26rpx;
		font-weight: 600;
	}

	.expire {
		font-size: 22rpx;
		font-weight: 500;
		color: rgba(120, 60, 20, 0.75);
	}

	.subtitle {
		display: block;
		margin-top: 36rpx;
		text-align: center;
		font-size: 28rpx;
		font-weight: 600;
		color: #3a2a1a;
	}

	.benefit-list {
		margin-top: 28rpx;
	}

	.benefit-row {
		display: flex;
		align-items: flex-start;
		margin-bottom: 22rpx;
	}

	.star {
		color: #c0392b;
		font-size: 28rpx;
		margin-right: 14rpx;
		line-height: 1.4;
		flex-shrink: 0;
	}

	.benefit-text {
		flex: 1;
		min-width: 0;
		display: flex;
		flex-direction: column;
	}

	.b-title {
		font-size: 28rpx;
		font-weight: 600;
		color: #5c1a1a;
		line-height: 1.55;
	}

	.b-desc {
		margin-top: 4rpx;
		font-size: 22rpx;
		color: rgba(80, 40, 20, 0.65);
		line-height: 1.4;
	}

	.remind {
		margin-top: 36rpx;
		padding-top: 24rpx;
		border-top: 1rpx dashed rgba(160, 100, 40, 0.35);
	}

	.remind-title {
		display: block;
		font-size: 26rpx;
		font-weight: 700;
		color: #b8860b;
		margin-bottom: 12rpx;
	}

	.remind-line {
		display: block;
		font-size: 22rpx;
		color: rgba(80, 50, 30, 0.72);
		line-height: 1.55;
		margin-bottom: 8rpx;
	}

	.rules-link {
		margin-top: 28rpx;
		text-align: center;
		font-size: 24rpx;
		color: rgba(120, 70, 30, 0.75);
	}

	.safe-bottom {
		height: calc(160rpx + env(safe-area-inset-bottom));
	}

	.pay-bar {
		position: fixed;
		left: 0;
		right: 0;
		bottom: 0;
		z-index: 30;
		padding: 16rpx 28rpx calc(16rpx + env(safe-area-inset-bottom));
		background: rgba(255, 250, 242, 0.96);
		border-top: 1rpx solid rgba(180, 120, 60, 0.22);
		display: flex;
		align-items: center;
		gap: 20rpx;
		box-sizing: border-box;
	}

	.pay-info {
		flex: 1;
		min-width: 0;
		display: flex;
		flex-direction: column;
	}

	.pay-price {
		font-size: 40rpx;
		font-weight: 800;
		color: #c0392b;
		line-height: 1.2;
	}

	.pay-tip {
		margin-top: 4rpx;
		font-size: 22rpx;
		color: rgba(80, 50, 30, 0.65);
	}

	.pay-btn {
		flex-shrink: 0;
		min-width: 240rpx;
		height: 88rpx;
		padding: 0 36rpx;
		border-radius: 44rpx;
		background: linear-gradient(90deg, #d4a84b 0%, #c0392b 100%);
		color: #fff;
		font-size: 30rpx;
		font-weight: 700;
		display: flex;
		align-items: center;
		justify-content: center;
		box-shadow: 0 10rpx 24rpx rgba(160, 50, 30, 0.28);
	}

	.pay-btn.busy {
		opacity: 0.65;
	}
</style>
