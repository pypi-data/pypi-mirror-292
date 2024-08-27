#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : image_to_image
# @Time         : 2024/8/23 17:04
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :

from meutils.pipe import *
from meutils.config_utils.lark_utils import get_spreadsheet_values, get_next_token_for_polling
from meutils.schemas.openai_types import ImageRequest, ImagesResponse
from meutils.apis.translator import deeplx
from meutils.schemas.translator_types import DeeplxRequest
from meutils.decorators.retry import retrying
from meutils.schemas.image_types import ASPECT_RATIOS
from meutils.io.image import image_to_base64

BASE_URL = "https://cloud.siliconflow.cn"
FEISHU_URL = "https://xchatllm.feishu.cn/sheets/Bmjtst2f6hfMqFttbhLcdfRJnNf?sheet=InxiCF"
FEISHU_URL_TOKEN = "https://xchatllm.feishu.cn/sheets/Bmjtst2f6hfMqFttbhLcdfRJnNf?sheet=xlvlrH"

url = "https://api.siliconflow.cn/v1/TencentARC/PhotoMaker/image-to-image"

PHOTOMAKER_STYLES = {
    "Photographic (Default)",
    "Cinematic",
    "Comic book",
    "Disney Character",
    "Disney Character",
    "Digital Art",
    "Fantasy Art",
    "Neopunk",
    "Enhance",
    "Lowpoly",
    "Line art",
    "(No style)",
}


@retrying(max_retries=3, title=__name__)
async def create(request: ImageRequest, api_key: Optional[str] = None):  # SD3
    api_key = api_key or await get_next_token_for_polling(feishu_url=FEISHU_URL)

    prompt = (await deeplx.translate(DeeplxRequest(text=request.prompt, target_lang="EN"))).get("data")

    if request.url.startswith('http'):
        image_data = image_to_base64(request.url)
    else:
        image_data = request.url

    payload = {
        "prompt": prompt,
        "negative_prompt": request.negative_prompt,
        "image_size": request.size,
        "batch_size": request.n,
        "seed": 0,
        "num_inference_steps": request.num_inference_steps,
        "guidance_scale": request.guidance_scale,

        "image": image_data,
        "style_name": request.style if request.style in PHOTOMAKER_STYLES else "Photographic (Default)",
        "style_strengh_radio": 20
    }

    # logger.debug(payload)

    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    base_url = "https://api.siliconflow.cn/v1"
    async with httpx.AsyncClient(base_url=base_url, headers=headers, timeout=100) as client:
        response = await client.post(f"{model}/image-to-image", json=payload)

        if response.is_success:
            data = response.json().get('images', [])
            return ImagesResponse(data=data)
        response.raise_for_status()  # 451


if __name__ == '__main__':
    url = "https://oss.ffire.cc/files/s.png"
    url = "https://dss2.bdstatic.com/5bVYsj_p_tVS5dKfpU_Y_D3/res/r/image/2021-3-4/hao123%20logo.png"
    # url = "https://sf-maas-uat-prod.oss-cn-shanghai.aliyuncs.com/outputs/5618c93e-74f6-4177-9a33-ef8b361ab1e9_00001_.png"
    model = "TencentARC/PhotoMaker"
    model = "ByteDance/SDXL-Lightning"
    model = "stabilityai/stable-diffusion-xl-base-1.0"
    model = "stabilityai/stable-diffusion-2-1"

    request = ImageRequest(
        prompt='a half-body portrait of a man img wearing the sunglasses in Iron man suit, best quality', url=url)

    arun(create(request))
