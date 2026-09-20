const stores = {
	gongkang: {
		id: 'gongkang',
		name: '上海共康店-天天俱乐部-2027年夜饭',
		cover: '/static/nye/gongkang.jpg',
		price: 2388,
		tag: '年夜饭',
		address: '共和新路5000弄绿地新都会1号楼二楼',
		route: '地铁1号线共康路站下4号口出往北直行过共康路约200米，甬粤江南隔壁大门进2楼',
		lat: 31.3208,
		lng: 121.4476,
		banners: [
			'/static/nye/detail/banner1.jpg',
			'/static/nye/detail/banner2.jpg',
			'/static/nye/detail/banner3.jpg'
		],
		// 后台可配置的详情长图列表
		detailImages: [
			'/static/nye/detail/content1.jpg',
			'/static/nye/detail/content2.jpg',
			'/static/nye/detail/content3.jpg'
		],
		recentBuy: {
			countText: '近一周1人买过',
			avatar: '/static/icons/avatar-default.png',
			name: '阿********)',
			timeText: '22小时前买了1件'
		}
	},
	shibo: {
		id: 'shibo',
		name: '上海世博店-天天俱乐部-2027年夜饭',
		cover: '/static/nye/shibo.jpg',
		price: 2688,
		tag: '年夜饭',
		address: '浦东新区长清路92号中邻上钢里3楼',
		route: '地铁长清路站7号线2号出口，13号线7号出口，步行进入中邻上钢里商场内3楼',
		lat: 31.1846,
		lng: 121.4852,
		banners: [
			'/static/nye/detail/banner2.jpg',
			'/static/nye/detail/banner1.jpg',
			'/static/nye/detail/banner3.jpg'
		],
		detailImages: [
			'/static/nye/detail/content1.jpg',
			'/static/nye/detail/content2.jpg',
			'/static/nye/detail/content3.jpg'
		],
		recentBuy: {
			countText: '近一周3人买过',
			avatar: '/static/icons/avatar-default.png',
			name: '小********)',
			timeText: '5小时前买了1件'
		}
	},
	yaxin: {
		id: 'yaxin',
		name: '上海亚新店-天天俱乐部-2027年夜饭',
		cover: '/static/nye/yaxin.jpg',
		price: 2688,
		originPrice: 3488,
		tag: '年夜饭',
		address: '普陀区长寿路401号3号楼2楼',
		route: '地铁7、13号线长寿路站7号口出来左转步行50米进入亚新广场内',
		lat: 31.2432,
		lng: 121.4374,
		banners: [
			'/static/nye/detail/banner3.jpg',
			'/static/nye/detail/banner1.jpg',
			'/static/nye/detail/banner2.jpg'
		],
		detailImages: [
			'/static/nye/detail/content1.jpg',
			'/static/nye/detail/content2.jpg',
			'/static/nye/detail/content3.jpg'
		],
		recentBuy: {
			countText: '近一周2人买过',
			avatar: '/static/icons/avatar-default.png',
			name: '李********)',
			timeText: '1天前买了1件'
		}
	},
	xinzhuang: {
		id: 'xinzhuang',
		name: '上海莘庄店-天天俱乐部-2027年夜饭',
		cover: '/static/nye/xinzhuang.jpg',
		price: 2688,
		originPrice: 3688,
		tag: '年夜饭',
		address: '闵行区都市路5001号5楼',
		route: '地铁1/5号线莘庄站南1口出，步行约600米至莘庄仲盛世界商城5楼',
		lat: 31.1134,
		lng: 121.3851,
		banners: [
			'/static/nye/detail/banner1.jpg',
			'/static/nye/detail/banner3.jpg',
			'/static/nye/detail/banner2.jpg'
		],
		detailImages: [
			'/static/nye/detail/content1.jpg',
			'/static/nye/detail/content2.jpg',
			'/static/nye/detail/content3.jpg'
		],
		recentBuy: {
			countText: '近一周5人买过',
			avatar: '/static/icons/avatar-default.png',
			name: '王********)',
			timeText: '3小时前买了2件'
		}
	}
}

export const nyeList = Object.values(stores).map((item) => ({
	id: item.id,
	name: item.name,
	cover: item.cover,
	price: item.price,
	originPrice: item.originPrice
}))

export function findNyeDetail(id) {
	return stores[id] || stores.gongkang
}

export function isNyeOpenDate(key) {
	return key >= '2027-02-05' && key <= '2027-02-12'
}

export function nyePackages(detail) {
	const price = (detail && detail.price) || 2388
	const cover = (detail && detail.cover) || '/static/nye/gongkang.jpg'
	return [
		{ id: 1, name: '喜气羊羊宴 (10-12人) 午市大厅', meal: '喜气羊羊宴', time: '10:00-14:00', price, people: 12, cover, disabled: false },
		{ id: 2, name: '喜气羊羊宴 (10-12人) 晚市大厅', meal: '喜气羊羊宴', time: '17:00-21:00', price: price + 200, people: 12, cover, disabled: false },
		{ id: 3, name: '喜气羊羊宴 (8-10人) 午市包厢', meal: '喜气羊羊宴', time: '10:00-14:00', price: price + 300, people: 10, cover: '/static/nye/shibo.jpg', disabled: false },
		{ id: 4, name: '团圆家宴 (8-10人) 晚市大厅', meal: '团圆家宴', time: '17:00-21:00', price: price + 100, people: 10, cover: '/static/nye/yaxin.jpg', disabled: false },
		{ id: 5, name: '团圆家宴 (6-8人) 午市包厢', meal: '团圆家宴', time: '10:00-14:00', price: price - 400, people: 8, cover: '/static/nye/yaxin.jpg', disabled: false },
		{ id: 6, name: '名羊四海宴 (12-14人) 午市大厅', meal: '名羊四海宴', time: '10:00-14:00', price: price + 1100, people: 14, cover: '/static/nye/xinzhuang.jpg', disabled: false },
		{ id: 7, name: '名羊四海宴 (16人) 晚市大厅', meal: '名羊四海宴', time: '17:00-21:00', price: price + 2100, people: 16, cover: '/static/nye/xinzhuang.jpg', disabled: true },
		{ id: 8, name: '名羊四海宴 (16人) 晚市包厢', meal: '名羊四海宴', time: '17:00-21:00', price: price + 2100, people: 16, cover: '/static/nye/xinzhuang.jpg', disabled: true }
	]
}
