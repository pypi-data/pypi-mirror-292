"""
class163/music.py
Version: 0.5.0
Author: CooooldWind_/豆包@字节跳动
E-Mail: 3091868003@qq.com
Copyright @CooooldWind_ / Following GNU_AGPLV3+ License
"""

import time
from netease_encode_api import EncodeSession
from urllib.parse import urlparse, parse_qs
from class163.global_args import *
from requests import Session
from requests.cookies import cookiejar_from_dict
from class163.common import BasicMusicType
from typing import Optional, Dict, List, Union, Type


class Music(BasicMusicType):
    def __init__(self, id: int | str) -> None:
        super().__init__()
        self.id = str(id)
        if self.id.find("music.163.com") != -1:
            self.id = url_to_id(self.id)
        self.encode_session = EncodeSession()  # 创建解码会话
        # 详细信息相关的初始化
        self.__detail_encode_data = {
            "c": str([{"id": self.id}]),
        }
        # 歌词相关的初始化
        self.__lyric_encode_data = {
            "id": self.id,
            "lv": -1,
            "tv": -1,
        }
        # 音乐文件相关的初始化
        """
        id 表示歌曲的 id 号,
        level 是音乐品质,
        标准为 standard,
        较高音质为 higher,
        极高音质 exhigh,
        无损音质关键词为 lossless。
        """
        self.__file_encode_data = {
            "ids": str([self.id]),
            "level": None,  # standard/higher/exhigh/lossless
            "encodeType": None,  # 如果是 lossless 就用 aac, 其他是 mp3
        }
        self.lyric_info_raw: dict = {}  # 原始的歌词信息数据
        self.detail_info_raw: dict = {}  # 原始的详细信息数据
        self.file_info_raw: dict = {}  # 原始的文件信息数据

    def get(
        self,
        mode: MODE = "d",
        encode_session: EncodeSession = None,
        level: LEVEL = "standard",
        offical: bool = True,
        # 如果使用外部链接
        url: str = None,
        cookies: dict = None,
        method: str = "get",
        **kwargs
    ) -> Dict:
        if encode_session is None:
            encode_session = self.encode_session
        if "d" in mode:
            self.get_detail(encode_session=encode_session)

    def get_detail(
        self,
        encode_session: EncodeSession = None,
    ) -> Dict:
        if encode_session is None:
            encode_session = self.encode_session
        self.detail_info_raw = encode_session.get_response(
            url=DETAIL_URL,
            encode_data=self.__detail_encode_data,
        )["songs"][0]
        result = {
            "title": self.extract(
                origin_dict=self.detail_info_raw, keys=["name"], expected_type=str
            ),
            "subtitle": self.extract(
                origin_dict=self.detail_info_raw,
                keys=["alia", 0],
                expected_type=str,
            ),
            "artist": self.extract_in_list(
                origin_list=self.extract(
                    origin_dict=self.detail_info_raw,
                    keys=["ar"],
                    expected_type=list,
                ),
                keys=["name"],
                expected_type=str,
            ),
            "album": self.extract(
                origin_dict=self.detail_info_raw,
                keys=["al", "name"],
                expected_type=str,
            ),
            "trans_title": self.extract(
                origin_dict=self.detail_info_raw, keys=["tns", 0], expected_type=str
            ),
            "trans_artist": self.extract_in_list(
                origin_list=self.extract(
                    origin_dict=self.detail_info_raw,
                    keys=["ar"],
                    expected_type=list,
                ),
                keys=["tns"],
                expected_type=str,
            ),
            "trans_album": self.extract(
                origin_dict=self.detail_info_raw,
                keys=["al", "tns"],
                expected_type=str,
            ),
        }
        self.info.update(result)
        return result


def url_to_id(url: str) -> str:
    """
    从给定的 URL 中提取歌曲 ID
    :param url: 包含歌曲 ID 的 URL
    :return: 提取出的歌曲 ID
    """
    try:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        song_id = query_params.get("id", [None])[0]
        if song_id is not None:
            return str(song_id)
        else:
            raise ValueError("URL 中未找到 'id' 参数")
    except (ValueError, TypeError) as e:
        raise e


def artist_join(artist: list[str], separator: str = ", ") -> str:
    """
    将歌手列表连接为一个字符串
    :param artist: 歌手列表
    :param separator: 分隔符，默认为", "
    :return: 连接后的字符串
    """
    artist_str = ""
    for i in artist[:-1]:
        artist_str += i + separator
    artist_str += artist[-1]
    return artist_str
