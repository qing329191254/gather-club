"""CMS seed payloads for SiteConfig keys (agreements / privacy / member)."""

from __future__ import annotations

AGREEMENTS = {
    "cancel": {
        "navTitle": "注销账号协议",
        "title": "小程序账号注销协议",
        "intro": (
            "尊敬的用户：\n"
            "在您申请注销天天俱乐部小程序账号前，请充分阅读、理解并同意本协议全部内容。"
            "您点击确认或继续办理注销，即视为已阅读并接受本协议。"
        ),
        "blocks": [
            {
                "heading": "一、账号注销后果",
                "paras": [
                    "账号注销为不可撤销操作。注销完成后，您将无法再使用该账号登录或使用本小程序相关服务，亦无法找回该账号下的全部内容、权益与数据。"
                ],
                "subs": [
                    {
                        "title": "1.1 信息清除与作废",
                        "paras": [
                            "注销后，系统将对该账号相关信息进行清除或作废处理，包括但不限于：",
                            "① 账号信息（如昵称、头像等）；",
                            "② 优惠券、折扣券、礼品卡等未使用或未核销的权益凭证；",
                            "③ 个人资料及业务数据（如身份信息、浏览/收藏记录、订单记录、收货地址等）。",
                        ],
                    },
                    {
                        "title": "1.2 财产性利益放弃（特别声明）",
                        "paras": [
                            "您理解并同意：申请注销即视为您自愿放弃该账号项下全部财产性利益及相关权益主张，包括但不限于未使用的优惠券、积分、未完成订单项下的权益等，平台不再另行补偿。"
                        ],
                    },
                    {
                        "title": "1.3 数据不可恢复",
                        "paras": [
                            "即使您后续使用同一手机号或其他方式重新注册，亦无法恢复原账号数据、记录及权益。"
                        ],
                    },
                ],
            },
            {
                "heading": "二、注销限制与冷却期",
                "subs": [
                    {
                        "title": "2.1 防范滥用机制",
                        "paras": [
                            "为保障系统安全、防范恶意注册与滥用，账号注销后，同一手机号可能在一定时间内无法再次注册新账号。具体间隔以系统当时规则为准。"
                        ],
                    },
                    {
                        "title": "2.2 例外情况",
                        "paras": [
                            "因违反法律法规、平台规则被封禁或限制的账号，可能不被允许重新注册或恢复使用。"
                        ],
                    },
                ],
            },
            {
                "heading": "三、注销条件",
                "paras": [
                    "申请注销前，您的账号应同时满足以下条件：",
                    "1. 账号处于安全状态（非被盗、非被限制/封禁等异常状态）；",
                    "2. 不存在进行中的交易、待核销订单或售后处理；",
                    "3. 不存在未结清的费用、欠款或其他应付义务；",
                    "4. 不存在尚未处理完毕的投诉、争议或举报；",
                    "5. 您已自行备份需保留的全部信息与凭证。",
                ],
            },
            {
                "heading": "四、注销流程",
                "subs": [
                    {
                        "title": "4.1 申请途径",
                        "paras": [
                            "您可通过以下方式提交注销申请：",
                            "① 客服热线：400-920-9400（服务时间：9:00-18:00）；",
                            "② 线下门店：上海市普陀区普罗娜商务广场B幢1楼。",
                        ],
                    },
                    {
                        "title": "4.2 审核周期",
                        "paras": [
                            "我们将在收到符合条件的申请后进行核验，并在 7 个工作日内完成注销处理。如需补充材料，处理时限自材料补齐之日起重新计算。"
                        ],
                    },
                ],
            },
            {
                "heading": "五、法律责任",
                "subs": [
                    {
                        "title": "5.1 用户承诺",
                        "paras": [
                            "您承诺：已妥善处理账号相关交易与权益；已解除或知晓与微信、支付宝、银行卡等第三方绑定关系的影响；已充分理解注销后果，并自愿申请注销。"
                        ],
                    },
                    {
                        "title": "5.2 平台责任",
                        "paras": [
                            "因您未按本协议妥善处理相关事项，或因不可抗力、系统故障等原因导致注销延迟或失败的，平台在法律允许范围内不承担相应责任；法律法规另有规定的除外。"
                        ],
                    },
                ],
            },
            {
                "heading": "六、法律适用与争议解决",
                "paras": [
                    "本协议适用中华人民共和国法律（不含冲突法）。因本协议引起的或与本协议有关的争议，双方应友好协商解决；协商不成的，提交平台运营主体所在地有管辖权的人民法院诉讼解决。"
                ],
            },
            {
                "heading": "七、其他",
                "paras": [
                    "1. 我们可能根据业务与合规需要修订本协议，修订后将通过小程序页面等方式公示。您继续申请注销即视为接受修订内容。",
                    "2. 本协议任一条款被认定无效或不可执行的，不影响其余条款效力。",
                    "3. 如有疑问，请拨打客服热线：400-920-9400。",
                ],
            },
        ],
        "confirm": (
            "【最终确认声明】本人已仔细阅读并充分理解本协议全部内容，特别是关于信息清除与作废、"
            "财产性利益放弃、数据不可恢复等条款，确认自愿申请账号注销，并接受由此产生的全部后果。"
        ),
    },
    "privacy": {
        "navTitle": "用户隐私协议",
        "title": "天天俱乐部用户隐私协议",
        "intro": (
            "尊敬的用户：\n"
            "天天俱乐部（以下简称“我们”）深知个人信息对您的重要性，并会尽全力保护您的个人信息安全。"
            "请您在使用本小程序服务前，仔细阅读并充分理解本协议。您使用或继续使用我们的服务，即表示您同意我们按照本协议处理您的相关信息。"
        ),
        "blocks": [
            {
                "heading": "一、我们如何收集和使用个人信息",
                "paras": [
                    "我们仅会出于本协议所述目的，收集和使用您的个人信息。若我们要将信息用于本协议未载明的其他用途，会事先征得您的同意。"
                ],
                "subs": [
                    {
                        "title": "1.1 账号与身份相关信息",
                        "paras": [
                            "当您登录、完善资料时，我们可能收集：微信授权的昵称、头像、OpenID/UnionID 等标识信息；您主动填写的手机号、收货人姓名、收货地址等。"
                        ],
                    },
                    {
                        "title": "1.2 业务功能所需信息",
                        "paras": [
                            "为向您提供门店预约、积分签到、积分商城兑换、优惠券、订单管理、活动报名/预约直播等服务，我们可能收集：订单信息、兑换记录、积分变动记录、优惠券使用记录、预约/签到记录、收货地址等。"
                        ],
                    },
                    {
                        "title": "1.3 设备与日志信息",
                        "paras": [
                            "为保障服务安全与稳定运行，我们可能收集设备型号、操作系统、网络类型、唯一设备标识（在法律允许范围内）、操作日志、崩溃日志等。"
                        ],
                    },
                    {
                        "title": "1.4 位置与相机等权限",
                        "paras": [
                            "当您使用门店导航、扫码核销、上传图片等功能时，经您授权后，我们可能调用位置、相机、相册等系统权限。您可在系统设置中关闭权限；关闭后部分功能可能无法使用，但不影响浏览等基础功能。"
                        ],
                    },
                ],
            },
            {
                "heading": "二、我们如何使用 Cookie 与同类技术",
                "paras": [
                    "我们可能使用本地存储、缓存等同类技术，用于维持登录状态、记住偏好、提升访问体验及统计分析。您可通过清除缓存等方式管理相关数据。"
                ],
            },
            {
                "heading": "三、我们如何共享、转让、公开披露个人信息",
                "subs": [
                    {
                        "title": "3.1 共享",
                        "paras": [
                            "我们不会与第三方共享您的个人信息，但以下情形除外：",
                            "① 获得您的明确同意；",
                            "② 根据法律法规或行政、司法机关的要求；",
                            "③ 为完成支付、物流、短信通知等必要服务，在最小必要范围内向受托方提供，并要求其依法保护信息；",
                            "④ 与关联方在必要范围内共享，用于统一账号体验或风控安全。",
                        ],
                    },
                    {
                        "title": "3.2 转让",
                        "paras": [
                            "我们不会将您的个人信息转让给任何公司、组织或个人，但在涉及合并、收购、资产转让等情形且需要转移时，我们将要求新的持有方继续受本协议约束，否则将重新征得您的授权同意。"
                        ],
                    },
                    {
                        "title": "3.3 公开披露",
                        "paras": [
                            "我们仅会在获得您明确同意，或基于法律法规规定必须披露的情形下，公开披露您的个人信息。"
                        ],
                    },
                ],
            },
            {
                "heading": "四、我们如何存储和保护个人信息",
                "paras": [
                    "1. 我们在中华人民共和国境内存储您的个人信息。如需跨境传输，将另行征得您的同意并履行法定程序。",
                    "2. 我们采用合理的安全措施（如访问控制、传输加密、权限管理等）防止信息遭到未经授权的访问、披露、使用、修改、损坏或丢失。",
                    "3. 如发生个人信息安全事件，我们将按法律法规要求及时告知您，并向主管部门报告。",
                ],
            },
            {
                "heading": "五、您如何管理个人信息",
                "paras": [
                    "您有权访问、更正、删除您的个人信息，以及撤回授权、注销账号等，具体可通过小程序内「我的」相关功能，或联系客服办理。",
                    "账号注销的条件、流程与后果，请另行参阅《小程序账号注销协议》。",
                    "在响应您的请求前，我们可能需要验证您的身份，并在法律法规规定的期限内处理。",
                ],
            },
            {
                "heading": "六、未成年人保护",
                "paras": [
                    "我们的服务主要面向成年人。若您为未成年人，请在监护人指导下阅读本协议，并在取得监护人同意后使用我们的服务。我们仅在法律允许、监护人同意或保护未成年人所必要的情况下处理相关个人信息。"
                ],
            },
            {
                "heading": "七、本协议的更新",
                "paras": [
                    "我们可能适时修订本协议。更新后，我们会在小程序内以页面提示、公告等方式公布。若更新涉及重大权益变化，我们将按法规要求再次征得您的同意。"
                ],
            },
            {
                "heading": "八、联系我们",
                "paras": [
                    "如您对本协议或个人信息保护有任何疑问、意见或投诉，可通过以下方式联系我们：",
                    "客服热线：4001919179（服务时间：9:00-18:00）；",
                    "或通过小程序内「联系客服 / 联系管家」与我们取得联系。",
                    "我们将在核实身份后尽快回复。",
                ],
            },
        ],
        "confirm": (
            "【确认声明】本人已仔细阅读并充分理解《天天俱乐部用户隐私协议》全部内容，"
            "知悉个人信息的收集、使用、共享与保护规则，并同意按本协议处理相关信息。"
        ),
    },
}

PRIVACY_COLLECT = {
    "intro": (
        "《天天俱乐部》小程序尊重并保护您的隐私，并将依照适用法律的要求在处理个人信息过程中采取必要的保护措施以保证您个人信息的安全性。"
        "为了向您提供本小程序的基本功能以及附加功能，我们需要收集您的个人信息，或者申请打开您设备的特定权限。"
        "以下我们将逐一说明您个人信息的收集情况，以便您快速查阅。"
    ),
    "sections": [
        {
            "title": "账号注册与登录",
            "content": "微信头像、昵称、手机号、性别",
            "purpose": "创建账户，个人主页信息展示，完善网络身份标识",
            "scene": "用户主动填写或授权微信头像昵称手机号",
        },
        {
            "title": "位置信息",
            "content": "模糊地址位置",
            "purpose": "展示自提商品附近门店信息",
            "scene": "下单",
        },
        {
            "title": "下单与订单管理",
            "content": "包括姓名、收货地址、订单信息明细",
            "purpose": "创建订单，历史交易信息展示与查询",
            "scene": "下单与订单查询",
        },
        {
            "title": "设备信息",
            "content": "操作系统版本、型号、设备标识符",
            "purpose": "适配当前设备；保障账户安全；保障安全交易；分析与统计",
            "scene": "进入小程序时",
        },
    ],
}

PRIVACY_SHARE = {
    "intro": (
        "《天天俱乐部》小程序可能在向您提供服务的过程中，委托或与第三方共享必要的个人信息。"
        "我们仅会出于合法、正当、必要、特定的目的共享信息，并要求接收方按照法律法规与约定保护您的信息。"
        "以下为当前涉及的第三方共享情况，便于您查阅。"
    ),
    "sections": [
        {
            "title": "微信支付",
            "name": "财付通支付科技有限公司",
            "info": "订单金额、订单号、支付状态等支付必要信息",
            "purpose": "完成在线支付、退款及对账",
            "scene": "用户下单支付、申请退款时",
            "method": "接口调用（SDK / 服务端）",
        },
        {
            "title": "微信登录与开放能力",
            "name": "深圳市腾讯计算机系统有限公司",
            "info": "微信昵称、头像、OpenID/UnionID 等授权标识",
            "purpose": "账号登录、身份识别与服务触达",
            "scene": "用户授权登录或使用微信相关能力时",
            "method": "接口调用（微信开放平台）",
        },
        {
            "title": "地图与定位服务",
            "name": "腾讯科技（深圳）有限公司（腾讯位置服务）",
            "info": "模糊位置信息、门店坐标相关信息",
            "purpose": "展示附近门店、路线导航与到店指引",
            "scene": "用户查看门店、发起导航或下单自提时",
            "method": "接口调用（地图 / 定位 SDK）",
        },
        {
            "title": "短信通知服务",
            "name": "第三方短信服务商（以实际合作方为准）",
            "info": "手机号码、短信模板相关业务变量",
            "purpose": "发送验证码、订单/预约等业务通知",
            "scene": "需要短信验证或业务提醒时",
            "method": "接口调用（服务端）",
        },
    ],
}

MEMBER_LEVELS = [
    {
        "id": "V0",
        "theme": "silver",
        "pageBg": "#0b1423",
        "pageBgImage": "/static/member/bg-v0.jpg",
        "cardBgImage": "/static/member/card-v0.jpg",
        "levelColor": "#2f4578",
        "needColor": "rgba(40, 55, 95, 0.78)",
        "barColor": "#7b6bb8",
        "accent": "#9eb6d8",
        "navFront": "#ffffff",
        "navBg": "#0b1423",
        "benefitBg": "linear-gradient(180deg, #1a2438 0%, #0e1524 100%)",
        "benefitBorder": "rgba(158, 182, 216, 0.18)",
        "couponBg": "linear-gradient(180deg, #152038 0%, #0f1830 100%)",
        "couponBorder": "rgba(158, 182, 216, 0.16)",
        "couponDeco": "rgba(100, 140, 200, 0.22)",
        "secLine": "rgba(158, 182, 216, 0.75)",
        "crownIcon": "/static/icons/vip-style-v0.png",
        "need": 0,
        "needText": "有效期至：2027-08-17",
        "progressLabel": "当前已达标",
        "doneText": True,
        "benefits": [
            {"title": "会员券包", "desc": "菜品酒水任领", "icon": "/static/icons/benefit/coupon.png"},
            {"title": "管家服务", "desc": "大众管家", "icon": "/static/icons/benefit/steward.png"},
        ],
    },
    {
        "id": "V1",
        "theme": "blue",
        "pageBg": "#081830",
        "pageBgImage": "/static/member/bg-v1.jpg",
        "cardBgImage": "/static/member/card-v1.jpg",
        "levelColor": "#1f5cb0",
        "needColor": "rgba(30, 60, 110, 0.8)",
        "barColor": "#3d7de0",
        "accent": "#7eb3f0",
        "navFront": "#ffffff",
        "navBg": "#081830",
        "benefitBg": "linear-gradient(180deg, #132844 0%, #0a1628 100%)",
        "benefitBorder": "rgba(126, 179, 240, 0.2)",
        "couponBg": "linear-gradient(180deg, #12304c 0%, #0c1c34 100%)",
        "couponBorder": "rgba(126, 179, 240, 0.18)",
        "couponDeco": "rgba(80, 150, 230, 0.24)",
        "secLine": "rgba(126, 179, 240, 0.8)",
        "crownIcon": "/static/icons/vip-style-v1.png",
        "need": 1,
        "needText": "有效期内完成1桌可升级",
        "progressLabel": "升级进度",
        "doneText": False,
        "benefits": [
            {"title": "会员券包", "desc": "菜品酒水任领", "icon": "/static/icons/benefit/coupon.png"},
            {"title": "管家服务", "desc": "银牌管家", "icon": "/static/icons/benefit/steward.png"},
            {"title": "生日尊享", "desc": "特色生日面", "icon": "/static/icons/benefit/birthday.png"},
        ],
    },
    {
        "id": "V2",
        "theme": "violet",
        "pageBg": "#120e1c",
        "pageBgImage": "/static/member/bg-v2.jpg",
        "cardBgImage": "/static/member/card-v2.jpg",
        "levelColor": "#5a3588",
        "needColor": "rgba(70, 45, 110, 0.8)",
        "barColor": "#8a5cc8",
        "accent": "#c4a6e8",
        "navFront": "#ffffff",
        "navBg": "#120e1c",
        "benefitBg": "linear-gradient(180deg, #241830 0%, #140e1c 100%)",
        "benefitBorder": "rgba(196, 166, 232, 0.2)",
        "couponBg": "linear-gradient(180deg, #261a38 0%, #161022 100%)",
        "couponBorder": "rgba(196, 166, 232, 0.18)",
        "couponDeco": "rgba(150, 100, 210, 0.24)",
        "secLine": "rgba(196, 166, 232, 0.8)",
        "crownIcon": "/static/icons/vip-style-v2.png",
        "need": 2,
        "needText": "有效期内完成2桌可升级",
        "progressLabel": "升级进度",
        "doneText": False,
        "benefits": [
            {"title": "会员券包", "desc": "菜品酒水任领", "icon": "/static/icons/benefit/coupon.png"},
            {"title": "管家服务", "desc": "银牌管家", "icon": "/static/icons/benefit/steward.png"},
            {"title": "生日尊享", "desc": "特色生日面/当月出行2倍积分", "icon": "/static/icons/benefit/birthday.png"},
            {"title": "送红酒加大菜", "desc": "出行日每桌送1瓶红酒", "icon": "/static/icons/benefit/gift.png"},
            {"title": "包房升级券", "desc": "工作日可用，3张/年", "icon": "/static/icons/benefit/room.png"},
            {"title": "门店礼遇", "desc": "精修合照/欢迎语制作", "icon": "/static/icons/benefit/store.png"},
        ],
    },
    {
        "id": "V3",
        "theme": "gold",
        "pageBg": "#1a120c",
        "pageBgImage": "/static/member/bg-v3.jpg",
        "cardBgImage": "/static/member/card-v3.jpg",
        "levelColor": "#6b4a1e",
        "needColor": "rgba(90, 60, 25, 0.82)",
        "barColor": "#c49a3c",
        "accent": "#e0c080",
        "navFront": "#ffffff",
        "navBg": "#1a120c",
        "benefitBg": "linear-gradient(180deg, #2a1c14 0%, #16100c 100%)",
        "benefitBorder": "rgba(212, 175, 120, 0.28)",
        "couponBg": "linear-gradient(180deg, #2a1e14 0%, #18120c 100%)",
        "couponBorder": "rgba(212, 175, 120, 0.22)",
        "couponDeco": "rgba(200, 150, 80, 0.22)",
        "secLine": "rgba(212, 175, 120, 0.9)",
        "crownIcon": "/static/icons/vip-style-v3.png",
        "need": 5,
        "needText": "有效期内完成5桌可升级",
        "progressLabel": "升级进度",
        "doneText": False,
        "benefits": [
            {"title": "会员券包", "desc": "菜品酒水任领", "icon": "/static/icons/benefit/coupon.png"},
            {"title": "管家服务", "desc": "金牌管家1V1服务", "icon": "/static/icons/benefit/steward.png"},
            {"title": "生日尊享", "desc": "特色生日面/当月出行2倍积分", "icon": "/static/icons/benefit/birthday.png"},
            {"title": "送红酒加大菜", "desc": "出行日每桌送1瓶红酒+1道大菜", "icon": "/static/icons/benefit/gift.png"},
            {"title": "优选位置", "desc": "指定包房/桌位优先", "icon": "/static/icons/benefit/seat.png"},
            {"title": "包房升级券", "desc": "工作日可用，6张/年", "icon": "/static/icons/benefit/room.png"},
            {"title": "门店礼遇", "desc": "精修合照/欢迎语制作", "icon": "/static/icons/benefit/store.png"},
            {"title": "扣损减免", "desc": "每年3桌扣损减免", "icon": "/static/icons/benefit/waiver.png"},
        ],
    },
]

MEMBER_MONTH_COUPON = {
    "title": "红酒20元立减券",
    "tip": "前台核销使用",
    "tag": "红酒\n立减\n20元券",
}

MEMBER_RULES = [
    {
        "title": "一、会员等级体系",
        "blocks": [
            {
                "subtitle": "1.1 等级介绍",
                "paras": [
                    "会员等级根据用户近365天内在天天俱乐部小程序累计消费桌数评定，共设 V0、V1、V2、V3 四个等级。",
                    {"text": "注：视频号、抖音、美团等外部平台订单不计入会员等级统计。", "tip": True},
                ],
            },
            {
                "subtitle": "1.2 等级标准",
                "paras": [
                    {"text": "V0：仅注册，每年有效桌数为 0 桌", "indent": True},
                    {"text": "V1：每年有效桌数为 1 桌", "indent": True},
                    {"text": "V2：每年有效桌数为 2–4 桌", "indent": True},
                    {"text": "V3：每年有效桌数为 5 桌及以上", "indent": True},
                ],
            },
        ],
    },
    {
        "title": "二、会员权益体系详解",
        "blocks": [
            {
                "subtitle": "2.1 积分倍率",
                "paras": [
                    {"text": "V0 / V1 / V2：0.5 倍积分", "indent": True},
                    {"text": "V3：1.0 倍积分", "indent": True},
                    {"text": "注：首单消费固定按 0.5 倍积分计算。", "tip": True},
                ],
            },
            {
                "subtitle": "2.2 管家服务",
                "paras": [
                    {"text": "V0 / V1：基础客服服务（大众管家）", "indent": True},
                    {"text": "V2：专属管家服务（银牌管家）", "indent": True},
                    {"text": "V3：金牌管家 1V1 服务", "indent": True},
                ],
            },
            {
                "subtitle": "2.3 生日礼遇",
                "paras": [
                    {"text": "V0：无", "indent": True},
                    {"text": "V1：门店特色生日面", "indent": True},
                    {"text": "V2：特色生日面 + 生日当月出行 2 倍积分", "indent": True},
                    {"text": "V3：生日蛋糕 + 礼品 + 特色生日面 + 生日当月出行 2 倍积分", "indent": True},
                    {"text": "注：生日礼遇适用于 12 人及以上预订，需提前至少 2 天告知门店。", "tip": True},
                ],
            },
            {
                "subtitle": "2.4 门店礼遇",
                "paras": [
                    {"text": "V0 / V1：无", "indent": True},
                    {"text": "V2 / V3：精修合照服务、主题欢迎语 / 活动氛围定制", "indent": True},
                ],
            },
            {
                "subtitle": "2.5 酒水权益",
                "paras": [
                    {"text": "V0 / V1：无", "indent": True},
                    {"text": "V2：出行日每桌赠送 1 瓶红酒", "indent": True},
                    {"text": "V3：出行日每桌赠送 1 瓶红酒 + 1 道招牌大菜", "indent": True},
                    {"text": "注：适用于 12 人及以上预订。", "tip": True},
                ],
            },
            {
                "subtitle": "2.6 扣损减免",
                "paras": [
                    {"text": "V0 / V1 / V2：无", "indent": True},
                    {"text": "V3：每年可享 3 次扣损减免", "indent": True},
                ],
            },
            {
                "subtitle": "2.7 优先权益",
                "paras": [
                    {"text": "V0 / V1 / V2：无", "indent": True},
                    {"text": "V3：包房 / 桌位预订优先权", "indent": True},
                ],
            },
            {
                "subtitle": "2.8 会员券包",
                "paras": [
                    {"text": "V0 / V1：黄酒 5 元券 + 红酒 20 元立减券", "indent": True},
                    {"text": "V2：黄酒 5 元券 + 红酒 20 元立减券 + 工作日包房升级券 3 张/年", "indent": True},
                    {"text": "V3：黄酒 5 元券 + 红酒 20 元立减券 + 工作日包房升级券 6 张/年", "indent": True},
                ],
            },
        ],
    },
    {
        "title": "三、相关规则",
        "blocks": [
            {
                "subtitle": "3.1 规则调整",
                "paras": [
                    "天天俱乐部有权根据经营需要调整会员权益、积分规则等内容。规则变更将通过小程序公告等方式告知，自公告之日起 30 日后生效。"
                ],
            },
            {
                "subtitle": "3.2 合规要求",
                "paras": [
                    "禁止转赠、出借、倒卖会员权益；禁止使用技术手段刷单、套取积分或优惠；禁止恶意注册、虚假消费等行为。一经发现，平台有权清空相关积分、收回权益，情节严重的可限制或封禁账号。"
                ],
            },
        ],
    },
]

MEMBER_CONFIG = {
    "levels": MEMBER_LEVELS,
    "monthCoupon": MEMBER_MONTH_COUPON,
    "rules": MEMBER_RULES,
}

RECOMMEND_BANNERS = [
    "https://picsum.photos/seed/gather-rec-b1/1200/500",
    "https://picsum.photos/seed/gather-rec-b2/1200/500",
    "https://picsum.photos/seed/gather-rec-b3/1200/500",
]

RECOMMEND_ITEMS = [
    {"name": "太仓锦江国际酒店", "cover": "https://picsum.photos/seed/gather-rec-1/800/600", "price": 249, "sort": 1},
    {"name": "苏州知音温德姆至尊酒店", "cover": "https://picsum.photos/seed/gather-rec-2/800/600", "price": 324, "sort": 2},
    {"name": "3天2晚(含2早1正)|苏州同里湖大饭店", "cover": "https://picsum.photos/seed/gather-rec-3/800/600", "price": 599, "sort": 3},
    {"name": "苏州金陵南林饭店", "cover": "https://picsum.photos/seed/gather-rec-4/800/600", "price": 229, "sort": 4},
    {"name": "江阴城发金茂嘉悦酒店", "cover": "https://picsum.photos/seed/gather-rec-5/800/600", "price": 399, "sort": 5},
    {"name": "3天2晚(含2早2正)|常州远洲酒店", "cover": "https://picsum.photos/seed/gather-rec-6/800/600", "price": 459, "sort": 6},
    {"name": "无锡希尔顿逸林酒店", "cover": "https://picsum.photos/seed/gather-rec-7/800/600", "price": 369, "sort": 7},
    {"name": "南通新城吾悦精选酒店", "cover": "https://picsum.photos/seed/gather-rec-8/800/600", "price": 289, "sort": 8},
    {"name": "常熟虞城希尔顿欢朋酒店", "cover": "https://picsum.photos/seed/gather-rec-9/800/600", "price": 319, "sort": 9},
]


HOBBY_OPTIONS = {
    "items": [
        {"name": "旅游", "color": "#f08a3a", "enabled": True, "sort": 1},
        {"name": "美食", "color": "#5aa8e8", "enabled": True, "sort": 2},
        {"name": "酒店", "color": "#3cbf7a", "enabled": True, "sort": 3},
        {"name": "休闲娱乐", "color": "#8b6bc9", "enabled": True, "sort": 4},
        {"name": "线下活动", "color": "#3d6fd9", "enabled": True, "sort": 5},
        {"name": "老年大学", "color": "#e24b4b", "enabled": True, "sort": 6},
    ]
}

LOYALTY_CONFIG = {
    "welcomePoints": 12,
    "earnRateDefault": 0.5,
    "earnRateV3": 1.0,
    "firstOrderRate": 0.5,
    "birthdayMultiplier": 2.0,
    "vipTables": {"V1": 1, "V2": 2, "V3": 5},
    "roomPrice": 0,
}


# 签到规则：每日积分 + 当月累计天数里程碑（与小程序签到页一致）
CHECKIN_CONFIG = {
    "dailyPoints": 2,
    "makeupPoints": 2,
    "fullMonthBonus": 30,
    "milestones": [
        {"days": 5, "points": 2, "label": "签到5天"},
        {"days": 15, "points": 15, "label": "签到15天"},
        {"days": 25, "points": 25, "label": "签到25天"},
    ],
    "rules": "每日签到可领取积分，当月累计签到可解锁额外奖励。漏签可用补签机会补回，每日仅一次。",
}


def default_nye_packages(price: float, cover: str) -> list[dict]:
    p = price or 2388
    c = cover or ""
    return [
        {"id": 1, "name": "喜气羊羊宴 (10-12人) 午市大厅", "meal": "喜气羊羊宴", "time": "10:00-14:00", "price": p, "people": 12, "cover": c, "disabled": False},
        {"id": 2, "name": "喜气羊羊宴 (10-12人) 晚市大厅", "meal": "喜气羊羊宴", "time": "17:00-21:00", "price": p + 200, "people": 12, "cover": c, "disabled": False},
        {"id": 3, "name": "喜气羊羊宴 (8-10人) 午市包厢", "meal": "喜气羊羊宴", "time": "10:00-14:00", "price": p + 300, "people": 10, "cover": c, "disabled": False},
        {"id": 4, "name": "团圆家宴 (8-10人) 晚市大厅", "meal": "团圆家宴", "time": "17:00-21:00", "price": p + 100, "people": 10, "cover": c, "disabled": False},
        {"id": 5, "name": "团圆家宴 (6-8人) 午市包厢", "meal": "团圆家宴", "time": "10:00-14:00", "price": p - 400, "people": 8, "cover": c, "disabled": False},
        {"id": 6, "name": "名羊四海宴 (12-14人) 午市大厅", "meal": "名羊四海宴", "time": "10:00-14:00", "price": p + 1100, "people": 14, "cover": c, "disabled": False},
        {"id": 7, "name": "名羊四海宴 (16人) 晚市大厅", "meal": "名羊四海宴", "time": "17:00-21:00", "price": p + 2100, "people": 16, "cover": c, "disabled": True},
        {"id": 8, "name": "名羊四海宴 (16人) 晚市包厢", "meal": "名羊四海宴", "time": "17:00-21:00", "price": p + 2100, "people": 16, "cover": c, "disabled": True},
    ]


def default_theme_packages(price: float, cover: str) -> list[dict]:
    """非年夜饭主题（包房聚会等）默认规格。"""
    p = price or 799
    c = cover or ""
    return [
        {"id": 1, "name": "【大厅】6人（标准菜单）", "meal": "标准菜单", "time": "10:00-21:00", "price": p, "people": 6, "cover": c, "disabled": False},
        {"id": 2, "name": "【包房】6人（标准菜单）", "meal": "标准菜单", "time": "10:00-21:00", "price": p + 100, "people": 6, "cover": c, "disabled": False},
        {"id": 3, "name": "6人包房-海鲜聚宝盆", "meal": "海鲜聚宝盆", "time": "10:00-21:00", "price": p + 200, "people": 6, "cover": c, "disabled": False},
        {"id": 4, "name": "【大厅】12人（标准菜单）", "meal": "标准菜单", "time": "10:00-21:00", "price": p + 589, "people": 12, "cover": c, "disabled": False},
        {"id": 5, "name": "【包房】12人套餐（大厅棋牌）（标准菜单）", "meal": "标准菜单", "time": "10:00-21:00", "price": p + 789, "people": 12, "cover": c, "disabled": False},
        {"id": 6, "name": "【包房】12人套餐（包房内棋牌）（标准菜单）", "meal": "标准菜单", "time": "10:00-21:00", "price": p + 889, "people": 12, "cover": c, "disabled": False},
        {"id": 7, "name": "【包房】12人套餐（大厅棋牌）（尊享菜单）", "meal": "尊享菜单", "time": "10:00-21:00", "price": p + 1317, "people": 12, "cover": c, "disabled": False},
        {"id": 8, "name": "【双桌包房】20-22人套餐（包房内棋牌）（标准菜单）", "meal": "标准菜单", "time": "10:00-21:00", "price": p + 2377, "people": 22, "cover": c, "disabled": False},
        {"id": 9, "name": "【豪华包房】18-20人套餐（标准菜单）", "meal": "标准菜单", "time": "10:00-21:00", "price": p + 2589, "people": 20, "cover": c, "disabled": False},
    ]


DEFAULT_ACTIVITIES = [
    {
        "id": "nye",
        "name": "年夜饭",
        "tag": "年夜饭",
        "banners": [],
        "enabled": True,
        "sort": 1,
    },
    {
        "id": "family",
        "name": "家宴",
        "tag": "家宴",
        "banners": [],
        "enabled": True,
        "sort": 2,
    },
]
