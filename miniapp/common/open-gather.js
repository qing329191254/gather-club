/** 首页推荐位和去哪聚点进同一张页面：有门店详情进门店页，否则进商品下单页。 */
export function openGatherTarget(item) {
	if (!item) return false
	if (item.detailId) {
		uni.navigateTo({ url: '/pages/nye/detail?id=' + item.detailId })
		return true
	}
	if (item.id) {
		uni.navigateTo({ url: '/pages/gather/detail?id=' + item.id })
		return true
	}
	return false
}
