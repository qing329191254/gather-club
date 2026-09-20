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
				silentLogin().then(() => {
					this.globalData.authVersion = Date.now()
				})
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
		background-color: #F6F3EF;
		font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Helvetica Neue", Helvetica, "Microsoft YaHei", sans-serif;
	}
</style>
