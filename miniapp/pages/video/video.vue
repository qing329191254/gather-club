<template>
	<app-loading />
	<view class="page">
		<view class="header">
			<view class="header-avatar-wrap">
				<image v-if="profile.avatar" class="header-avatar" :src="profile.avatar" mode="aspectFill" />
				<view v-if="living" class="live-badge">直播中</view>
			</view>
			<text class="header-name">{{ profile.name }}</text>
		</view>

		<view class="channel-card">
			<view class="cover-wrap">
				<image v-if="profile.cover" class="cover" :src="profile.cover" mode="aspectFill" />
			</view>
			<view class="channel">
				<view class="channel-row">
					<image v-if="profile.avatar" class="channel-avatar" :src="profile.avatar" mode="aspectFill" />
					<text class="channel-name">{{ profile.name }}</text>
					<view class="follow" :class="{ 'tap-busy': isTapBusy('follow') }" @tap.stop="onFollow">关注视频号</view>
				</view>
				<text class="intro">{{ profile.intro }}</text>
			</view>
		</view>

		<!-- 直播中 -->
		<view v-if="living" class="live-onair" :class="{ 'tap-busy': isTapBusy('watch-' + living.id) }" @tap="onWatch(living)">
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
					<image v-if="living.avatar || profile.avatar" class="live-avatar" :src="living.avatar || profile.avatar" mode="aspectFill" />
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
		<view v-for="item in lives" :key="item.id" class="live" :class="{ 'tap-busy': isTapBusy('reserve-' + item.id) }" @tap="onReserve(item)">
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
				<image v-if="item.avatar || profile.avatar" class="live-avatar" :src="item.avatar || profile.avatar" mode="aspectFill" />
				<view class="live-title">
					<text>{{ item.line1 }}</text>
					<text>{{ item.line2 }}</text>
				</view>
				<view class="reserve" :class="{ 'reserve--done': item.reserved }">{{ item.reserved ? '已预约' : '预约直播' }}</view>
			</view>
		</view>

		<app-tabbar :current="2" />
	</view>
</template>

<script>
	import { api } from '../../common/api.js'

	export default {
		data() {
			return {
				profile: {
					name: '天天俱乐部',
					avatar: '',
					cover: '',
					intro: '天天俱乐部！天天都有局！关注直播间，给您带来更多超高性价比的聚会餐，酒店直播！',
					finderUserName: ''
				},
				living: null,
				lives: []
			}
		},
		onShow() {
			uni.hideTabBar({ fail() {} })
			this.loadList()
		},
		methods: {
			channelsErrorText(err, fallback) {
				const fb = fallback || '视频号操作失败'
				if (!err) return fb
				const code = Number(
					(err && (err.errCode != null ? err.errCode : err.errno != null ? err.errno : err.err_code)) ||
						0
				)
				const byCode = {
					100008: '视频号需认证或与小程序主体不一致',
					40097: '视频号参数异常',
					1416100: '视频号 ID 无效',
					1416104: '暂无直播或预告'
				}
				if (byCode[code]) return byCode[code]

				const raw = String((err && (err.errMsg || err.message)) || '').trim()
				if (!raw) return fb
				const lower = raw.toLowerCase()
				if (lower.indexOf('unsupported') >= 0) return '请在微信真机中打开'
				if (lower.indexOf('not same contractor') >= 0 || lower.indexOf('100008') >= 0) {
					return '视频号需认证或与小程序主体不一致'
				}
				if (lower.indexOf('cancel') >= 0) return '已取消'
				if (lower.indexOf('auth deny') >= 0 || lower.indexOf('authorize') >= 0) {
					return '未获得视频号授权'
				}
				if (lower.indexOf('invalid') >= 0 && lower.indexOf('finder') >= 0) {
					return '视频号 ID 无效'
				}
				if (lower.indexOf('fail') >= 0 && /[a-z]/i.test(raw) && !/[\u4e00-\u9fff]/.test(raw)) {
					return fb
				}
				// 已是中文或简短可读文案时直接展示
				if (/[\u4e00-\u9fff]/.test(raw)) {
					return raw.replace(/^[^:]+:\s*/i, '').slice(0, 40) || fb
				}
				return fb
			},
			async loadList() {
				try {
					const res = await api.videoHome()
					if (res && res.profile) {
						this.profile = Object.assign({}, this.profile, res.profile)
					}
					this.living = null
					this.lives = []
					const fromProfile = Number(res && res.profile && res.profile.defaultReservePoints)
					const defaultPoints =
						Number.isFinite(fromProfile) && fromProfile >= 0 ? fromProfile : 10
					const finder = (this.profile && this.profile.finderUserName) || ''
					if (!finder) {
						return
					}
					try {
						await this.syncFromChannels(
							finder,
							defaultPoints,
							(res && res.reservedNoticeIds) || []
						)
					} catch (e) {
						this.living = null
						this.lives = []
						const msg = this.channelsErrorText(e, '视频号直播同步失败')
						console.warn('[video] channels sync failed', finder, e)
						if (String((e && (e.errMsg || e.message)) || '').indexOf('unsupported') >= 0) {
							console.warn('[video] getChannelsLive* 仅真机可用')
						} else {
							uni.showToast({
								title: msg,
								icon: 'none',
								duration: 3000
							})
						}
					}
				} catch (e) {
					this.living = null
					this.lives = []
					uni.showToast({ title: '直播列表加载失败', icon: 'none' })
				}
			},
			wxCall(name, opts) {
				return new Promise((resolve, reject) => {
					const fn = typeof wx !== 'undefined' && wx[name]
					if (typeof fn !== 'function') {
						reject(new Error('unsupported'))
						return
					}
					fn(
						Object.assign({}, opts || {}, {
							success(res) {
								resolve(res || {})
							},
							fail(err) {
								reject(err || new Error('fail'))
							}
						})
					)
				})
			},
			splitLiveTitle(raw) {
				const text = String(raw || '').trim()
				if (!text) {
					return { line1: '视频号直播', line2: '' }
				}
				const parts = text.split(/\s*[+＋／/|\n]\s*/).filter(Boolean)
				if (parts.length >= 2) {
					return { line1: parts[0], line2: parts.slice(1).join('+') }
				}
				return { line1: text, line2: '' }
			},
			formatLiveTime(raw) {
				if (raw === null || raw === undefined || raw === '') return ''
				const n = Number(raw)
				let d
				if (Number.isFinite(n) && n > 0) {
					d = new Date(n > 1e12 ? n : n * 1000)
				} else {
					d = new Date(raw)
				}
				if (isNaN(d.getTime())) return String(raw)
				const m = d.getMonth() + 1
				const day = d.getDate()
				const hh = String(d.getHours()).padStart(2, '0')
				const mm = String(d.getMinutes()).padStart(2, '0')
				return m + '月' + day + ' ' + hh + ':' + mm
			},
			async syncFromChannels(finder, defaultPoints, reservedNoticeIds) {
				const reservedNotice = {}
				;(reservedNoticeIds || []).forEach((id) => {
					if (id) reservedNotice[String(id)] = true
				})

				let liveInfo = null
				let noticeInfo = null
				let liveErr = null
				let noticeErr = null
				try {
					liveInfo = await this.wxCall('getChannelsLiveInfo', { finderUserName: finder })
				} catch (e) {
					liveErr = e
				}
				try {
					noticeInfo = await this.wxCall('getChannelsLiveNoticeInfo', {
						finderUserName: finder
					})
				} catch (e) {
					noticeErr = e
				}

				console.log('[video] channels result', {
					finder,
					liveInfo,
					noticeInfo,
					liveErr,
					noticeErr
				})

				if (!liveInfo && !noticeInfo) {
					const err = noticeErr || liveErr || new Error('channels unavailable')
					throw err
				}

				if (liveInfo && Number(liveInfo.status) === 2) {
					const titles = this.splitLiveTitle(
						liveInfo.description || liveInfo.nickname || this.profile.name || ''
					)
					this.living = {
						id: 'living',
						line1: titles.line1,
						line2: titles.line2,
						avatar: liveInfo.headUrl || this.profile.avatar || '',
						feedId: liveInfo.feedId || '',
						nonceId: liveInfo.nonceId || ''
					}
				} else {
					this.living = null
				}

				const notices = []
				if (noticeInfo && noticeInfo.noticeId) {
					notices.push(noticeInfo)
				}
				const others = (noticeInfo && noticeInfo.otherInfos) || []
				if (Array.isArray(others)) {
					others.forEach((row) => {
						if (row && row.noticeId) notices.push(row)
					})
				}

				const n = Number(defaultPoints)
				const points = Number.isFinite(n) && n >= 0 ? n : 10
				this.lives = notices.map((row) => {
					const nid = String(row.noticeId)
					const titles = this.splitLiveTitle(
						row.description || row.nickname || this.profile.name || '视频号直播'
					)
					return {
						id: nid,
						noticeId: nid,
						time: this.formatLiveTime(row.startTime),
						line1: titles.line1,
						line2: titles.line2,
						points,
						avatar: row.headUrl || this.profile.avatar || '',
						reserved: !!reservedNotice[nid]
					}
				})
			},
			async onFollow() {
				return this.tapGuard('follow', async () => {
				try {
					const res = await api.videoFollow()
					const finder = (res && res.finderUserName) || this.profile.finderUserName || ''
					this.profile.finderUserName = finder
					if (!finder) {
						uni.showToast({ title: '视频号审核中', icon: 'none' })
						return
					}
					this.openChannel('openChannelsUserProfile')
				} catch (e) {
					uni.showToast({
						title: this.channelsErrorText(e, '打开失败'),
						icon: 'none'
					})
				}
				})
			},
			async onWatch(item) {
				const key = 'watch-' + ((item && item.id) || 'live')
				return this.tapGuard(key, async () => {
				try {
					const res = await api.videoWatch(item && item.id)
					const finder = (res && res.finderUserName) || this.profile.finderUserName || ''
					this.profile.finderUserName = finder
					if (!finder) {
						uni.showToast({ title: '视频号审核中，直播稍后开放', icon: 'none' })
						return
					}
					const extra = {}
					if (item && item.feedId) extra.feedId = item.feedId
					if (item && item.nonceId) extra.nonceId = item.nonceId
					this.openChannel('openChannelsLive', extra)
				} catch (e) {
					uni.showToast({
						title: this.channelsErrorText(e, '打开失败'),
						icon: 'none'
					})
				}
				})
			},
			async onReserve(item) {
				if (!item || !item.noticeId) return
				return this.tapGuard('reserve-' + item.noticeId, async () => {
				try {
					const finder = this.profile.finderUserName || ''
					const noticeId = item.noticeId
					if (finder) {
						try {
							await this.openChannelPromise('reserveChannelsLive', { noticeId })
						} catch (e) {
							uni.showToast({
								title: this.channelsErrorText(e, '打开预约失败'),
								icon: 'none'
							})
							return
						}
					}
					const res = await api.videoReserve({
						noticeId,
						time: item.time || '',
						line1: item.line1 || '',
						line2: item.line2 || '',
						points: item.points || 10,
						avatar: item.avatar || ''
					})
					const data = (res && res.data) || {}
					item.reserved = true
					const gained = data.points || 0
					const nextFinder = data.finderUserName || finder || ''
					this.profile.finderUserName = nextFinder
					if (gained) {
						uni.showToast({ title: '预约成功 +' + gained + '积分', icon: 'none' })
					} else {
						uni.showToast({ title: '已预约', icon: 'none' })
					}
				} catch (e) {
					uni.showToast({
						title: this.channelsErrorText(e, '预约失败'),
						icon: 'none'
					})
				}
				})
			},
			openChannelPromise(name, extra) {
				return new Promise((resolve, reject) => {
					const finder = this.profile.finderUserName || ''
					if (!finder) {
						reject(new Error('视频号未配置'))
						return
					}
					const fn = (typeof wx !== 'undefined' && wx[name]) || uni[name]
					if (typeof fn !== 'function') {
						reject(new Error('请在微信中打开'))
						return
					}
					const self = this
					fn(
						Object.assign({ finderUserName: finder }, extra || {}, {
							success(res) {
								resolve(res || {})
							},
							fail(err) {
								const e = err || {}
								reject({
									errMsg: e.errMsg || '',
									errCode: e.errCode != null ? e.errCode : e.errno != null ? e.errno : e.err_code,
									message: self.channelsErrorText(e, '打开视频号失败')
								})
							}
						})
					)
				})
			},
			openChannel(name, extra) {
				const finder = this.profile.finderUserName || ''
				if (!finder) return
				const fn = (typeof wx !== 'undefined' && wx[name]) || uni[name]
				if (typeof fn !== 'function') {
					uni.showToast({ title: '请在微信中打开', icon: 'none' })
					return
				}
				const self = this
				fn(Object.assign({ finderUserName: finder }, extra || {}, {
					fail(err) {
						uni.showToast({
							title: self.channelsErrorText(err, '打开视频号失败'),
							icon: 'none'
						})
					}
				}))
			}
		}
	}
</script>

<style>
	page {
		height: 100%;
		background: #FDECEC;
	}

	.page {
		box-sizing: border-box;
		min-height: 100%;
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

	.reserve--done {
		background: #c8c8c8;
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
		overflow: visible;
	}

	.watch-heart text {
		font-size: 18rpx;
		color: #fff;
		line-height: 1;
		transform: scaleX(1.22);
	}
</style>
