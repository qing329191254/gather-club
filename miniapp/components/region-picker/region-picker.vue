<template>
	<view
		v-if="visible"
		class="region-mask"
		@tap="onCancel"
		@touchmove.stop.prevent="preventTouchMove"
	>
		<view class="region-sheet" @tap.stop @touchmove.stop.prevent="preventTouchMove">
			<view class="region-bar">
				<text class="region-cancel" @tap="onCancel">取消</text>
				<text class="region-ok" @tap="onConfirm">确定</text>
			</view>
			<picker-view
				class="region-picker"
				:value="pickerValue"
				indicator-style="height: 88rpx;"
				@change="onPick"
			>
				<picker-view-column>
					<view v-for="item in options" :key="item.id" class="region-item">
						{{ item.name }}
					</view>
				</picker-view-column>
			</picker-view>
		</view>
	</view>
</template>

<script>
	export default {
		props: {
			visible: {
				type: Boolean,
				default: false
			},
			options: {
				type: Array,
				default() {
					return []
				}
			},
			value: {
				type: String,
				default: ''
			}
		},
		data() {
			return {
				pickerValue: [0]
			}
		},
		watch: {
			visible(val) {
				if (val) {
					this.syncIndex()
				}
			},
			value() {
				if (this.visible) {
					this.syncIndex()
				}
			},
			options() {
				if (this.visible) {
					this.syncIndex()
				}
			}
		},
		methods: {
			syncIndex() {
				const idx = this.options.findIndex((item) => item.name === this.value || item.id === this.value)
				this.pickerValue = [idx >= 0 ? idx : 0]
			},
			onPick(e) {
				this.pickerValue = e.detail.value || [0]
			},
			onCancel() {
				this.$emit('close')
			},
			onConfirm() {
				const idx = (this.pickerValue && this.pickerValue[0]) || 0
				const item = this.options[idx] || this.options[0]
				if (item) {
					this.$emit('confirm', item)
				}
				this.$emit('close')
			},
			preventTouchMove() {}
		}
	}
</script>

<style>
	.region-mask {
		position: fixed;
		left: 0;
		right: 0;
		top: 0;
		bottom: 0;
		z-index: 1000;
		background: rgba(0, 0, 0, 0.45);
		display: flex;
		flex-direction: column;
		justify-content: flex-end;
	}

	.region-sheet {
		background: #fff;
		border-radius: 24rpx 24rpx 0 0;
		padding-bottom: env(safe-area-inset-bottom);
	}

	.region-bar {
		height: 96rpx;
		padding: 0 32rpx;
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.region-cancel {
		font-size: 30rpx;
		color: #999;
		line-height: 96rpx;
	}

	.region-ok {
		font-size: 30rpx;
		color: #E03D47;
		line-height: 96rpx;
	}

	.region-picker {
		width: 100%;
		height: 440rpx;
	}

	.region-item {
		height: 88rpx;
		line-height: 88rpx;
		text-align: center;
		font-size: 34rpx;
		color: #333;
		font-weight: 600;
	}
</style>
