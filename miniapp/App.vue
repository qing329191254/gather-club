<script>
	export default {
		globalData: {
			gatherTab: '',
			authVersion: 0
		},
		onLaunch() {
			uni.hideTabBar({ fail() {} })
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
