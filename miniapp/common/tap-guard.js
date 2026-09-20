export const tapGuardMixin = {
	data() {
		return {
			tapBusy: {}
		}
	},
	methods: {
		isTapBusy(key) {
			return !!this.tapBusy[key]
		},
		holdTap(key) {
			const k = String(key || 'default')
			if (this.tapBusy[k]) return false
			this.tapBusy = Object.assign({}, this.tapBusy, { [k]: true })
			return true
		},
		releaseTap(key) {
			const k = String(key || 'default')
			if (!this.tapBusy[k]) return
			const next = Object.assign({}, this.tapBusy)
			delete next[k]
			this.tapBusy = next
		},
		tapGuard(key, fn) {
			if (!this.holdTap(key)) return
			let ret
			try {
				ret = typeof fn === 'function' ? fn() : null
			} catch (e) {
				this.releaseTap(key)
				throw e
			}
			if (ret && typeof ret.then === 'function') {
				return ret.finally(() => this.releaseTap(key))
			}
			this.releaseTap(key)
			return ret
		},
		askModal(options) {
			return new Promise((resolve) => {
				uni.showModal(
					Object.assign({}, options || {}, {
						success: (res) => resolve(!!(res && res.confirm)),
						fail: () => resolve(false)
					})
				)
			})
		}
	}
}
