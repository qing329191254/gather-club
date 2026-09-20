import App from './App'

function currentPageShare() {
	const pages = getCurrentPages()
	const page = pages[pages.length - 1]
	const route = (page && page.route) || 'pages/index/index'
	const options = (page && page.options) || {}
	const query = Object.keys(options)
		.map((key) => key + '=' + encodeURIComponent(options[key] == null ? '' : options[key]))
		.join('&')
	return {
		title: '天天俱乐部',
		path: '/' + route + (query ? '?' + query : ''),
		query
	}
}

const shareMixin = {
	onShow() {
		uni.showShareMenu({
			withShareTicket: true,
			menus: ['shareAppMessage', 'shareTimeline']
		})
	},
	onShareAppMessage() {
		const share = currentPageShare()
		return {
			title: share.title,
			path: share.path
		}
	},
	onShareTimeline() {
		const share = currentPageShare()
		return {
			title: share.title,
			query: share.query
		}
	}
}

// #ifndef VUE3
import Vue from 'vue'
import './uni.promisify.adaptor'
Vue.config.productionTip = false
Vue.mixin(shareMixin)
App.mpType = 'app'
const app = new Vue({
  ...App
})
app.$mount()
// #endif

// #ifdef VUE3
import { createSSRApp } from 'vue'
export function createApp() {
  const app = createSSRApp(App)
  app.mixin(shareMixin)
  return {
    app
  }
}
// #endif