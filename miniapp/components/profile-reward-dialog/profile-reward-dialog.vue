<template>
	<view v-if="visible" class="mask" @tap="onClose" @touchmove.stop.prevent="noop">
		<view class="panel" @tap.stop @touchmove.stop.prevent="noop">
			<view v-if="mode === 'prompt'" class="art art-doc">
				<view class="paper">
					<view class="line" />
					<view class="line short" />
					<view class="line" />
				</view>
				<view class="pencil" />
			</view>
			<view v-else class="art art-coin">
				<view class="ray r1" />
				<view class="ray r2" />
				<view class="ray r3" />
				<view class="dot d1" />
				<view class="dot d2" />
				<view class="dot d3" />
				<view class="dot d4" />
				<view class="coin">积</view>
			</view>

			<view v-if="mode === 'prompt'" class="copy">
				<text class="title">完善您的个人信息</text>
				<view class="reward-line">
					<text>得 </text>
					<text class="num">{{ points }}</text>
					<text> 积分</text>
				</view>
			</view>
			<view v-else class="copy">
				<text class="title">恭喜您获得</text>
				<view class="reward-line">
					<text class="num">{{ points }}</text>
					<text> 积分</text>
				</view>
			</view>

			<view class="main-btn" @tap="onMain">{{ mode === 'prompt' ? '立即完善' : '获得更多积分' }}</view>
			<text v-if="mode === 'prompt'" class="later" @tap="onLater">稍后再说</text>
		</view>
		<view class="close" @tap.stop="onClose">×</view>
	</view>
</template>

<script>
	export default {
		props: {
			visible: { type: Boolean, default: false },
			mode: { type: String, default: 'prompt' },
			points: { type: Number, default: 0 }
		},
		methods: {
			noop() {},
			onClose() {
				this.$emit('close')
			},
			onLater() {
				this.$emit('later')
			},
			onMain() {
				this.$emit(this.mode === 'prompt' ? 'go' : 'more')
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
		z-index: 10000;
		background: rgba(0, 0, 0, 0.55);
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 0 72rpx;
	}

	.panel {
		width: 100%;
		background: #fff;
		border-radius: 12rpx;
		padding: 48rpx 40rpx 36rpx;
		display: flex;
		flex-direction: column;
		align-items: center;
		box-sizing: border-box;
	}

	.art {
		position: relative;
		width: 220rpx;
		height: 180rpx;
		margin-bottom: 12rpx;
	}

	.paper {
		position: absolute;
		left: 28rpx;
		top: 24rpx;
		width: 120rpx;
		height: 140rpx;
		background: #F7F3EE;
		border: 4rpx solid #C4B5A8;
		border-radius: 8rpx;
		padding: 28rpx 16rpx;
		box-sizing: border-box;
	}

	.line {
		height: 8rpx;
		background: #D8D0C6;
		border-radius: 4rpx;
		margin-bottom: 14rpx;
	}

	.line.short {
		width: 60%;
	}

	.pencil {
		position: absolute;
		right: 18rpx;
		bottom: 8rpx;
		width: 18rpx;
		height: 110rpx;
		background: linear-gradient(#f6c445, #f0a020);
		border-radius: 8rpx;
		transform: rotate(38deg);
	}

	.coin {
		position: absolute;
		left: 50%;
		top: 50%;
		width: 120rpx;
		height: 120rpx;
		margin-left: -60rpx;
		margin-top: -60rpx;
		border-radius: 50%;
		background: radial-gradient(circle at 35% 35%, #ffe38a, #e0a322 62%, #b67b10);
		color: #8a5a10;
		font-size: 52rpx;
		font-weight: 700;
		display: flex;
		align-items: center;
		justify-content: center;
		box-shadow: 0 8rpx 0 #c48a1a;
	}

	.ray {
		position: absolute;
		left: 50%;
		top: 50%;
		width: 8rpx;
		height: 36rpx;
		margin-left: -4rpx;
		background: #f3c96a;
		border-radius: 8rpx;
	}

	.r1 { transform: translateY(-78rpx); }
	.r2 { transform: rotate(55deg) translateY(-78rpx); }
	.r3 { transform: rotate(-55deg) translateY(-78rpx); }

	.dot {
		position: absolute;
		width: 14rpx;
		height: 14rpx;
		border-radius: 50%;
	}

	.d1 { background: #f25b5b; left: 12rpx; top: 20rpx; }
	.d2 { background: #3db5ff; right: 16rpx; top: 28rpx; }
	.d3 { background: #47c46a; left: 8rpx; bottom: 24rpx; }
	.d4 { background: #f0b429; right: 10rpx; bottom: 18rpx; }

	.copy {
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.title {
		font-size: 34rpx;
		font-weight: 600;
		color: #222;
		line-height: 1.4;
	}

	.reward-line {
		margin-top: 12rpx;
		font-size: 32rpx;
		color: #222;
		display: flex;
		align-items: baseline;
	}

	.num {
		font-size: 56rpx;
		font-weight: 700;
		color: #C6453C;
		line-height: 1;
		margin: 0 8rpx;
	}

	.main-btn {
		margin-top: 36rpx;
		width: 100%;
		height: 88rpx;
		line-height: 88rpx;
		text-align: center;
		border-radius: 10rpx;
		background: #C6453C;
		color: #fff;
		font-size: 32rpx;
		font-weight: 600;
	}

	.later {
		margin-top: 24rpx;
		font-size: 28rpx;
		color: #999;
	}

	.close {
		margin-top: 36rpx;
		width: 64rpx;
		height: 64rpx;
		border-radius: 50%;
		border: 2rpx solid rgba(255, 255, 255, 0.85);
		color: #fff;
		font-size: 40rpx;
		line-height: 60rpx;
		text-align: center;
	}
</style>
