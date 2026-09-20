<template>
	<page-meta :page-style="'overflow:' + (stewardVisible || regionVisible ? 'hidden' : 'visible')"></page-meta>
	<view class="page">
		<view class="fixed-head" :style="{ paddingTop: statusBarHeight + 'px' }">
			<view class="nav">
				<view class="city" @tap="chooseCity">
					<image class="city-pin" src="/static/icons/city-pin.png" mode="aspectFit" />
					<text class="city-name">{{ city }}</text>
					<view class="city-arrow" />
				</view>
			</view>
			<view class="tabs">
				<view
					v-for="tab in tabs"
					:key="tab.key"
					class="tab"
					:class="{ on: tab.key === currentTab }"
					@tap="switchTab(tab.key)"
				>
					<text>{{ tab.name }}</text>
					<image
						class="tab-curve"
						src="/static/icons/tab-curve.png"
						mode="aspectFit"
					/>
				</view>
			</view>
		</view>
		<view class="head-space" :style="{ height: headHeight + 'px' }" />

		<view v-if="!list.length" class="state">暂无活动</view>
		<view v-else class="waterfall">
			<view v-for="(col, ci) in columns" :key="ci" class="col">
				<view v-for="item in col" :key="item.id" class="card" @tap="onItem(item)">
					<view class="cover-wrap">
						<image class="cover" :src="item.cover" mode="aspectFill" />
						<view v-if="showSold && item.soldText" class="sold">{{ item.soldText }}</view>
					</view>
					<text class="title">{{ item.title }}</text>
					<text v-if="item.tag" class="tag">{{ item.tag }}</text>
					<view v-if="item.tags && item.tags.length" class="chips">
						<text v-for="chip in item.tags" :key="chip" class="chip">{{ chip }}</text>
					</view>
					<view class="price-row">
						<text class="price">¥{{ item.price }}</text>
						<text v-if="item.originPrice" class="origin">¥{{ item.originPrice }}</text>
					</view>
				</view>
			</view>
		</view>
		<view v-if="list.length" class="more">没有更多了</view>

		<view class="service" @tap="openSteward">
			<image src="/static/icons/service-float.png" mode="aspectFit" />
			<text>客服</text>
		</view>
		<app-tabbar :current="1" />
		<steward-dialog :visible="stewardVisible" @close="closeSteward" />
		<region-picker
			:visible="regionVisible"
			:options="regions"
			:value="city"
			@confirm="onRegionConfirm"
			@close="closeRegion"
		/>
	</view>
</template>

<script>
	import { gatherRegions } from '../../common/regions.js'
	import { gatherTabs, gatherProducts } from '../../common/gather-data.js'
	import { api } from '../../common/api.js'

	export default {
		data() {
			return {
				statusBarHeight: 20,
				headHeight: 120,
				city: '全部',
				regions: gatherRegions,
				regionVisible: false,
				currentTab: gatherTabs[0] ? gatherTabs[0].key : 'day',
				tabs: gatherTabs,
				products: gatherProducts,
				stewardVisible: false
			}
		},
		computed: {
			list() {
				return this.products.filter((item) => item.tab === this.currentTab)
			},
			showSold() {
				const tab = this.tabs.find((item) => item.key === this.currentTab)
				return !!(tab && tab.showSold)
			},
			columns() {
				const left = []
				const right = []
				this.list.forEach((item, index) => {
					;(index % 2 === 0 ? left : right).push(item)
				})
				return [left, right]
			}
		},
		onLoad() {
			const sys = uni.getSystemInfoSync()
			this.statusBarHeight = sys.statusBarHeight || 20
			const rpx = (sys.windowWidth || 375) / 750
			this.headHeight = this.statusBarHeight + Math.round(176 * rpx)
			this.loadGather()
		},
		onShow() {
			uni.hideTabBar({ fail() {} })
			const app = getApp()
			const tab = app.globalData && app.globalData.gatherTab
			if (tab && this.tabs.some((item) => item.key === tab)) {
				this.currentTab = tab
				app.globalData.gatherTab = ''
			}
		},
		methods: {
			loadGather() {
				api
					.gather()
					.then((res) => {
						if (res.tabs && res.tabs.length) {
							this.tabs = res.tabs.map((t) => ({
								key: t.key,
								name: t.name,
								showSold: t.showSold
							}))
							if (!this.tabs.some((t) => t.key === this.currentTab)) {
								this.currentTab = this.tabs[0].key
							}
						}
						if (res.products && res.products.length) {
							this.products = res.products
						}
					})
					.catch(() => {})
			},
			switchTab(key) {
				if (this.currentTab === key) return
				this.currentTab = key
				uni.pageScrollTo({ scrollTop: 0, duration: 0 })
			},
			chooseCity() {
				this.regionVisible = true
			},
			onRegionConfirm(item) {
				if (item && item.name) {
					this.city = item.name
				}
			},
			closeRegion() {
				this.regionVisible = false
			},
			onItem(item) {
				if (item && item.detailId) {
					uni.navigateTo({ url: '/pages/nye/detail?id=' + item.detailId })
					return
				}
				if (item && item.id) {
					uni.navigateTo({ url: '/pages/gather/detail?id=' + item.id })
				}
			},
			openSteward() {
				this.stewardVisible = true
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
		background: #F5F5F5;
		padding-bottom: calc(168rpx + env(safe-area-inset-bottom));
	}

	.fixed-head {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		z-index: 100;
		background: #fff;
	}

	.nav {
		height: 88rpx;
		padding: 0 28rpx;
		display: flex;
		align-items: center;
	}

	.city {
		display: flex;
		align-items: center;
	}

	.city-pin {
		width: 48rpx;
		height: 54rpx;
		margin-right: 8rpx;
		flex-shrink: 0;
	}

	.city-name {
		font-size: 32rpx;
		font-weight: 400;
		color: #E03D47;
		line-height: 44rpx;
	}

	.city-arrow {
		width: 12rpx;
		height: 12rpx;
		margin-left: 8rpx;
		border-right: 2rpx solid #313131;
		border-bottom: 2rpx solid #313131;
		transform: rotate(45deg);
		box-sizing: border-box;
	}

	.tabs {
		display: flex;
		padding: 4rpx 8rpx 0;
	}

	.tab {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		padding-bottom: 12rpx;
	}

	.tab text {
		font-size: 30rpx;
		color: #333;
		line-height: 44rpx;
	}

	.tab.on text {
		color: #E03D47;
		font-weight: 600;
	}

	.tab-curve {
		width: 56rpx;
		height: 12rpx;
		margin-top: 6rpx;
		opacity: 0;
	}

	.tab.on .tab-curve {
		opacity: 1;
	}

	.waterfall {
		display: flex;
		align-items: flex-start;
		padding: 8rpx 16rpx 0;
	}

	.col {
		width: 50%;
		box-sizing: border-box;
		padding: 0 10rpx;
	}

	.card {
		width: 100%;
		margin-bottom: 20rpx;
		padding-bottom: 20rpx;
		background: #fff;
		border-radius: 12rpx;
		overflow: hidden;
	}

	.cover-wrap {
		position: relative;
		width: 100%;
		padding-top: 100%;
		overflow: hidden;
		background: #F3F0EC;
	}

	.cover {
		position: absolute;
		left: 0;
		top: 0;
		width: 100%;
		height: 100%;
		display: block;
	}

	.sold {
		position: absolute;
		right: 10rpx;
		top: 10rpx;
		background: rgba(0, 0, 0, 0.45);
		color: #fff;
		font-size: 20rpx;
		line-height: 36rpx;
		padding: 0 12rpx;
		border-radius: 18rpx;
	}

	.title {
		display: -webkit-box;
		-webkit-box-orient: vertical;
		-webkit-line-clamp: 2;
		overflow: hidden;
		margin: 14rpx 16rpx 0;
		font-size: 26rpx;
		line-height: 1.4;
		color: #222;
	}

	.tag {
		display: block;
		margin: 8rpx 16rpx 0;
		font-size: 22rpx;
		color: #B0B0B0;
	}

	.chips {
		display: flex;
		flex-wrap: wrap;
		margin: 8rpx 16rpx 0;
	}

	.chip {
		font-size: 20rpx;
		color: #B0B0B0;
		margin-right: 10rpx;
	}

	.price-row {
		display: flex;
		align-items: baseline;
		margin: 10rpx 16rpx 0;
	}

	.price {
		font-size: 34rpx;
		font-weight: 700;
		color: #E23636;
	}

	.origin {
		margin-left: 8rpx;
		font-size: 22rpx;
		color: #C8C8C8;
		text-decoration: line-through;
	}

	.state,
	.more {
		text-align: center;
		padding: 48rpx 0 24rpx;
		font-size: 24rpx;
		color: #C0C0C0;
	}

	.service {
		position: fixed;
		right: 0;
		top: 54%;
		width: 148rpx;
		padding: 28rpx 12rpx 24rpx 20rpx;
		background: #fff;
		border-radius: 74rpx 0 0 74rpx;
		box-shadow: -4rpx 4rpx 24rpx rgba(0, 0, 0, 0.1);
		display: flex;
		flex-direction: column;
		align-items: center;
		z-index: 30;
		box-sizing: border-box;
	}

	.service image {
		width: 64rpx;
		height: 64rpx;
	}

	.service text {
		margin-top: 8rpx;
		font-size: 26rpx;
		color: #333;
		line-height: 1.2;
	}
</style>
