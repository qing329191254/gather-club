/** 支付结果处理：needPay 时调起微信支付，否则视为已模拟支付成功。 */

export function settlePay(payRes) {
	if (!payRes || !payRes.needPay || !payRes.payment) {
		return Promise.resolve(payRes)
	}
	const p = payRes.payment
	return new Promise((resolve, reject) => {
		uni.requestPayment({
			provider: 'wxpay',
			timeStamp: String(p.timeStamp),
			nonceStr: p.nonceStr,
			package: p.package,
			signType: p.signType || 'MD5',
			paySign: p.paySign,
			success: () => resolve(payRes),
			fail: (err) => {
				const msg = (err && err.errMsg) || ''
				const cancelled = /cancel/i.test(msg)
				const error = new Error(cancelled ? '已取消支付' : '支付失败')
				error.cancelled = cancelled
				reject(error)
			}
		})
	})
}
