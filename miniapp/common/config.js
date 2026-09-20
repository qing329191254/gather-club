/** 微信云托管配置 */
export const CLOUD_ENV = 'prod-d7gemg7fe0004adc9'
export const CLOUD_SERVICE = 'gather-api'
/** 对象存储 CDN（与云托管「存储配置」一致） */
export const COS_CDN =
	'https://7072-prod-d7gemg7fe0004adc9-1492244999.tcb.qcloud.la'

/**
 * 开发/调试兜底：callContainer 不可用时走公网域名。
 * 真机正式环境应优先 callContainer，公网仅作测试。
 */
export const PUBLIC_BASE =
	'https://gather-api-316910-10-1492244999.sh.run.tcloudbase.com'
