/** 去哪聚每张卡是独立商品；打开对应商品详情（套餐/轮播/销量各自独立）。 */
export function openGatherTarget(item) {
	if (!item) return false
	const id = item.id || item.detailId || item.detail_id || ''
	if (id) {
		uni.navigateTo({ url: '/pages/nye/detail?id=' + id })
		return true
	}
	uni.showToast({ title: '门店暂未开放预约', icon: 'none' })
	return false
}
