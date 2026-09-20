<template>
	<app-loading />
	<view class="page">
		<view class="card">
			<view class="row">
				<text class="label">姓名</text>
				<input
					class="field"
					v-model="form.name"
					placeholder="请输入收货人姓名"
					placeholder-class="ph"
				/>
				<view class="arrow" />
			</view>
			<view class="row">
				<text class="label">手机号</text>
				<input
					class="field"
					v-model="form.phone"
					type="number"
					maxlength="11"
					placeholder="请输入收货人手机号"
					placeholder-class="ph"
				/>
				<view class="arrow" />
			</view>
		</view>

		<view class="card">
			<picker mode="region" :value="regionValue" @change="onRegionChange">
				<view class="row">
					<text class="label">选择地区</text>
					<text class="field" :class="{ ph: !regionText }">
						{{ regionText || '请选择省市区' }}
					</text>
					<view class="arrow" />
				</view>
			</picker>
			<view class="row">
				<text class="label">详细地址</text>
				<input
					class="field"
					v-model="form.detail"
					placeholder="请输入收货人详细地址"
					placeholder-class="ph"
				/>
				<view class="arrow" />
			</view>
			<view class="paste-box">
				<textarea
					class="paste-input"
					v-model="pasteText"
					placeholder="粘贴地址到此处，将自动识别姓名/电话/地区/详细地址"
					placeholder-class="ph"
					:maxlength="300"
				/>
				<view class="paste-actions">
					<text class="clear" @tap="onClearPaste">清除</text>
					<view class="submit" @tap="onParsePaste">提交</view>
				</view>
			</view>
		</view>

		<view class="card switch-card">
			<text class="label">设为默认地址</text>
			<switch :checked="form.isDefault" color="#e23636" @change="onDefaultChange" />
		</view>

		<view class="footer">
			<view class="save" :class="{ 'tap-busy': isTapBusy('save') }" @tap="onSave">保存</view>
		</view>
	</view>
</template>

<script>
	import { api } from '../../common/api.js'
	import { isLoggedIn, silentLogin } from '../../common/auth.js'

	export default {
		data() {
			return {
				editId: '',
				pasteText: '',
				regionValue: [],
				form: {
					name: '',
					phone: '',
					province: '',
					city: '',
					district: '',
					detail: '',
					isDefault: false
				}
			}
		},
		computed: {
			regionText() {
				const { province, city, district } = this.form
				if (!province) return ''
				return [province, city, district].filter(Boolean).join(' ')
			}
		},
		onLoad(query) {
			this.editId = (query && query.id) || ''
			this.readClipboard()
			if (this.editId) this.loadEdit()
		},
		methods: {
			async loadEdit() {
				if (!isLoggedIn()) await silentLogin()
				try {
					const res = await api.addresses()
					const item = (res.list || []).find((row) => String(row.id) === String(this.editId))
					if (!item) return
					this.form = {
						name: item.name || '',
						phone: item.phone || '',
						province: item.province || '',
						city: item.city || '',
						district: item.district || '',
						detail: item.detail || '',
						isDefault: !!item.isDefault
					}
					this.regionValue = [this.form.province, this.form.city, this.form.district].filter(Boolean)
					uni.setNavigationBarTitle({ title: '编辑地址' })
				} catch (e) {}
			},
			readClipboard() {
				uni.getClipboardData({
					success: (res) => {
						const text = (res && res.data) || ''
						if (text && !this.pasteText) {
							this.pasteText = String(text).trim()
						}
					}
				})
			},
			onRegionChange(e) {
				const value = (e.detail && e.detail.value) || []
				this.regionValue = value
				this.form.province = value[0] || ''
				this.form.city = value[1] || ''
				this.form.district = value[2] || ''
			},
			onDefaultChange(e) {
				this.form.isDefault = !!(e.detail && e.detail.value)
			},
			onClearPaste() {
				this.pasteText = ''
			},
			onParsePaste() {
				const text = (this.pasteText || '').trim()
				if (!text) {
					uni.showToast({ title: '请先粘贴地址', icon: 'none' })
					return
				}
				const parsed = parseAddressText(text)
				if (parsed.name) this.form.name = parsed.name
				if (parsed.phone) this.form.phone = parsed.phone
				if (parsed.province) {
					this.form.province = parsed.province
					this.form.city = parsed.city
					this.form.district = parsed.district
					this.regionValue = [parsed.province, parsed.city, parsed.district].filter(Boolean)
				}
				if (parsed.detail) this.form.detail = parsed.detail
				uni.showToast({ title: '已识别', icon: 'success' })
			},
			async onSave() {
				const name = (this.form.name || '').trim()
				const phone = (this.form.phone || '').trim()
				const detail = (this.form.detail || '').trim()
				if (!name) {
					uni.showToast({ title: '请填写收货人姓名', icon: 'none' })
					return
				}
				if (!/^1\d{10}$/.test(phone)) {
					uni.showToast({ title: '请填写正确手机号', icon: 'none' })
					return
				}
				if (!this.form.province) {
					uni.showToast({ title: '请选择省市区', icon: 'none' })
					return
				}
				if (!detail) {
					uni.showToast({ title: '请填写详细地址', icon: 'none' })
					return
				}
				return this.tapGuard('save', async () => {
				if (!isLoggedIn()) await silentLogin()
				const payload = {
					name,
					phone,
					province: this.form.province,
					city: this.form.city,
					district: this.form.district,
					region: [this.form.province, this.form.city, this.form.district].filter(Boolean).join(''),
					detail,
					isDefault: this.form.isDefault
				}
				try {
					if (this.editId) await api.updateAddress(this.editId, payload)
					else await api.createAddress(payload)
					uni.showToast({ title: '保存成功', icon: 'success' })
					setTimeout(() => {
						uni.navigateBack({ fail() {} })
					}, 400)
				} catch (e) {
					uni.showToast({ title: (e && e.message) || '保存失败', icon: 'none' })
				}
				})
			}
		}
	}

	function parseAddressText(text) {
		const raw = String(text).replace(/\s+/g, ' ').trim()
		const phoneMatch = raw.match(/1[3-9]\d{9}/)
		const phone = phoneMatch ? phoneMatch[0] : ''
		let rest = raw.replace(phone, ' ').replace(/[，,。；;]/g, ' ').replace(/\s+/g, ' ').trim()

		let name = ''
		const nameMatch = rest.match(/^[\u4e00-\u9fa5·]{2,4}/)
		if (nameMatch) {
			name = nameMatch[0]
			rest = rest.slice(name.length).trim()
		}

		let province = ''
		let city = ''
		let district = ''
		const regionMatch = rest.match(
			/((?:[\u4e00-\u9fa5]{2,8}(?:省|自治区))|(?:北京市|天津市|上海市|重庆市))?((?:[\u4e00-\u9fa5]{2,10}市))?((?:[\u4e00-\u9fa5]{2,10}(?:区|县|旗)))?/
		)
		if (regionMatch) {
			province = regionMatch[1] || ''
			city = regionMatch[2] || ''
			district = regionMatch[3] || ''
			const hit = (province || '') + (city || '') + (district || '')
			if (hit) {
				rest = rest.replace(hit, '').trim()
			}
		}
		if (!province && (city === '北京市' || city === '上海市' || city === '天津市' || city === '重庆市')) {
			province = city
		}

		return {
			name,
			phone,
			province,
			city,
			district,
			detail: rest
		}
	}
</script>

<style>
	.page {
		min-height: 100vh;
		box-sizing: border-box;
		background: #f7f3f3;
		padding: 24rpx 24rpx calc(140rpx + env(safe-area-inset-bottom));
	}

	.card {
		background: #ffffff;
		border-radius: 20rpx;
		margin-bottom: 20rpx;
		overflow: hidden;
	}

	.row {
		display: flex;
		align-items: center;
		min-height: 100rpx;
		padding: 0 28rpx;
		border-bottom: 1rpx solid #f3f3f3;
	}

	.row:last-child {
		border-bottom: none;
	}

	.label {
		width: 160rpx;
		flex-shrink: 0;
		font-size: 30rpx;
		color: #222222;
	}

	.field {
		flex: 1;
		min-width: 0;
		font-size: 28rpx;
		color: #222222;
		text-align: right;
	}

	.ph {
		color: #c8c8c8;
	}

	.arrow {
		width: 14rpx;
		height: 14rpx;
		margin-left: 12rpx;
		border-top: 3rpx solid #d0d0d0;
		border-right: 3rpx solid #d0d0d0;
		transform: rotate(45deg);
		flex-shrink: 0;
	}

	.paste-box {
		margin: 8rpx 24rpx 24rpx;
		background: #f7f7f7;
		border-radius: 16rpx;
		padding: 20rpx 20rpx 16rpx;
	}

	.paste-input {
		width: 100%;
		height: 140rpx;
		font-size: 26rpx;
		color: #333333;
		line-height: 1.5;
	}

	.paste-actions {
		display: flex;
		justify-content: flex-end;
		align-items: center;
		margin-top: 8rpx;
	}

	.clear {
		font-size: 26rpx;
		color: #999999;
		padding: 8rpx 20rpx;
	}

	.submit {
		min-width: 96rpx;
		height: 52rpx;
		padding: 0 20rpx;
		border-radius: 8rpx;
		background: #e23636;
		color: #ffffff;
		font-size: 26rpx;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.switch-card {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 24rpx 28rpx;
	}

	.switch-card .label {
		width: auto;
	}

	.footer {
		position: fixed;
		left: 0;
		right: 0;
		bottom: 0;
		padding: 16rpx 32rpx calc(16rpx + env(safe-area-inset-bottom));
		background: #f7f3f3;
	}

	.save {
		height: 88rpx;
		border-radius: 999rpx;
		background: #e23636;
		color: #ffffff;
		font-size: 32rpx;
		font-weight: 600;
		display: flex;
		align-items: center;
		justify-content: center;
	}
</style>
