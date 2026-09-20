<template>
	<view class="page">
		<view class="hero">
			<text class="subtitle">让大家更好认识你~</text>
			<button
				class="avatar-wrap"
				open-type="chooseAvatar"
				@chooseavatar="onChooseAvatar"
			>
				<image
					class="avatar"
					:src="form.avatar || '/static/icons/avatar-default.png'"
					mode="aspectFill"
				/>
				<view class="cam">
					<image class="cam-icon" src="/static/icons/camera.png" mode="aspectFit" />
				</view>
			</button>
		</view>

		<view class="card">
			<view class="row" @tap="onNickname">
				<text class="label">昵称</text>
				<view class="right">
					<text class="value">{{ form.nickname || '请输入昵称' }}</text>
					<view class="arrow" />
				</view>
			</view>
			<view class="row" @tap="openBirthday">
				<text class="label">生日</text>
				<view class="right">
					<text class="value" :class="{ placeholder: !form.birthday }">
						{{ form.birthday || '请选择生日' }}
					</text>
					<view class="arrow" />
				</view>
			</view>
			<view class="row phone-row">
				<text class="label">手机号</text>
				<view class="right">
					<text class="value">{{ form.phone || '未绑定' }}</text>
					<text class="link" @tap.stop="onPhone">{{ phoneEditLabel }}</text>
				</view>
			</view>
			<view class="row" @tap="onHobby">
				<text class="label">兴趣爱好</text>
				<view class="right">
					<text class="value" :class="{ placeholder: !form.hobby }">
						{{ form.hobby || '' }}
					</text>
					<view class="arrow" />
				</view>
			</view>
		</view>

		<view class="save-wrap">
			<view class="save-btn" @tap="onSave">保存</view>
		</view>

		<date-picker
			:visible="birthdayVisible"
			:value="form.birthday || '2000-01-01'"
			:end="today"
			@confirm="onBirthdayConfirm"
			@close="birthdayVisible = false"
		/>
		<tip-dialog
			:visible="phoneTipVisible"
			phone-auth
			title="温馨提示"
			:message="phoneTipMessage"
			@confirm="onPhoneTipConfirm"
			@cancel="phoneTipVisible = false"
			@close="phoneTipVisible = false"
		/>

		<!-- 微信昵称：type=nickname 可拉起选用微信昵称 -->
		<view
			v-if="nickSheetVisible"
			class="nick-mask"
			@tap="closeNickSheet"
			@touchmove.stop.prevent="preventTouchMove"
		>
			<view class="nick-sheet" @tap.stop @touchmove.stop.prevent="preventTouchMove">
				<text class="nick-title">修改昵称</text>
				<input
					class="nick-input"
					type="nickname"
					:value="nickDraft"
					placeholder="点击输入，可选用微信昵称"
					placeholder-class="nick-ph"
					maxlength="20"
					@input="onNickInput"
					@blur="onNickBlur"
				/>
				<view class="nick-actions">
					<view class="nick-btn ghost" @tap="closeNickSheet">取消</view>
					<view class="nick-btn solid" @tap="confirmNick">确定</view>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
	import DatePicker from '../../components/date-picker/date-picker.vue'
	import TipDialog from '../../components/tip-dialog/tip-dialog.vue'
	import { getUser, saveLogin, getOpenid, refreshProfile, isLoggedIn, silentLogin } from '../../common/auth.js'
	import { api } from '../../common/api.js'

	const PROFILE_KEY = 'gather_profile'
	const PHONE_EDITED_KEY = 'gather_phone_edited'

	export default {
		components: {
			DatePicker,
			TipDialog
		},
		data() {
			return {
				today: '',
				birthdayVisible: false,
				phoneTipVisible: false,
				phoneTipMessage: '您仅有一次修改机会\n是否确认修改?',
				phoneEditLabel: '修改手机号 >',
				nickSheetVisible: false,
				nickDraft: '',
				form: {
					avatar: '',
					nickname: '微信用户',
					birthday: '',
					phone: '',
					hobby: ''
				}
			}
		},
		onLoad() {
			const now = new Date()
			const m = String(now.getMonth() + 1).padStart(2, '0')
			const d = String(now.getDate()).padStart(2, '0')
			this.today = `${now.getFullYear()}-${m}-${d}`
			this.loadProfile()
		},
		onShow() {
			this.loadProfile()
		},
		methods: {
			preventTouchMove() {},
			async loadProfile() {
				if (!isLoggedIn()) await silentLogin()
				else await refreshProfile()
				const user = getUser()
				this.form = Object.assign({}, this.form, {
					avatar: user.avatar || this.form.avatar || '',
					nickname: user.nickname || this.form.nickname || '微信用户',
					birthday: user.birthday || '',
					phone: user.phone || '',
					hobby: user.hobby || ''
				})
				try {
					const raw = uni.getStorageSync(PROFILE_KEY)
					if (raw && typeof raw === 'object') {
						if (!this.form.birthday && raw.birthday) this.form.birthday = raw.birthday
						if (!this.form.hobby && raw.hobby) this.form.hobby = raw.hobby
						if (!this.form.avatar && raw.avatar) this.form.avatar = raw.avatar
					}
				} catch (e) {}
				this.phoneEditLabel = user.phoneEdited || uni.getStorageSync(PHONE_EDITED_KEY) ? '已绑定' : '修改手机号 >'
			},
			saveLocal() {
				uni.setStorageSync(PROFILE_KEY, this.form)
			},
			onChooseAvatar(e) {
				const url = e && e.detail && e.detail.avatarUrl
				if (url) {
					this.form.avatar = url
				}
			},
			onNickname() {
				uni.showActionSheet({
					itemList: ['使用微信昵称', '手动输入'],
					success: (res) => {
						if (res.tapIndex === 0) {
							this.nickDraft = this.form.nickname || ''
							this.nickSheetVisible = true
						} else if (res.tapIndex === 1) {
							this.editNicknameManual()
						}
					}
				})
			},
			editNicknameManual() {
				uni.showModal({
					title: '修改昵称',
					editable: true,
					placeholderText: '请输入昵称',
					content: this.form.nickname,
					success: (res) => {
						if (res.confirm && res.content != null) {
							const name = String(res.content).trim()
							if (name) this.form.nickname = name
						}
					}
				})
			},
			onNickInput(e) {
				this.nickDraft = (e && e.detail && e.detail.value) || ''
			},
			onNickBlur(e) {
				const v = (e && e.detail && e.detail.value) || this.nickDraft
				this.nickDraft = String(v || '').trim()
			},
			confirmNick() {
				const name = String(this.nickDraft || '').trim()
				if (!name) {
					uni.showToast({ title: '请输入昵称', icon: 'none' })
					return
				}
				this.form.nickname = name
				this.closeNickSheet()
			},
			closeNickSheet() {
				this.nickSheetVisible = false
			},
			openBirthday() {
				this.birthdayVisible = true
			},
			onBirthdayConfirm(value) {
				this.form.birthday = value
			},
			onPhone() {
				if (getUser().phoneEdited || uni.getStorageSync(PHONE_EDITED_KEY)) {
					uni.showToast({ title: '手机号仅可修改一次', icon: 'none' })
					return
				}
				this.phoneTipVisible = true
			},
			onPhoneTipConfirm(detail) {
				this.phoneTipVisible = false
				const d = detail || {}
				const errMsg = String(d.errMsg || '')
				const ok = !errMsg || errMsg.indexOf(':ok') !== -1
				if (!ok) {
					return
				}
				if (d.phoneNumber && /^1\d{10}$/.test(String(d.phoneNumber))) {
					this.form.phone = String(d.phoneNumber)
				}
				uni.setStorageSync(PHONE_EDITED_KEY, 1)
				this.saveLocal()
				uni.showToast({ title: '修改成功', icon: 'success' })
			},
			onHobby() {
				uni.navigateTo({ url: '/pages/mine/hobbies' })
			},
			async onSave() {
				this.saveLocal()
				uni.showLoading({ title: '保存中', mask: true })
				try {
					if (!isLoggedIn()) await silentLogin()
					const res = await api.updateProfile({
						nickname: this.form.nickname,
						avatar: this.form.avatar,
						birthday: this.form.birthday,
						hobby: this.form.hobby,
						phone: this.form.phone
					})
					saveLogin(
						Object.assign({}, getUser(), {
							avatar: res.avatar,
							nickname: res.nickname,
							phone: res.phone,
							birthday: res.birthday,
							hobby: res.hobby,
							phoneEdited: res.phoneEdited,
							points: res.points,
							vipLevel: res.vipLevel,
							vip: res.vip
						}),
						getOpenid()
					)
					uni.hideLoading()
					uni.showToast({ title: '保存成功', icon: 'success' })
					setTimeout(() => {
						uni.navigateBack({ fail() {} })
					}, 500)
				} catch (e) {
					uni.hideLoading()
					uni.showToast({ title: (e && e.message) || '保存失败', icon: 'none' })
				}
			}
		}
	}
</script>

<style>
	.page {
		min-height: 100vh;
		background: #f5f5f5;
		padding-bottom: calc(160rpx + env(safe-area-inset-bottom));
		box-sizing: border-box;
	}

	.hero {
		padding: 8rpx 0 48rpx;
		background: linear-gradient(180deg, #ffe8ec 0%, #fff5f6 42%, #f5f5f5 100%);
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.subtitle {
		font-size: 24rpx;
		color: #999999;
		margin-bottom: 36rpx;
	}

	.avatar-wrap {
		position: relative;
		width: 168rpx;
		height: 168rpx;
		padding: 0;
		margin: 0;
		background: transparent;
		border: none;
		line-height: 1;
	}

	.avatar-wrap::after {
		border: none;
	}

	.avatar {
		width: 168rpx;
		height: 168rpx;
		border-radius: 50%;
		background: #f0e6dc;
	}

	.cam {
		position: absolute;
		right: -4rpx;
		bottom: 0;
		width: 64rpx;
		height: 64rpx;
		border-radius: 50%;
		background: #3d4f7a;
		display: flex;
		align-items: center;
		justify-content: center;
		border: 4rpx solid #fff;
		box-sizing: border-box;
		pointer-events: none;
	}

	.cam-icon {
		width: 38rpx;
		height: 38rpx;
	}

	.card {
		margin: 0 24rpx;
		background: #ffffff;
		border-radius: 20rpx;
		overflow: hidden;
	}

	.row {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 34rpx 28rpx;
		border-bottom: 1rpx solid #f2f2f2;
	}

	.row:last-child {
		border-bottom: none;
	}

	.label {
		font-size: 30rpx;
		color: #222222;
		flex-shrink: 0;
	}

	.right {
		display: flex;
		align-items: center;
		min-width: 0;
		flex: 1;
		justify-content: flex-end;
	}

	.value {
		font-size: 28rpx;
		color: #333333;
		max-width: 360rpx;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.value.placeholder {
		color: #bbbbbb;
	}

	.phone-row .value {
		margin-right: 12rpx;
	}

	.link {
		font-size: 26rpx;
		color: #999999;
		flex-shrink: 0;
	}

	.arrow {
		width: 14rpx;
		height: 14rpx;
		border-top: 3rpx solid #c8c8c8;
		border-right: 3rpx solid #c8c8c8;
		transform: rotate(45deg);
		margin-left: 12rpx;
		flex-shrink: 0;
	}

	.save-wrap {
		position: fixed;
		left: 0;
		right: 0;
		bottom: 0;
		padding: 20rpx 40rpx calc(20rpx + env(safe-area-inset-bottom));
		background: linear-gradient(180deg, rgba(245, 245, 245, 0) 0%, #f5f5f5 30%);
	}

	.save-btn {
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

	.nick-mask {
		position: fixed;
		left: 0;
		right: 0;
		top: 0;
		bottom: 0;
		z-index: 11000;
		background: rgba(0, 0, 0, 0.45);
		display: flex;
		align-items: flex-end;
		justify-content: center;
	}

	.nick-sheet {
		width: 100%;
		background: #ffffff;
		border-radius: 28rpx 28rpx 0 0;
		padding: 40rpx 36rpx calc(40rpx + env(safe-area-inset-bottom));
		box-sizing: border-box;
	}

	.nick-title {
		display: block;
		text-align: center;
		font-size: 32rpx;
		font-weight: 700;
		color: #222;
		margin-bottom: 28rpx;
	}

	.nick-input {
		height: 88rpx;
		border-radius: 16rpx;
		background: #f6f6f6;
		padding: 0 28rpx;
		font-size: 30rpx;
		color: #222;
		box-sizing: border-box;
		margin-bottom: 32rpx;
	}

	.nick-ph {
		color: #bbbbbb;
	}

	.nick-actions {
		display: flex;
		gap: 20rpx;
	}

	.nick-btn {
		flex: 1;
		height: 84rpx;
		border-radius: 999rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 30rpx;
		font-weight: 600;
		box-sizing: border-box;
	}

	.nick-btn.ghost {
		background: #ffffff;
		border: 2rpx solid #dddddd;
		color: #666666;
	}

	.nick-btn.solid {
		background: #e23636;
		color: #ffffff;
	}
</style>
