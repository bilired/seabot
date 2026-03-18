import os
import threading
from typing import Any, Dict, Tuple

from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_dypnsapi20170525 import models as dypns_models
from alibabacloud_dypnsapi20170525.client import Client as DypnsapiClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as util_models


def create_client() -> DypnsapiClient:
    access_key_id = (os.getenv('ALIYUN_SMS_ACCESS_KEY_ID') or '').strip()
    access_key_secret = (os.getenv('ALIYUN_SMS_ACCESS_KEY_SECRET') or '').strip()
    security_token = (os.getenv('ALIYUN_SMS_SECURITY_TOKEN') or '').strip()
    endpoint = (os.getenv('ALIYUN_SMS_ENDPOINT') or 'dypnsapi.aliyuncs.com').strip()

    if access_key_id and access_key_secret:
        config = open_api_models.Config(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            security_token=security_token or None,
        )
        config.endpoint = endpoint
        return DypnsapiClient(config)

    if threading.current_thread() is not threading.main_thread():
        raise RuntimeError(
            '短信服务凭证未配置，请设置 ALIYUN_SMS_ACCESS_KEY_ID 和 ALIYUN_SMS_ACCESS_KEY_SECRET'
        )

    credential = CredentialClient()
    config = open_api_models.Config(credential=credential)
    config.endpoint = endpoint
    return DypnsapiClient(config)


def _to_dict(obj: Any) -> Dict[str, Any]:
    if obj is None:
        return {}
    if isinstance(obj, dict):
        return obj
    if hasattr(obj, 'to_map'):
        return obj.to_map()
    if hasattr(obj, '__dict__'):
        return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
    return {}


def _extract_body(resp: Any) -> Dict[str, Any]:
    body = getattr(resp, 'body', None)
    body_dict = _to_dict(body)
    if body_dict:
        return body_dict
    return _to_dict(resp)


def _normalize_text(value: Any) -> str:
    if value is None:
        return ''
    return str(value).strip()


def _is_true_text(value: Any) -> bool:
    text = _normalize_text(value).lower()
    return text in {'1', 'true', 'ok', 'pass', 'passed', 'success'}


def _extract_error_payload(error: Exception) -> Dict[str, Any]:
    payload: Dict[str, Any] = {}
    data = getattr(error, 'data', None)
    if isinstance(data, dict):
        payload.update(data)

    message = _normalize_text(getattr(error, 'message', None) or str(error))
    if message and 'Message' not in payload and 'message' not in payload:
        payload['message'] = message

    return payload


def _pick_error_code(payload: Dict[str, Any]) -> str:
    return _normalize_text(payload.get('Code') or payload.get('code'))


def _pick_error_message(payload: Dict[str, Any], default_message: str) -> str:
    return _normalize_text(payload.get('Message') or payload.get('message')) or default_message


def send_sms_verify_code(phone_number: str) -> Tuple[bool, str, Dict[str, Any]]:
    client = create_client()

    sign_name = os.getenv('ALIYUN_SMS_SIGN_NAME', '速通互联验证平台')
    template_code = os.getenv('ALIYUN_SMS_TEMPLATE_CODE', '100001')
    template_param = os.getenv('ALIYUN_SMS_TEMPLATE_PARAM', '{"code":"##code##","min":"5"}')
    scheme_name = os.getenv('ALIYUN_SMS_SCHEME_NAME', '').strip()

    if not scheme_name:
        return False, '短信配置缺失：请设置 ALIYUN_SMS_SCHEME_NAME（方案名称）', {}

    request = dypns_models.SendSmsVerifyCodeRequest(
        phone_number=phone_number,
        scheme_name=scheme_name,
        sign_name=sign_name,
        template_code=template_code,
        template_param=template_param,
    )

    runtime = util_models.RuntimeOptions()
    try:
        resp = client.send_sms_verify_code_with_options(request, runtime)
    except Exception as error:
        payload = _extract_error_payload(error)
        message = _pick_error_message(payload, '验证码发送失败')
        return False, message, payload

    payload = _extract_body(resp)

    code = _normalize_text(payload.get('Code') or payload.get('code'))
    message = _normalize_text(payload.get('Message') or payload.get('message'))
    success = code == 'OK'

    return success, (message or ('发送成功' if success else '发送失败')), payload


def check_sms_verify_code(phone_number: str, verify_code: str) -> Tuple[bool, str, Dict[str, Any]]:
    client = create_client()
    scheme_name = os.getenv('ALIYUN_SMS_SCHEME_NAME', '').strip()
    if not scheme_name:
        return False, '短信配置缺失：请设置 ALIYUN_SMS_SCHEME_NAME（方案名称）', {}

    request = dypns_models.CheckSmsVerifyCodeRequest(
        phone_number=phone_number,
        scheme_name=scheme_name,
        verify_code=verify_code,
    )

    runtime = util_models.RuntimeOptions()
    try:
        resp = client.check_sms_verify_code_with_options(request, runtime)
    except Exception as error:
        payload = _extract_error_payload(error)
        error_code = _pick_error_code(payload).lower()
        if error_code == 'isv.validatefail':
            return False, '验证码错误或已过期', payload

        message = _pick_error_message(payload, '验证码校验失败')
        return False, message, payload

    payload = _extract_body(resp)

    code = _normalize_text(payload.get('Code') or payload.get('code'))
    message = _normalize_text(payload.get('Message') or payload.get('message'))

    verify_markers = [
        payload.get('IsVerify'),
        payload.get('isVerify'),
        payload.get('VerifyResult'),
        payload.get('verifyResult'),
        payload.get('Result'),
        payload.get('result'),
    ]
    verify_pass = any(_is_true_text(marker) for marker in verify_markers if marker is not None)

    if code != 'OK':
        return False, (message or '验证码校验失败'), payload

    if any(marker is not None for marker in verify_markers):
        if verify_pass:
            return True, (message or '验证码校验通过'), payload
        return False, (message or '验证码不正确或已过期'), payload

    return True, (message or '验证码校验通过'), payload
