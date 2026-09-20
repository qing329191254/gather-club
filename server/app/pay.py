"""微信支付 APIv2：统一下单 + 小程序 paySign + 支付结果通知。"""

from __future__ import annotations

import hashlib
import time
import uuid
from typing import Any, Optional
from xml.etree import ElementTree as ET

import httpx
from fastapi import HTTPException

from .config import get_settings


def pay_configured() -> bool:
    s = get_settings()
    return bool(s.wx_appid and s.wx_mch_id and s.wx_mch_key)


def _sign(params: dict[str, Any], key: str) -> str:
    items = sorted((k, v) for k, v in params.items() if v is not None and str(v) != "" and k != "sign")
    raw = "&".join(f"{k}={v}" for k, v in items) + f"&key={key}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest().upper()


def _dict_to_xml(data: dict[str, Any]) -> str:
    parts = ["<xml>"]
    for k, v in data.items():
        parts.append(f"<{k}><![CDATA[{v}]]></{k}>")
    parts.append("</xml>")
    return "".join(parts)


def _xml_to_dict(xml_text: str) -> dict[str, str]:
    root = ET.fromstring(xml_text)
    return {child.tag: (child.text or "") for child in root}


def build_jsapi_payment(prepay_id: str) -> dict[str, str]:
    settings = get_settings()
    ts = str(int(time.time()))
    nonce = uuid.uuid4().hex
    package = f"prepay_id={prepay_id}"
    payload = {
        "appId": settings.wx_appid,
        "timeStamp": ts,
        "nonceStr": nonce,
        "package": package,
        "signType": "MD5",
    }
    payload["paySign"] = _sign(payload, settings.wx_mch_key)
    return {
        "timeStamp": ts,
        "nonceStr": nonce,
        "package": package,
        "signType": "MD5",
        "paySign": payload["paySign"],
    }


async def unified_order(
    *,
    openid: str,
    out_trade_no: str,
    body: str,
    total_fee: int,
    client_ip: str = "127.0.0.1",
    notify_url: Optional[str] = None,
) -> dict[str, Any]:
    """调用统一下单，返回含 prepay_id 的结果。total_fee 单位为分。"""
    if not pay_configured():
        raise HTTPException(status_code=500, detail="未配置微信支付商户号")
    if total_fee < 1:
        raise HTTPException(status_code=400, detail="支付金额无效")
    if not openid or openid.startswith("demo_"):
        raise HTTPException(status_code=400, detail="当前账号无法发起微信支付")

    settings = get_settings()
    notify = (notify_url or settings.wx_notify_url or "").strip()
    if not notify:
        raise HTTPException(status_code=500, detail="未配置 WX_NOTIFY_URL")

    nonce = uuid.uuid4().hex
    params = {
        "appid": settings.wx_appid,
        "mch_id": settings.wx_mch_id,
        "nonce_str": nonce,
        "body": (body or "天天俱乐部订单")[:127],
        "out_trade_no": out_trade_no,
        "total_fee": str(int(total_fee)),
        "spbill_create_ip": client_ip or "127.0.0.1",
        "notify_url": notify,
        "trade_type": "JSAPI",
        "openid": openid,
    }
    params["sign"] = _sign(params, settings.wx_mch_key)
    xml_body = _dict_to_xml(params)

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            "https://api.mch.weixin.qq.com/pay/unifiedorder",
            content=xml_body.encode("utf-8"),
            headers={"Content-Type": "application/xml"},
        )
        data = _xml_to_dict(resp.text)

    if data.get("return_code") != "SUCCESS":
        raise HTTPException(status_code=400, detail=f"微信支付通信失败: {data.get('return_msg') or data}")
    if data.get("result_code") != "SUCCESS":
        raise HTTPException(
            status_code=400,
            detail=f"统一下单失败: {data.get('err_code_des') or data.get('err_code') or data}",
        )
    prepay_id = data.get("prepay_id") or ""
    if not prepay_id:
        raise HTTPException(status_code=400, detail="未返回 prepay_id")
    return {"prepay_id": prepay_id, "raw": data}


def parse_notify(xml_text: str) -> dict[str, str]:
    data = _xml_to_dict(xml_text or "")
    if not data:
        raise HTTPException(status_code=400, detail="通知为空")
    settings = get_settings()
    if not settings.wx_mch_key:
        raise HTTPException(status_code=500, detail="未配置商户密钥")
    sign = data.get("sign") or ""
    expected = _sign(data, settings.wx_mch_key)
    if sign.upper() != expected.upper():
        raise HTTPException(status_code=400, detail="签名校验失败")
    return data


def notify_ok_xml() -> str:
    return "<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml>"


def notify_fail_xml(msg: str = "FAIL") -> str:
    return f"<xml><return_code><![CDATA[FAIL]]></return_code><return_msg><![CDATA[{msg}]]></return_msg></xml>"
