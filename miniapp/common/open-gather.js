/** 去哪聚入口一律进宴会专题详情（封面/店名/套餐价在专题配置）。 */
export function openGatherTarget(item) {
	if (!item) return false
	const detailId = item.detailId || item.detail_id || ''
	if (detailId) {
		uni.navigateTo({ url: '/pages/nye/detail?id=' + detailId })
		return true
	}
	uni.showToast({ title: '门店暂未开放预约', icon: 'none' })
	return false
}
