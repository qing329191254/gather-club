<template>
	<view
		v-if="visible"
		class="mask"
		@tap="onClose"
		@touchmove.stop.prevent="preventMove"
	>
		<view class="card" @tap.stop @touchmove.stop.prevent="preventMove">
			<view class="close" @tap="onClose">
				<text class="x">×</text>
			</view>
			<text class="title">核销码</text>
			<view class="title-line" />
			<view class="code-box">
				<text class="digits">{{ formatted }}</text>
			</view>
			<text v-if="expire" class="expire">{{ expire }}</text>
			<view v-if="shownPlaces.length" class="store-box">
				<text class="store-label">{{ placeLabel }}</text>
				<view class="store-grid">
					<view v-for="item in shownPlaces" :key="item.id" class="store-item">
						<view class="pin" />
						<text class="store-name">{{ item.name }}</text>
					</view>
				</view>
			</view>
			<text class="footer">到店后联系工作人员核销使用</text>
		</view>
	</view>
</template>

<script>
	import { api } from '../../common/api.js'

	export default {
		props: {
			visible: {
				type: Boolean,
				default: false
			},
			code: {
				type: String,
				default: ''
			},
			expire: {
				type: String,
				default: ''
			},
			placeLabel: {
				type: String,
				default: '该产品适用门店：'
			},
			places: {
				type: Array,
				default: null
			}
		},
		data() {
			return {
				stores: []
			}
		},
		computed: {
			formatted() {
				const raw = String(this.code || '').replace(/\s/g, '')
				return raw.replace(/(.{4})/g, '$1 ').trim()
			},
			shownPlaces() {
				if (this.places) return this.places
				return this.stores
			}
		},
		watch: {
			visible(value) {
				if (value) this.loadStores()
			}
		},
		methods: {
			preventMove() {},
			onClose() {
				this.$emit('close')
			},
			async loadStores() {
				if (this.places || this.stores.length) return
				try {
					const res = await api.stores()
					this.stores = (res && res.list) || []
				} catch (e) {}
			}
		}
	}
</script>

<style>
	.mask {
		position: fixed;
		left: 0;
		right: 0;
		top: 0;
		bottom: 0;
		z-index: 80;
		background: rgba(0, 0, 0, 0.55);
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 40rpx;
		box-sizing: border-box;
	}

	.card {
		width: 640rpx;
		max-height: 86vh;
		overflow-y: auto;
		background: #ffffff;
		border-radius: 24rpx;
		padding: 36rpx 32rpx 40rpx;
		box-sizing: border-box;
		display: flex;
		flex-direction: column;
		align-items: center;
		position: relative;
	}

	.close {
		position: absolute;
		right: 16rpx;
		top: 12rpx;
		width: 56rpx;
		height: 56rpx;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.x {
		font-size: 44rpx;
		line-height: 1;
		color: #999999;
	}

	.title {
		font-size: 36rpx;
		font-weight: 700;
		color: #222222;
	}

	.title-line {
		width: 72rpx;
		height: 6rpx;
		margin-top: 12rpx;
		border-radius: 6rpx;
		background: #f3b6b6;
	}

	.code-box {
		margin-top: 36rpx;
		margin-bottom: 8rpx;
		min-width: 420rpx;
		padding: 36rpx 28rpx;
		border-radius: 16rpx;
		background: #fff6f5;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.digits {
		font-size: 56rpx;
		font-weight: 700;
		letter-spacing: 6rpx;
		color: #e23636;
	}

	.expire {
		margin-top: 16rpx;
		font-size: 24rpx;
		color: #888888;
		text-align: center;
	}

	.store-box {
		width: 100%;
		margin-top: 28rpx;
		padding: 20rpx 20rpx 8rpx;
		border: 1rpx solid #f3c4c4;
		border-radius: 12rpx;
		box-sizing: border-box;
	}

	.store-label {
		display: block;
		font-size: 26rpx;
		color: #333333;
		margin-bottom: 16rpx;
	}

	.store-grid {
		display: flex;
		flex-wrap: wrap;
	}

	.store-item {
		width: 50%;
		display: flex;
		align-items: flex-start;
		margin-bottom: 16rpx;
		padding-right: 12rpx;
		box-sizing: border-box;
	}

	.pin {
		width: 18rpx;
		height: 18rpx;
		margin-top: 8rpx;
		margin-right: 10rpx;
		border-radius: 50% 50% 50% 0;
		background: #e23636;
		transform: rotate(-45deg);
		flex-shrink: 0;
	}

	.store-name {
		flex: 1;
		font-size: 24rpx;
		line-height: 1.4;
		color: #444444;
	}

	.footer {
		margin-top: 28rpx;
		font-size: 26rpx;
		color: #666666;
		text-align: center;
	}
</style>
