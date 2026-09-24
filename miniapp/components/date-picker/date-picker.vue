<template>
	<view
		v-if="visible"
		class="date-mask"
		@tap="onCancel"
		@touchmove.stop.prevent="preventTouchMove"
	>
		<view class="date-sheet" @tap.stop @touchmove.stop.prevent="preventTouchMove">
			<view class="date-bar">
				<text class="date-cancel" @tap="onCancel">取消</text>
				<text class="date-ok" @tap="onConfirm">确定</text>
			</view>
			<picker-view
				class="date-picker"
				:value="pickerValue"
				indicator-style="height: 88rpx;"
				@change="onPick"
			>
				<picker-view-column>
					<view v-for="y in years" :key="'y' + y" class="date-item">{{ y }}年</view>
				</picker-view-column>
				<picker-view-column>
					<view v-for="m in months" :key="'m' + m" class="date-item">{{ m }}月</view>
				</picker-view-column>
				<picker-view-column>
					<view v-for="d in days" :key="'d' + d" class="date-item">{{ d }}日</view>
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
			value: {
				type: String,
				default: ''
			},
			end: {
				type: String,
				default: ''
			},
			start: {
				type: String,
				default: '1950-01-01'
			}
		},
		data() {
			return {
				pickerValue: [30, 0, 0],
				years: [],
				months: [],
				days: []
			}
		},
		watch: {
			visible(val) {
				if (val) this.init()
			}
		},
		methods: {
			pad(n) {
				return n < 10 ? '0' + n : '' + n
			},
			parseDate(str, fallback) {
				if (str && /^\d{4}-\d{2}-\d{2}$/.test(str)) {
					const parts = str.split('-').map(Number)
					return new Date(parts[0], parts[1] - 1, parts[2])
				}
				return fallback
			},
			init() {
				const endDate = this.parseDate(this.end, new Date())
				const startDate = this.parseDate(this.start, new Date(1950, 0, 1))
				const current = this.parseDate(this.value, new Date(2000, 0, 1))

				const startY = startDate.getFullYear()
				const endY = endDate.getFullYear()
				const years = []
				for (let y = startY; y <= endY; y++) years.push(y)
				this.years = years

				let year = current.getFullYear()
				let month = current.getMonth() + 1
				let day = current.getDate()
				if (year < startY) year = startY
				if (year > endY) year = endY

				this.months = this.buildMonths(year, startDate, endDate)
				if (this.months.indexOf(month) === -1) month = this.months[0] || 1
				this.days = this.buildDays(year, month, startDate, endDate)
				if (this.days.indexOf(day) === -1) day = this.days[0] || 1

				this.pickerValue = [
					Math.max(0, years.indexOf(year)),
					Math.max(0, this.months.indexOf(month)),
					Math.max(0, this.days.indexOf(day))
				]
			},
			buildMonths(year, startDate, endDate) {
				let from = 1
				let to = 12
				if (year === startDate.getFullYear()) from = startDate.getMonth() + 1
				if (year === endDate.getFullYear()) to = endDate.getMonth() + 1
				const list = []
				for (let m = from; m <= to; m++) list.push(m)
				return list
			},
			buildDays(year, month, startDate, endDate) {
				const max = new Date(year, month, 0).getDate()
				let from = 1
				let to = max
				if (year === startDate.getFullYear() && month === startDate.getMonth() + 1) {
					from = startDate.getDate()
				}
				if (year === endDate.getFullYear() && month === endDate.getMonth() + 1) {
					to = endDate.getDate()
				}
				const list = []
				for (let d = from; d <= to; d++) list.push(d)
				return list
			},
			onPick(e) {
				const val = e.detail.value || [0, 0, 0]
				const endDate = this.parseDate(this.end, new Date())
				const startDate = this.parseDate(this.start, new Date(1950, 0, 1))
				const year = this.years[val[0]] || this.years[0]
				this.months = this.buildMonths(year, startDate, endDate)
				let monthIdx = Math.min(val[1], this.months.length - 1)
				const month = this.months[monthIdx] || this.months[0]
				this.days = this.buildDays(year, month, startDate, endDate)
				let dayIdx = Math.min(val[2], this.days.length - 1)
				this.pickerValue = [val[0], monthIdx, dayIdx]
			},
			onCancel() {
				this.$emit('close')
			},
			onConfirm() {
				const y = this.years[this.pickerValue[0]] || this.years[0]
				const m = this.months[this.pickerValue[1]] || this.months[0]
				const d = this.days[this.pickerValue[2]] || this.days[0]
				this.$emit('confirm', y + '-' + this.pad(m) + '-' + this.pad(d))
				this.$emit('close')
			},
			preventTouchMove() {}
		}
	}
</script>

<style>
	.date-mask {
		position: fixed;
		left: 0;
		right: 0;
		top: 0;
		bottom: 0;
		z-index: 10000;
		background: rgba(0, 0, 0, 0.45);
		display: flex;
		flex-direction: column;
		justify-content: flex-end;
	}

	.date-sheet {
		background: #ffffff;
		border-radius: 12rpx 12rpx 0 0;
		padding-bottom: env(safe-area-inset-bottom);
	}

	.date-bar {
		height: 96rpx;
		padding: 0 32rpx;
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.date-cancel {
		font-size: 30rpx;
		color: #999999;
		line-height: 96rpx;
	}

	.date-ok {
		font-size: 30rpx;
		color: #C6453C;
		line-height: 96rpx;
		font-weight: 600;
	}

	.date-picker {
		width: 100%;
		height: 440rpx;
	}

	.date-item {
		height: 88rpx;
		line-height: 88rpx;
		text-align: center;
		font-size: 36rpx;
		color: #222222;
		font-weight: 700;
	}
</style>
