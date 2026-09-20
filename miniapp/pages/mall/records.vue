<template>
	<view class="page">
		<view v-if="!list.length" class="empty">
			<image class="empty-img" src="/static/mall/empty-exchange.png" mode="aspectFit" />
			<text class="empty-text">暂无兑换内容</text>
		</view>
		<view v-else class="list">
			<view v-for="item in list" :key="item.id" class="item">
				<image class="thumb" :src="item.cover" mode="aspectFill" />
				<view class="info">
					<text class="name">{{ item.name }}</text>
					<text class="time">{{ item.time }}</text>
				</view>
				<text class="cost">-{{ item.cost }}</text>
			</view>
		</view>
		<view v-if="list.length" class="end">{{ loading ? '加载中…' : (hasMore ? '上拉加载更多' : '没有更多了') }}</view>
	</view>
</template>

<script>
	import { api } from '../../common/api.js'
	import { isLoggedIn, silentLogin } from '../../common/auth.js'

	export default {
		data() {
			return {
				list: [],
				page: 1,
				pageSize: 20,
				hasMore: true,
				loading: false
			}
		},
		onShow() {
			this.reloadRecords()
		},
		onReachBottom() {
			this.loadMore()
		},
		methods: {
			async reloadRecords() {
				if (!isLoggedIn()) await silentLogin()
				this.page = 1
				this.hasMore = true
				this.list = []
				await this.loadMore(true)
			},
			async loadMore(reset) {
				if (this.loading || (!this.hasMore && !reset)) return
				this.loading = true
				try {
					const res = await api.mallRecords({ page: this.page, page_size: this.pageSize })
					const rows = res.list || []
					this.list = reset || this.page === 1 ? rows : this.list.concat(rows)
					this.hasMore = !!res.has_more
					if (this.hasMore) this.page += 1
				} catch (e) {
					if (reset) this.list = []
				} finally {
					this.loading = false
				}
			},
			async loadRecords() {
				await this.reloadRecords()
			}
		}
	}
</script>

<style>
	.page {
		min-height: 100vh;
		background: #f5f5f5;
		box-sizing: border-box;
	}

	.empty {
		padding-top: 220rpx;
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.empty-img {
		width: 360rpx;
		height: 300rpx;
	}

	.empty-text {
		margin-top: 24rpx;
		font-size: 28rpx;
		color: #999;
	}

	.list {
		padding: 24rpx;
	}

	.item {
		display: flex;
		align-items: center;
		background: #fff;
		border-radius: 16rpx;
		padding: 24rpx;
		margin-bottom: 20rpx;
	}

	.thumb {
		width: 96rpx;
		height: 96rpx;
		border-radius: 12rpx;
		background: #eee;
		flex-shrink: 0;
	}

	.info {
		flex: 1;
		min-width: 0;
		margin: 0 20rpx;
		display: flex;
		flex-direction: column;
	}

	.name {
		font-size: 28rpx;
		color: #222;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.time {
		margin-top: 12rpx;
		font-size: 24rpx;
		color: #999;
	}

	.cost {
		font-size: 28rpx;
		color: #e64750;
		font-weight: 600;
		flex-shrink: 0;
	}

	.end {
		padding: 24rpx 0 40rpx;
		text-align: center;
		font-size: 24rpx;
		color: #999;
	}
</style>
