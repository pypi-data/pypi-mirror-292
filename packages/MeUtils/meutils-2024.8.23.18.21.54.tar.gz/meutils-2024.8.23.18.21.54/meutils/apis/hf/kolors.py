#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : kolors
# @Time         : 2024/7/25 08:42
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : https://huggingface.co/spaces/gokaygokay/KolorsPlusPlus
import os

#  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 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

from meutils.pipe import *
from meutils.schemas.openai_types import ImageRequest, ImagesResponse
from meutils.async_utils import sync_to_async
from meutils.decorators.retry import retrying

from gradio_client import Client as _Client

Client = lru_cache(_Client)


# os.getenv("HF_TOKEN")
@sync_to_async(thread_sensitive=False)
@retrying()
def create_image(request: ImageRequest):
    tokens = "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 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".split()
    token = np.random.choice(tokens + [None])

    client = Client("Kwai-Kolors/Kolors", download_files=False, hf_token=token)

    image = client.predict(
        prompt=request.prompt,
        ip_adapter_image=None,
        ip_adapter_scale=0.5,
        negative_prompt=request.negative_prompt,
        seed=0,
        randomize_seed=True,
        width=1024,
        height=1024,
        guidance_scale=request.guidance_scale,
        num_inference_steps=request.num_inference_steps,
        api_name="/infer"
    )

    return ImagesResponse(data=[image])


if __name__ == '__main__':
    r = ImageRequest(prompt='一张瓢虫的照片，微距，变焦，高质量，电影，拿着一个牌子，写着“可图”')
    # # with timer():
    # #     result = client.predict(
    # #         prompt="a cat",
    # #         negative_prompt=None,
    # #         api_name="/infer"
    # #     )
    # #     print(result)
    # # {'path': '/tmp/gradio/3a3fa0048e52b02169f4bb477d3c16e0a3fd7796/image.webp',
    # #  'url': 'https://kwai-kolors-kolors.hf.space/file=/tmp/gradio/3a3fa0048e52b02169f4bb477d3c16e0a3fd7796/image.webp',
    # #  'size': None, 'orig_name': 'image.webp', 'mime_type': None, 'is_stream': False,
    # #  'meta': {'_type': 'gradio.FileData'}}
    #
    with timer():
        arun(create_image(r))
