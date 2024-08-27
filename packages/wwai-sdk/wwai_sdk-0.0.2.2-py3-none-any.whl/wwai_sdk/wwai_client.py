import asyncio
import base64
import json
import logging
import os
from crypt import methods

import requests
from requests_toolbelt import MultipartEncoder

from wwai_sdk import utils
from wwai_sdk.cache import WwaiSdkCache
from wwai_sdk.decrypt_util import decrypt_rsa, decrypt_aes

logger = logging.getLogger(__name__)

class WwaiClient:
    def __init__(self,
                 grant_type,
                 server="http://ai.api.wwai.wwxckj.com",
                 authorization=None,
                 username=None,
                 password=None,
                 tenant_code=None,
                 client_id=None,
                 client_secret=None,
                 cache_type="local",
                 redis_host=None,
                 redis_port=6379,
                 redis_password=None,
                 redis_db=0):
        self.cache = WwaiSdkCache(cache_type, redis_host, redis_port, redis_password, redis_db)
        self.server = server
        self.grant_type = grant_type
        self.authorization = authorization
        self.username = username
        self.password = password
        self.tenant_code = tenant_code
        self.client_id = client_id
        self.client_secret = client_secret
        self.get_token()

    def get_token(self):
        """
        获取Token
        :return:
        """
        access_token = self.cache.get(f"{self.tenant_code}-access_token")
        if access_token:
            return access_token, self.cache.get(f"{self.tenant_code}-tenant_id")
        headers = {
            "Authorization": self.authorization,
            "Content-Type": 'application/x-www-form-urlencoded'
        }
        if self.grant_type == 'password':
            payload = {
                "grant_type": "password",
                "username": self.username,
                "password": self.password,
                "tenant_code": self.tenant_code
            }
        else:
            payload = {
                "grant_type": "client_credentials"
            }
        response = requests.post(
            f"{self.server}/auth/oauth2/token",
            headers=headers,
            data=payload,
            verify=False
        )
        if response.ok:
            response_data = response.json()
            if "access_token" in response_data:
                access_token = f"Bearer {response_data.get('access_token', '')}"
                tenant_id = response_data.get("tenant_id", None)
                access_token_expire = int(response_data.get("expires_in", "0"))
                access_token_expire = access_token_expire - 60
                self.cache.set(f"{self.tenant_code}-access_token", access_token, access_token_expire)
                if tenant_id:
                    self.cache.set(f"{self.tenant_code}-tenant_id", tenant_id)
                return access_token, tenant_id
            else:
                raise ValueError(f"WWAI云平台参数错误：{response.status_code} {response.text}")
        else:
            raise ValueError(f"WWAI云平台登陆异常：{response.status_code} {response.text}")



    def _request(self, url: str, params=None, json=None, data=None, files=None, headers=None, method="GET", all_result=False):
        """
        发送请求
        :return:
        """
        base_url = self.server
        if base_url.endswith("/"):
            base_url = base_url[:-1]
        if url.startswith("/"):
            url = url[1:]
        api_url = f"{base_url}/{url}"

        if headers is None:
            headers = {}
        access_token, tenant_id = self.get_token()
        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json'
        headers['Authorization'] = f"{access_token}"
        if tenant_id is not None:
            headers['Tenant-ID'] = tenant_id

        resp = requests.request(method, api_url, params=params, json=json, data=data, files=files, headers=headers, verify=False)
        if resp.ok:
            resp = resp.json()
            if int(resp.get("code", "500")) != 0:
                if resp["msg"] == "用户凭证已过期":
                    self.cache.delete(f"{self.tenant_code}-access_token")
                    self.cache.delete(f"{self.tenant_code}-tenant_id")
                raise Exception(resp["msg"])
            else:
                return resp if all_result else resp['data']
        else:
            raise Exception(resp.text)

    async def ocr_idcard(self, image_url, side=None):
        """
        身份证识别
        :param image_url:
        :param side:
        :return:
        """
        req = {
            "image": image_url,
            "side": side
        }
        return await asyncio.to_thread(self._request, "/open/ocr/idcard", json=req, method="POST")

    async def ocr_vehicle(self, image_url: str):
        """
        行驶证识别
        :param image_url:
        :return:
        """
        req = {
            "image": image_url
        }
        return await asyncio.to_thread(self._request, "/open/ocr/vehicle", json=req, method="POST")

    async def ocr_vehicle_certificate(self, image_url: str):
        """
        机动车登记证书识别
        :param image_url:
        :return:
        """
        req = {
            "image": image_url
        }
        return await asyncio.to_thread(self._request, "/open/ocr/vehicle_certificate", json=req, method="POST")

    async def ocr_invoice(self, image_url: str):
        """
        发票识别
        :param image_url:
        :return:
        """
        req = {
            "image": image_url
        }
        return await asyncio.to_thread(self._request, "/open/ocr/invoice", json=req, method="POST")

    async def ocr_bank_card(self, image_url: str):
        """
        银行卡识别
        :param image_url:
        :return:
        """
        req = {
            "image": image_url
        }
        return await asyncio.to_thread(self._request, "/open/ocr/bank", json=req, method="POST")

    async def other_classify(self, image):
        """
        通用图片分类
        :param image:
        :return:
        """
        req = {
            "image": image
        }
        return await asyncio.to_thread(self._request, "/open/other/image_classify", json=req, method="POST")


    async def asr_iat(self, audio: str):
        """
        语音识别
        :return:
        """
        try:
            import wave
        except ImportError:
            raise ImportError("Please install wave with `pip install wave`")

        if not audio:
            return
        if utils.is_url(audio):
            audio = utils.down_bytes(audio)
            audio = base64.b64encode(audio).decode()
        if not isinstance(audio, str):
            raise ValueError("audio must be base64 or url")

        try:
            res = await asyncio.to_thread(self._request, "/open/speech/asr_result", data={"audio": audio}, method="POST",
                                headers={"Content-Type": "application/x-www-form-urlencoded"})
            logger.info(f"=======>wwai asr res: {res}")
            return res
        except Exception as e:
            logger.error(f"wwai asr error: {e}")
            raise e

    async def aigc_models(self, model_type=None):
        """
        获取可用的模型列表
        :param model_type:
        :return:
        """
        req = {}
        if model_type:
            if model_type not in ["text", "vl", "embedding"]:
                raise ValueError("model_type must be text or vl or embedding")
            req["modelType"] = model_type
        return await asyncio.to_thread(self._request, "/open/aigc/models", params=req)

    async def huaweicloud_obs_get_ak_sk(self, bucket_name, endpoint=None):
        """
        获取临时OBS的 AK/SK
        :param bucket_name:
        :param endpoint:
        :return:
        """
        req = {
            "bucketName": bucket_name
        }
        if endpoint:
            req["endpoint"] = endpoint
        else:
            req["endpoint"] = "obs.cn-north-4.myhuaweicloud.com"

        res = await asyncio.to_thread(self._request, "/open/huaweicloud/getObsTempAkSk", json=req, method="POST", all_result=True)
        aes_key_encrypt_data = res.get("aesKey", "")
        encrypt_data = res.get("data", "")

        aes_key = decrypt_rsa(aes_key_encrypt_data)
        data = decrypt_aes(encrypt_data, aes_key)

        return json.loads(data)

    async def common_word2html(self, word_path):
        """
        word转html
        :param word_path:
        :return:
        """
        if not os.path.exists(word_path):
            raise FileNotFoundError(f"文件{word_path}不存在")
        filename = os.path.basename(word_path)
        data = MultipartEncoder(
            fields={
                "file": (filename, open(word_path, "rb"))
            }
        )
        access_token, tenant_id = self.get_token()
        headers = {
            "Content-Type": data.content_type,
            "Authorization": f"Bearer {access_token}"
        }
        if tenant_id:
            headers["Tenant-Id"] = tenant_id
        resp = await asyncio.to_thread(requests.post, f"{self.server}/open/common/word2html", data=data, headers=headers, verify=False)
        if resp.ok:
            b = resp.content
            html = b.decode("utf-8")
            return html
        else:
            logger.error(f"word转html失败: {resp.text}")
            raise Exception(resp.text)

    async def common_word2docx(self, word_path):
        """
        word转docx
        :param word_path:
        :return:
        """
        if not os.path.exists(word_path):
            raise FileNotFoundError(f"文件{word_path}不存在")
        filename = os.path.basename(word_path)
        data = MultipartEncoder(
            fields={
                "file": (filename, open(word_path, "rb"))
            }
        )
        access_token, tenant_id = self.get_token()
        headers = {
            "Content-Type": data.content_type,
            "Authorization": f"Bearer {access_token}"
        }
        if tenant_id:
            headers["Tenant-Id"] = tenant_id
        resp = await asyncio.to_thread(requests.post, f"{self.server}/open/common/word2docx", data=data, headers=headers, verify=False)
        if resp.ok:
            docx_path = f"{word_path}.docx"
            with open(docx_path, "wb") as f:
                f.write(resp.content)
            return docx_path
        else:
            logger.error(f"word转docx失败: {resp.text}")
            raise Exception(resp.text)

    async def common_word2pdf(self, word_path: str, pdf_path: None):
        """
        word转pdf
        :param word_path:
        :return:
        """
        if not os.path.exists(word_path):
            raise FileNotFoundError(f"文件{word_path}不存在")
        filename = os.path.basename(word_path)
        data = MultipartEncoder(
            fields={
                "file": (filename, open(word_path, "rb"))
            }
        )
        access_token, tenant_id = self.get_token()
        headers = {
            "Content-Type": data.content_type,
            "Authorization": f"Bearer {access_token}"
        }
        if tenant_id:
            headers["Tenant-Id"] = tenant_id
        resp = await asyncio.to_thread(requests.post, f"{self.server}/open/common/doc2pdf", data=data, headers=headers, verify=False)
        if resp.ok:
            if not pdf_path:
                pdf_path = f"{word_path}.pdf"
            with open(pdf_path, "wb") as f:
                f.write(resp.content)
            return pdf_path
        else:
            logger.error(f"word转pdf失败: {resp.text}")
            raise Exception(resp.text)

    async def common_cp_user(self, agentid, code, state=None):
        """
        获取企业用户信息
        :param agentid:
        :param code:
        :return:
        """
        data = {
            "agentid": agentid,
            "code": code,
            "state": state
        }
        resp = await asyncio.to_thread(self._request, "/open/oauth2/cp/verifyCode", params=data, method='GET')
        if resp.get("uuid", ""):
            return resp
        raise Exception("获取企业用户信息失败")
