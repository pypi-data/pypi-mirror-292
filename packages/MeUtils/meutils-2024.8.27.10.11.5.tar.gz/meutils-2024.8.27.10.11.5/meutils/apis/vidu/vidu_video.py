#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : vidu_video
# @Time         : 2024/7/31 08:59
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :

from meutils.decorators.retry import retrying
from meutils.pipe import *
from meutils.schemas.vidu_types import BASE_URL, UPLOAD_BASE_URL, ViduRequest, ViduUpscaleRequest
from meutils.schemas.task_types import TaskType, Task, FileTask

from meutils.notice.feishu import send_message as _send_message
from meutils.config_utils.lark_utils import get_next_token_for_polling

FEISHU_URL = "https://xchatllm.feishu.cn/sheets/Bmjtst2f6hfMqFttbhLcdfRJnNf?sheet=l3VpZf"
FEISHU_URL_VIP = "https://xchatllm.feishu.cn/sheets/GYCHsvI4qhnDPNtI4VPcdw2knEd?sheet=EYgZ8c"

send_message = partial(
    _send_message,
    title=__name__,
    url="https://open.feishu.cn/open-apis/bot/v2/hook/dc1eda96-348e-4cb5-9c7c-2d87d584ca18"
)


async def upload(file, token: Optional[str] = None, vip: bool = False):  # todo: 统一到 file object
    token = token or await get_next_token_for_polling(FEISHU_URL_VIP if vip else FEISHU_URL)
    token = token.strip(";Shunt=").strip("; Shunt=")
    logger.debug(token)

    payload = {"scene": "vidu"}
    headers = {
        "Cookie": token  # ;Shunt= 居然失效
    }
    async with httpx.AsyncClient(base_url=UPLOAD_BASE_URL, headers=headers, timeout=60) as client:
        response = await client.post("/files/uploads", json=payload)
        if response.is_success:
            logger.debug(response.json())
            file_id = response.json()['id']
            put_url = response.json()['put_url']  # 图片url

            response = await client.put(put_url, content=file, headers=headers)
            etag = response.headers.get('Etag')

            payload = {"id": file_id, "etag": etag}
            response = await client.put(f"/files/uploads/{file_id}/finish", json=payload)
            logger.debug(response.text)
            logger.debug(response.status_code)
            logger.debug(put_url.split('?')[0])
            if response.is_success:
                uri = response.json()['uri']
                return FileTask(id=file_id, url=put_url, system_fingerprint=token)

            response.raise_for_status()


@retrying(max_retries=8, max=8, predicate=lambda r: r is True, title=__name__)  # 触发重试
async def create_task(request: ViduRequest, token: Optional[str] = None, vip: bool = False):
    token = token or await get_next_token_for_polling(FEISHU_URL_VIP if vip else FEISHU_URL)
    token = token.strip(";Shunt=").strip("; Shunt=")

    task_type = TaskType.vidu_vip if vip else TaskType.vidu

    headers = {
        "Cookie": token
    }
    async with httpx.AsyncClient(base_url=BASE_URL, headers=headers, timeout=60) as client:
        response = await client.post("/tasks", json=request.payload)

        logger.debug(response.text)
        logger.debug(response.status_code)

        if response.status_code in {429, 403} or "insufficient" in response.text:  # 触发重试
            return True

        if response.is_success:
            data = response.json()
            task_id = f"{task_type}-{data['id']}"
            return Task(id=task_id, data=data, system_fingerprint=token)
        else:
            logger.debug(token)
            return Task(data=response.text, status=0, status_code=response.status_code)


@retrying(max_retries=8, max=8, predicate=lambda r: r is True)  # 触发重试
async def create_task_upscale(request: ViduUpscaleRequest, token: str):
    payload = {
        "input": {
            "creation_id": str(request.creation_id)
        },
        "type": "upscale",
        "settings": {"model": "stable", "duration": 4}
    }
    headers = {
        "Cookie": token
    }
    async with httpx.AsyncClient(base_url=BASE_URL, headers=headers, timeout=60) as client:
        response = await client.post("/tasks", json=payload)

        if response.status_code in {429} and "insufficient" in response.text:  # 触发重试
            return True

        if response.is_success:
            data = response.json()
            task_id = f"vidu-{data['id']}"
            return Task(id=task_id, data=data, system_fingerprint=token)
        else:
            return Task(data=response.text, status=0, status_code=response.status_code)


async def get_task(task_id: str, token: str):  # https://api.vidu.studio/vidu/v1/tasks/state?id=2375528561004183
    task_id = task_id.split("-", 1)[-1]

    token = token.strip(";Shunt=").strip("; Shunt=")

    headers = {
        "Cookie": token
    }
    async with httpx.AsyncClient(base_url=BASE_URL, headers=headers, timeout=30) as client:
        response = await client.get(f"/tasks/{task_id}")

        logger.debug(response.text)
        logger.debug(response.status_code)

        if response.is_success:
            data = response.json()
            return data
        response.raise_for_status()


async def get_credits(token: str):
    headers = {
        "Cookie": token
    }
    async with httpx.AsyncClient(base_url="https://api.vidu.studio/credit/v1", headers=headers, timeout=60) as client:
        response = await client.get(f"/credits/me")

        if response.is_success:
            data = response.json()
            return data


if __name__ == '__main__':
    # token = "JWT=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjM2ODMyODcsImlhdCI6MTcyMjM4NzI4NywiaXNzIjoiaWFtIiwic3ViIjoiMjM2ODMxNTE4NTAwNTI4NyJ9.4_tA-d3LI4ftNPPoAECdREtQIkn0vq95_OC22SHhfqA; Shunt="
    #
    # token = '_GRECAPTCHA=09AA5Y-DKEaPCPtfl_s0o9z-HKEP5Tkfrn7CsmZfUj5MUYAFZiW7ELincbr2c2baFkM5Vu_KDPJ11l_N_DJhHTx_A; HMACCOUNT_BFESS=4189E6AE98589913; Hm_lvt_a3c8711bce1795293b1793d35916c067=1722407159; Hm_lpvt_a3c8711bce1795293b1793d35916c067=1722407159; HMACCOUNT=4189E6AE98589913; io=FKh7a-dvlK-UnBmOAB7M; JWT=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjM3MDMxNjgsImlhdCI6MTcyMjQwNzE2OCwiaXNzIjoiaWFtIiwic3ViIjoiMjM2ODY0MDkxNDEwMTMxOCJ9.mbNkzI6piihIVDsGSshSCiLlakAAG_Hxh0xAnPkx_vs; Shunt=; Hm_lvt_a3c8711bce1795293b1793d35916c067=1753943158594|1722407159; shortid=parsvjrji; debug=undefined; _grecaptcha=09AA5Y-DJauC2Mo_KPc5_R5OUPR__wsqLYpOjUViIajU8hpDPOpg6LcH1xECbelcZwXl_BSHnZlCWRGxGWvRvMyQr7QGnCCJam75DKvw; VIDU_SELECTED_LOCALE=zh; VIDU_TOUR="v1"'
    # token = "JWT=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjM3MDIyNjAsImlhdCI6MTcyMjQwNjI2MCwiaXNzIjoiaWFtIiwic3ViIjoiMjM2ODYyNjA0MzE4MTg1NCJ9.8P8WuktyjFM0utFbGcxLQptzfv43ugmMcE31RXR9JJQ"
    # file = Path('/Users/betterme/PycharmProjects/AI/cover.jpeg').read_bytes()
    # url = arun(upload(file, token)).url

    # print(arun(get_next_token_for_polling(FEISHU_URL)) == token)

    # arun(get_task("vidu-2368380300283813", token=token))
    # arun(get_task('vidu-2389570992698888', token=token))

    # arun(create_task_upscale())

    # arun(get_credits(token))
    #
    d = {
        "prompt": "一条可爱的狗跑过来",
        # "url": url  # failed to save uploads
    }
    token = None
    print(bjson(ViduRequest(**d).payload))
    # arun(create_task(ViduRequest(**d), token=token))
    arun(create_task(ViduRequest(**d), vip=True))
    pass
