<template>
	<app-loading />
	<view class="page">
		<view v-if="loaded && !list.length" class="empty">
			<view class="empty-illust">
				<view class="pin">
					<view class="pin-head" />
					<view class="pin-point" />
				</view>
				<view class="hill" />
				<text class="q q1">?</text>
				<text class="q q2">?</text>
			</view>
			<text class="empty-text">暂无收货地址...</text>
		</view>

		<view v-else class="list">
			<view v-for="item in list" :key="item.id" class="card" :class="{ 'tap-busy': isTapBusy('addr-' + item.id) }" @tap="onEdit(item)">
				<view class="card-top">
					<text class="name">{{ item.name }}</text>
					<text class="phone">{{ item.phone }}</text>
					<text v-if="item.isDefault" class="tag">默认</text>
				</view>
				<text class="addr">{{ item.region }}{{ item.detail }}</text>
			</view>
		</view>

		<view class="footer">
			<view class="btn ghost" :class="{ 'tap-busy': isTapBusy('import') }" @tap="onImport">微信导入</view>
			<view class="btn solid" @tap="onAdd">新增收货地址</view>
		</view>
	</view>
</template>

<script>
	import { api } from '../../common/api.js'
	import { isLoggedIn, silentLogin } from '../../common/auth.js'

	export default {
		data() {
			return {
				list: [],
				loaded: false
			}
		},
		onShow() {
			this.loadList()
		},
		methods: {
			async loadList() {
				try {
					if (!isLoggedIn()) await silentLogin()
					const res = await api.addresses()
					this.list = res.list || []
				} catch (e) {
					this.list = []
				}
				this.loaded = true
			},
			onImport() {
				if (typeof uni.chooseAddress !== 'function') {
					uni.showToast({ title: '请在微信小程序中使用', icon: 'none' })
					return
				}
				if (!this.holdTap('import')) return
				uni.chooseAddress({
					success: async (res) => {
						try {
							await api.createAddress({
								name: res.userName || '',
								phone: res.telNumber || '',
								province: res.provinceName || '',
								city: res.cityName || '',
								district: res.countyName || '',
								region:
									(res.provinceName || '') +
									(res.cityName || '') +
									(res.countyName || '') +
									(res.streetName || ''),
								detail: res.detailInfoNew || res.detailInfo || '',
								isDefault: this.list.length === 0
							})
							uni.showToast({ title: '导入成功', icon: 'success' })
							this.loadList()
						} catch (e) {
							uni.showToast({ title: (e && e.message) || '导入失败', icon: 'none' })
						} finally {
							this.releaseTap('import')
						}
					},
					fail: (err) => {
						this.releaseTap('import')
						const msg = (err && err.errMsg) || ''
						if (msg.indexOf('cancel') !== -1) return
						uni.showToast({ title: '导入失败', icon: 'none' })
					}
				})
			},
			onAdd() {
				uni.navigateTo({ url: '/pages/mine/address-edit' })
			},
			onEdit(item) {
				const key = 'addr-' + item.id
				if (!this.holdTap(key)) return
				uni.showActionSheet({
					itemList: ['设为默认', '编辑地址', '删除地址'],
					success: (res) => {
						if (res.tapIndex === 1) {
							this.releaseTap(key)
							uni.navigateTo({
								url: '/pages/mine/address-edit?id=' + item.id
							})
							return
						}
						const task = res.tapIndex === 0
							? api.setDefaultAddress(item.id).then(() => {
								uni.showToast({ title: '已设为默认', icon: 'success' })
								this.loadList()
							})
							: api.deleteAddress(item.id).then(() => {
								uni.showToast({ title: '已删除', icon: 'success' })
								this.loadList()
							})
						Promise.resolve(task).catch((e) => {
							uni.showToast({ title: (e && e.message) || '操作失败', icon: 'none' })
						}).finally(() => this.releaseTap(key))
					},
					fail: () => this.releaseTap(key)
				})
			}
		}
	}
</script>

<style>
	.page {
		min-height: 100vh;
		background: #f5f5f5;
		padding-bottom: calc(140rpx + env(safe-area-inset-bottom));
		box-sizing: border-box;
	}

	.empty {
		padding-top: 160rpx;
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.empty-illust {
		width: 360rpx;
		height: 260rpx;
		position: relative;
		display: flex;
		align-items: flex-end;
		justify-content: center;
	}

	.hill {
		width: 280rpx;
		height: 100rpx;
		border-radius: 140rpx 140rpx 0 0;
		background: #e8e8e8;
		position: absolute;
		bottom: 20rpx;
	}

	.pin {
		position: relative;
		z-index: 1;
		margin-bottom: 70rpx;
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.pin-head {
		width: 72rpx;
		height: 72rpx;
		border-radius: 50%;
		background: #cfcfcf;
		position: relative;
	}

	.pin-head::after {
		content: '';
		position: absolute;
		left: 50%;
		top: 50%;
		width: 24rpx;
		height: 24rpx;
		margin: -12rpx 0 0 -12rpx;
		border-radius: 50%;
		background: #f5f5f5;
	}

	.pin-point {
		width: 0;
		height: 0;
		margin-top: -10rpx;
		border-left: 22rpx solid transparent;
		border-right: 22rpx solid transparent;
		border-top: 36rpx solid #cfcfcf;
	}

	.q {
		position: absolute;
		color: #d0d0d0;
		font-size: 28rpx;
		font-weight: 700;
	}

	.q1 {
		left: 48rpx;
		top: 40rpx;
	}

	.q2 {
		right: 56rpx;
		top: 72rpx;
		font-size: 22rpx;
	}

	.empty-text {
		margin-top: 24rpx;
		font-size: 28rpx;
		color: #999999;
	}

	.list {
		padding: 24rpx;
	}

	.card {
		background: #ffffff;
		border-radius: 16rpx;
		padding: 28rpx 24rpx;
		margin-bottom: 16rpx;
	}

	.card-top {
		display: flex;
		align-items: center;
		margin-bottom: 12rpx;
	}

	.name {
		font-size: 30rpx;
		font-weight: 600;
		color: #222222;
		margin-right: 16rpx;
	}

	.phone {
		font-size: 28rpx;
		color: #666666;
		margin-right: 12rpx;
	}

	.tag {
		font-size: 20rpx;
		color: #e23636;
		border: 1rpx solid #e23636;
		border-radius: 6rpx;
		padding: 2rpx 8rpx;
	}

	.addr {
		font-size: 26rpx;
		color: #666666;
		line-height: 1.5;
	}

	.footer {
		position: fixed;
		left: 0;
		right: 0;
		bottom: 0;
		padding: 20rpx 24rpx calc(20rpx + env(safe-area-inset-bottom));
		background: #ffffff;
		display: flex;
		gap: 20rpx;
		box-shadow: 0 -4rpx 16rpx rgba(0, 0, 0, 0.04);
	}

	.btn {
		flex: 1;
		height: 84rpx;
		border-radius: 12rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 30rpx;
		font-weight: 600;
		box-sizing: border-box;
	}

	.btn.ghost {
		background: #ffffff;
		border: 2rpx solid #d8d8d8;
		color: #333333;
	}

	.btn.solid {
		background: #e23636;
		color: #ffffff;
	}
</style>
