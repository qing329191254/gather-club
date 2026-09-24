<script>
	import { initCloud } from './common/cloud.js'
	import { isLoggedIn, silentLogin } from './common/auth.js'

	export default {
		globalData: {
			gatherTab: '',
			authVersion: 0,
			site: null
		},
		onLaunch() {
			uni.hideTabBar({ fail() {} })
			initCloud()
			if (isLoggedIn()) {
				silentLogin({ quiet: true })
					.then(() => {
						this.globalData.authVersion = Date.now()
					})
					.catch(() => {})
			}
		},
		onShow() {
			uni.hideTabBar({ fail() {} })
		},
		onHide() {}
	}
</script>

<style>
	page {
		background-color: #F1EEE8;
		font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Helvetica Neue", Helvetica, "Microsoft YaHei", sans-serif;
		color: #2C2A27;
	}

	/* 只作用在加了这个类的那一个按钮上 */
	.tap-busy {
		opacity: 0.45;
	}
</style>
