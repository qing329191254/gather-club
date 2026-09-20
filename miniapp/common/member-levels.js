/** 会员中心等级与权益（含切换主题：背景图 / 配色） */

const I = {
	coupon: '/static/icons/benefit/coupon.png',
	steward: '/static/icons/benefit/steward.png',
	birthday: '/static/icons/benefit/birthday.png',
	gift: '/static/icons/benefit/gift.png',
	seat: '/static/icons/benefit/seat.png',
	room: '/static/icons/benefit/room.png',
	store: '/static/icons/benefit/store.png',
	waiver: '/static/icons/benefit/waiver.png'
}

export const memberLevels = [
	{
		id: 'V0',
		theme: 'silver',
		pageBg: '#0b1423',
		pageBgImage: '/static/member/bg-v0.jpg',
		cardBgImage: '/static/member/card-v0.jpg',
		levelColor: '#2f4578',
		needColor: 'rgba(40, 55, 95, 0.78)',
		barColor: '#7b6bb8',
		accent: '#9eb6d8',
		navFront: '#ffffff',
		navBg: '#0b1423',
		benefitBg: 'linear-gradient(180deg, #1a2438 0%, #0e1524 100%)',
		benefitBorder: 'rgba(158, 182, 216, 0.18)',
		couponBg: 'linear-gradient(180deg, #152038 0%, #0f1830 100%)',
		couponBorder: 'rgba(158, 182, 216, 0.16)',
		couponDeco: 'rgba(100, 140, 200, 0.22)',
		secLine: 'rgba(158, 182, 216, 0.75)',
		crownIcon: '/static/icons/vip-style-v0.png',
		need: 0,
		needText: '有效期至：2027-08-17',
		progressLabel: '当前已达标',
		doneText: true,
		benefits: [
			{ title: '会员券包', desc: '菜品酒水任领', icon: I.coupon },
			{ title: '管家服务', desc: '大众管家', icon: I.steward }
		]
	},
	{
		id: 'V1',
		theme: 'blue',
		pageBg: '#081830',
		pageBgImage: '/static/member/bg-v1.jpg',
		cardBgImage: '/static/member/card-v1.jpg',
		levelColor: '#1f5cb0',
		needColor: 'rgba(30, 60, 110, 0.8)',
		barColor: '#3d7de0',
		accent: '#7eb3f0',
		navFront: '#ffffff',
		navBg: '#081830',
		benefitBg: 'linear-gradient(180deg, #132844 0%, #0a1628 100%)',
		benefitBorder: 'rgba(126, 179, 240, 0.2)',
		couponBg: 'linear-gradient(180deg, #12304c 0%, #0c1c34 100%)',
		couponBorder: 'rgba(126, 179, 240, 0.18)',
		couponDeco: 'rgba(80, 150, 230, 0.24)',
		secLine: 'rgba(126, 179, 240, 0.8)',
		crownIcon: '/static/icons/vip-style-v1.png',
		need: 1,
		needText: '有效期内完成1桌可升级',
		progressLabel: '升级进度',
		doneText: false,
		benefits: [
			{ title: '会员券包', desc: '菜品酒水任领', icon: I.coupon },
			{ title: '管家服务', desc: '银牌管家', icon: I.steward },
			{ title: '生日尊享', desc: '特色生日面', icon: I.birthday }
		]
	},
	{
		id: 'V2',
		theme: 'violet',
		pageBg: '#120e1c',
		pageBgImage: '/static/member/bg-v2.jpg',
		cardBgImage: '/static/member/card-v2.jpg',
		levelColor: '#5a3588',
		needColor: 'rgba(70, 45, 110, 0.8)',
		barColor: '#8a5cc8',
		accent: '#c4a6e8',
		navFront: '#ffffff',
		navBg: '#120e1c',
		benefitBg: 'linear-gradient(180deg, #241830 0%, #140e1c 100%)',
		benefitBorder: 'rgba(196, 166, 232, 0.2)',
		couponBg: 'linear-gradient(180deg, #261a38 0%, #161022 100%)',
		couponBorder: 'rgba(196, 166, 232, 0.18)',
		couponDeco: 'rgba(150, 100, 210, 0.24)',
		secLine: 'rgba(196, 166, 232, 0.8)',
		crownIcon: '/static/icons/vip-style-v2.png',
		need: 2,
		needText: '有效期内完成2桌可升级',
		progressLabel: '升级进度',
		doneText: false,
		benefits: [
			{ title: '会员券包', desc: '菜品酒水任领', icon: I.coupon },
			{ title: '管家服务', desc: '银牌管家', icon: I.steward },
			{ title: '生日尊享', desc: '特色生日面/当月出行2倍积分', icon: I.birthday },
			{ title: '送红酒加大菜', desc: '出行日每桌送1瓶红酒', icon: I.gift },
			{ title: '包房升级券', desc: '工作日可用，3张/年', icon: I.room },
			{ title: '门店礼遇', desc: '精修合照/欢迎语制作', icon: I.store }
		]
	},
	{
		id: 'V3',
		theme: 'gold',
		pageBg: '#1a120c',
		pageBgImage: '/static/member/bg-v3.jpg',
		cardBgImage: '/static/member/card-v3.jpg',
		levelColor: '#6b4a1e',
		needColor: 'rgba(90, 60, 25, 0.82)',
		barColor: '#c49a3c',
		accent: '#e0c080',
		navFront: '#ffffff',
		navBg: '#1a120c',
		benefitBg: 'linear-gradient(180deg, #2a1c14 0%, #16100c 100%)',
		benefitBorder: 'rgba(212, 175, 120, 0.28)',
		couponBg: 'linear-gradient(180deg, #2a1e14 0%, #18120c 100%)',
		couponBorder: 'rgba(212, 175, 120, 0.22)',
		couponDeco: 'rgba(200, 150, 80, 0.22)',
		secLine: 'rgba(212, 175, 120, 0.9)',
		crownIcon: '/static/icons/vip-style-v3.png',
		need: 5,
		needText: '有效期内完成5桌可升级',
		progressLabel: '升级进度',
		doneText: false,
		benefits: [
			{ title: '会员券包', desc: '菜品酒水任领', icon: I.coupon },
			{ title: '管家服务', desc: '金牌管家1V1服务', icon: I.steward },
			{ title: '生日尊享', desc: '特色生日面/当月出行2倍积分', icon: I.birthday },
			{ title: '送红酒加大菜', desc: '出行日每桌送1瓶红酒+1道大菜', icon: I.gift },
			{ title: '优选位置', desc: '指定包房/桌位优先', icon: I.seat },
			{ title: '包房升级券', desc: '工作日可用，6张/年', icon: I.room },
			{ title: '门店礼遇', desc: '精修合照/欢迎语制作', icon: I.store },
			{ title: '扣损减免', desc: '每年3桌扣损减免', icon: I.waiver }
		]
	}
]

export const monthCoupon = {
	title: '红酒20元立减券',
	tip: '前台核销使用',
	tag: '红酒\n立减\n20元券'
}
