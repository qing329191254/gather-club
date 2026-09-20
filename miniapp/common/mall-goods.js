export const mallPoints = 12

export const mallRules = [
	'兑换成功后，可在「我的-积分商城-兑换记录」中查看已兑换商品及核销码。',
	'适用门店：天天俱乐部上海共康店、亚新生活广场、上海莘庄店、上钢新邻里3楼。',
	'仅限到店当日消费使用，每件商品每日限兑5份，请至前台核销。',
	'如遇缺货，可更换等值商品或退还相应积分。',
	'仅限本人使用，不可转让、不可截图核销；如发现异常兑换，平台有权取消相关权益。'
]

const usage = '适用于天天俱乐部上海共康店、亚新生活广场、上海莘庄店、上钢新邻里3楼，凭兑换码到店使用。'
const valid = '领取后立即生效，有效期30天。'

function goods(item) {
	return {
		usage,
		valid,
		title: item.name,
		...item
	}
}

export const mallGoods = [
	goods({ id: 1, name: '鱼缸投币挑战 (3次)', title: '鱼缸投币挑战 (3枚祈福币)', cover: '/static/mall/tank.png', cost: 300 }),
	goods({ id: 2, name: '百事可乐一瓶1.25L', cover: '/static/mall/pepsi.png', cost: 500 }),
	goods({ id: 3, name: '雪碧一瓶1.25L', cover: '/static/mall/sprite.png', cost: 500 }),
	goods({ id: 4, name: '美汁源果粒橙一瓶1.25L', cover: '/static/mall/minute.png', cost: 500 }),
	goods({ id: 5, name: '光明啤酒', cover: '/static/mall/beer.png', cost: 800 }),
	goods({ id: 6, name: '鱼林扑克', cover: '/static/mall/poker.png', cost: 200 }),
	goods({ id: 7, name: '葱烤海参烩鱼肚1份', cover: '/static/mall/haishen.png', cost: 2500 }),
	goods({ id: 8, name: '壹聚黄酒（8年纯酿）', cover: '/static/mall/wine.png', cost: 3000 }),
	goods({ id: 9, name: '麻将桌券1份', cover: '/static/mall/mahjong.png', cost: 3000 }),
	goods({ id: 10, name: '鲍鱼炒年糕1份', cover: '/static/mall/abalone.png', cost: 2500 }),
	goods({ id: 11, name: '蜂蜜小烤肉1份', cover: '/static/mall/meat.png', cost: 2000 })
]

export function findMallGoods(id) {
	return mallGoods.find((item) => String(item.id) === String(id)) || null
}
