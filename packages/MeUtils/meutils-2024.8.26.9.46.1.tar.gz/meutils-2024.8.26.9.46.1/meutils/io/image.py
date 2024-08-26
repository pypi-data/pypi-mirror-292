#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : MeUtils.
# @File         : image
# @Time         : 2022/6/15 上午11:33
# @Author       : yuanjie
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : https://blog.csdn.net/Q_452086192/article/details/125014538
# https://www.jb51.net/article/207138.htm

import mimetypes

from PIL import Image

from meutils.pipe import *


def img2bytes(img, format=None):
    """

    @param img: Optional[Image | np.array]
    @param format:
    @return:
    """
    # cv2 = try_import("cv2", pip_name="opencv-python")
    import cv2

    if isinstance(img, Image):
        a = np.asarray(img)

    # a = cv2.cvtColor(a, cv2.COLOR_RGB2BGR)
    _, img_encode = cv2.imencode(format, a)

    return img_encode.tobytes()


def bytes2img(_bytes):
    import cv2

    np_arr = np.frombuffer(_bytes, dtype=np.uint8)
    # np.asarray(bytearray(bs), dtype=np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return img


def image_read(filename):
    import cv2

    filename = str(filename)
    _bytes = b''
    if filename.startswith('http'):
        _bytes = requests.get(filename, stream=True).content

    elif Path(filename).exists():
        _bytes = Path(filename).read_bytes()

    if _bytes:
        try:
            np_arr = np.frombuffer(_bytes, dtype=np.uint8)
            # np.asarray(bytearray(bs), dtype=np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            return img
        except Exception as e:
            logger.warning(e)
            return np.asarray((Image.open(io.BytesIO(_bytes)).convert('RGB')))


def base64_to_image(base64_str):
    """
    import jmespath
    d = json.load(open('clients.ipynb'))
    base64_str = jmespath.search('cells[*].attachments', d)[0]['27fa29dd-5f0a-48b0-8e76-334e70a23595.png']['image/png']

    """
    import cv2
    # 传入为RGB格式下的base64，传出为RGB格式的numpy矩阵
    byte_data = base64.b64decode(base64_str)  # 将base64转换为二进制
    encode_image = np.asarray(bytearray(byte_data), dtype="uint8")  # 二进制转换为一维数组
    img_array = cv2.imdecode(encode_image, cv2.IMREAD_COLOR)  # 用cv2解码为三通道矩阵
    img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)  # BGR2RGB
    return img_array


def image_to_base64(image_path_or_url, for_image_url: bool = True):
    content_type = mimetypes.guess_type('img.webp')[0] or "data:image/jpeg"

    if image_path_or_url.startswith('http'):
        data = httpx.get(image_path_or_url, follow_redirects=True, timeout=100).content
    else:
        data = Path(image_path_or_url).read_bytes()

    _ = base64.b64encode(data).decode('utf-8')
    if for_image_url:
        _ = f"data:{content_type};base64,{_}"
    return _


def base64_to_bytes(base64_image_string):
    """
    # 将字节数据写入图片文件
    image_data = base64_to_bytes(...)
    with open(filename, 'wb') as file:
        file.write(image_data)
    """
    return base64.b64decode(base64_image_string.split(",", 1)[1])


def file_to_base64(image_path, data_prefix: Optional[str] = None):
    _ = base64.b64encode(Path(image_path).read_bytes()).decode('utf-8')
    content_type = mimetypes.guess_type('img.webp')[0] or "data:image/jpeg"

    return f"data:{content_type},{_}"


def base64_to_file(base64_image_string, filename):
    image_data = base64_to_bytes(base64_image_string)
    with open(filename, 'wb') as file:
        file.write(image_data)


# alias
base64_to_img = base64_to_image

if __name__ == '__main__':
    url = "https://i1.mifile.cn/f/i/mioffice/img/slogan_5.png?1604383825042"
    #
    # print(image_read(url))
    # base64_image_string = image_to_base64("img.png").split(",")[1]
    # # print(base64_to_bytes(image_to_base64("img.png")))
    # image_data = base64.b64decode(base64_image_string)
    #
    # with open("demo1.png", 'wb') as file:
    #     file.write(base64_to_bytes(image_to_base64("img.png")))

    import mimetypes

    print(mimetypes.guess_type('img.webp')[0])
