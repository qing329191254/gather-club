/**
 * 去哪聚分类与列表（后台可配置）
 * - tabs: 分类名可按客户业务改成菜品/套餐等，不绑定酒店旅游
 * - showSold: 该分类是否展示右上角「已购」文案
 * - 列表卡片字段统一，仅 soldText 有无影响布局差异
 */
export const gatherTabs = [
	{ key: 'day', name: '聚一天', showSold: true },
	{ key: 'meal', name: '聚个餐', showSold: true },
	{ key: 'dish', name: '招牌菜', showSold: false },
	{ key: 'set', name: '精品套餐', showSold: false }
]

export const gatherProducts = [
	// 聚一天
	{
		id: 'd1',
		tab: 'day',
		detailId: 'xinzhuang',
		cover: '/static/banners/nye.png',
		title: '上海莘庄店-天天俱乐部-2027年夜饭',
		tag: '年夜饭',
		soldText: '1人已购',
		price: 2688,
		originPrice: 3688
	},
	{
		id: 'd2',
		tab: 'day',
		detailId: 'xinzhuang',
		cover: '/static/stores/xinzhuang.png',
		title: '天天俱乐部-上海莘庄店（环球主题馆）',
		soldText: '1万+人已购',
		price: 899,
		originPrice: 1988
	},
	{
		id: 'd3',
		tab: 'day',
		detailId: 'yaxin',
		cover: '/static/banners/nye.png',
		title: '上海亚新店-天天俱乐部-2027年夜饭',
		tag: '年夜饭',
		soldText: '1人已购',
		price: 2688,
		originPrice: 3488
	},
	{
		id: 'd4',
		tab: 'day',
		detailId: 'yaxin',
		cover: '/static/stores/yaxin.png',
		title: '天天俱乐部上海亚新店（时光主题馆）',
		tags: ['地铁直', '沉浸体验', '全包房'],
		soldText: '1万+人已购',
		price: 899,
		originPrice: 1988
	},
	{
		id: 'd5',
		tab: 'day',
		detailId: 'gongkang',
		cover: '/static/banners/nye.png',
		title: '上海共康店-天天俱乐部-2027年夜饭',
		tag: '年夜饭',
		soldText: '1人已购',
		price: 2388,
		originPrice: 3488
	},
	{
		id: 'd6',
		tab: 'day',
		detailId: 'gongkang',
		cover: '/static/stores/gongkang.png',
		title: '天天俱乐部上海共康店（老上海情怀型）',
		tags: ['直营', '近地铁', '怀旧风'],
		soldText: '2万+人已购',
		price: 799,
		originPrice: 999
	},
	{
		id: 'd7',
		tab: 'day',
		cover: '/static/stores/ningbo.png',
		title: '宁波天天俱乐部（天一店）',
		tags: ['核心商圈', '地铁直达'],
		soldText: '4000+人已购',
		price: 828,
		originPrice: 1688
	},
	// 聚个餐 — 同布局，可带已购
	{
		id: 'm1',
		tab: 'meal',
		detailId: 'xinzhuang',
		cover: '/static/nye/xinzhuang.jpg',
		title: '莘庄店·帝王蟹海鲜盛宴（10人）',
		tag: '海鲜',
		soldText: '328人已购',
		price: 1888,
		originPrice: 2588
	},
	{
		id: 'm2',
		tab: 'meal',
		detailId: 'yaxin',
		cover: '/static/nye/yaxin.jpg',
		title: '亚新店·羊蝎子火锅双人餐',
		tags: ['招牌', '双人餐'],
		soldText: '1.2万+人已购',
		price: 198,
		originPrice: 298
	},
	{
		id: 'm3',
		tab: 'meal',
		detailId: 'gongkang',
		cover: '/static/nye/gongkang.jpg',
		title: '共康店·老上海本帮菜家宴',
		tag: '本帮菜',
		soldText: '860人已购',
		price: 688,
		originPrice: 988
	},
	{
		id: 'm4',
		tab: 'meal',
		detailId: 'shibo',
		cover: '/static/nye/shibo.jpg',
		title: '世博店·午市自助畅吃',
		tags: ['自助', '午市'],
		soldText: '5200+人已购',
		price: 168,
		originPrice: 228
	},
	// 招牌菜 — 同布局，不展示已购
	{
		id: 'c1',
		tab: 'dish',
		detailId: 'xinzhuang',
		cover: '/static/nye/detail/banner1.jpg',
		title: '招牌手撕盐焗鸡（整只）',
		tag: '招牌',
		price: 128,
		originPrice: 168
	},
	{
		id: 'c2',
		tab: 'dish',
		detailId: 'yaxin',
		cover: '/static/nye/detail/banner2.jpg',
		title: '黄油香煎小牛排',
		tags: ['人气', '西式'],
		price: 88,
		originPrice: 118
	},
	{
		id: 'c3',
		tab: 'dish',
		detailId: 'gongkang',
		cover: '/static/nye/detail/banner3.jpg',
		title: '红烧肉配糯米饭',
		tag: '本帮',
		price: 68,
		originPrice: 88
	},
	{
		id: 'c4',
		tab: 'dish',
		detailId: 'shibo',
		cover: '/static/nye/detail/content1.jpg',
		title: '蒜蓉粉丝蒸扇贝（6只）',
		tags: ['海鲜', '热销'],
		price: 98,
		originPrice: 128
	},
	// 精品套餐 — 同布局，不展示已购
	{
		id: 's1',
		tab: 'set',
		detailId: 'xinzhuang',
		cover: '/static/nye/xinzhuang.jpg',
		title: '喜气羊羊宴（10-12人）',
		tag: '套餐',
		price: 2688,
		originPrice: 3288
	},
	{
		id: 's2',
		tab: 'set',
		detailId: 'yaxin',
		cover: '/static/nye/yaxin.jpg',
		title: '团圆家宴（8-10人）',
		tags: ['包厢', '晚市'],
		price: 1988,
		originPrice: 2588
	},
	{
		id: 's3',
		tab: 'set',
		detailId: 'gongkang',
		cover: '/static/nye/gongkang.jpg',
		title: '名羊四海宴（12-14人）',
		tag: '套餐',
		price: 3588,
		originPrice: 4288
	},
	{
		id: 's4',
		tab: 'set',
		detailId: 'shibo',
		cover: '/static/nye/shibo.jpg',
		title: '商务午宴精选套餐（6人）',
		tags: ['午市', '商务'],
		price: 1288,
		originPrice: 1688
	}
]
