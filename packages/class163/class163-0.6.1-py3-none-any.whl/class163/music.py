"""
class163/music.py
Version: 0.6.1
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
from class163.common import BasicMusicType, extract, extract_in_list
from typing import Optional, Dict, List, Union, Type


class Music(BasicMusicType):
    def __init__(self, id: int | str) -> None:
        """
        初始化 Music 类实例。
        :param id: 音乐的 ID，可以是整数或字符串。如果是包含"music.163.com"的 URL，则从 URL 中提取歌曲 ID。
        """
        super().__init__()
        self.id = str(id)
        if self.id.find("music.163.com") != -1:
            self.id = url_to_id(self.id)
        self.encode_session = EncodeSession()
        self.__detail_encode_data = {
            "c": str([{"id": self.id}]),
        }
        self.__lyric_encode_data = {
            "id": self.id,
            "lv": -1,
            "tv": -1,
        }
        self.__file_encode_data = {
            "ids": str([self.id]),
            "level": None,
            "encodeType": None,
        }
        self.lyric_info_raw: dict = {}
        self.detail_info_raw: dict = {}
        self.file_info_raw: dict = {}
        self.lyric = None
        self.trans_lyric = None
        self.trans_lyric_uploader = None
        self.lyric_update_time = None
        self.file_md5 = None
        self.file_size = None
        self.file_url = None

    def get(
        self,
        mode: MODE = "d",
        encode_session: EncodeSession = None,
        level: LEVEL = "standard",
        offical: bool = True,
        url: str = None,
        cookies: Dict = None,
        method: str = "get",
        url_keys: List[Union[str, int]] = [],
        md5_keys: List[Union[str, int]] = [],
        size_keys: List[Union[str, int]] = [],
        **kwargs
    ) -> Optional[Dict]:
        """
        获取音乐信息。
        :param mode: 获取模式，默认为"d"，表示获取详细信息。
        :param encode_session: 编码会话实例，默认为 None。
        :param level: 音乐品质，默认为"standard"。
        :param offical: 是否为官方版本，默认为 True。
        :param url: 外部链接，默认为 None。
        :param cookies: 字典形式的 cookies，默认为 None。
        :param method: 请求方法，默认为"get"。
        :param kwargs: 其他关键字参数。
        :return: 音乐信息字典。
        """
        if encode_session is None:
            encode_session = self.encode_session
        result = {}
        if "d" in mode:
            result.update(self.get_detail(encode_session=encode_session))
        if "l" in mode:
            result.update(self.get_lyric(encode_session=encode_session))
        if "f" in mode:
            result.update(
                self.get_file(
                    encode_session=encode_session,
                    cookies=cookies,
                    url=url,
                    level=level,
                    offical=offical,
                    method=method,
                    kwargs=kwargs,
                    url_keys=url_keys,
                    md5_keys=md5_keys,
                    size_keys=size_keys,
                )
            )
        return result

    def get_file(
        self,
        url_keys: List[Union[str, int]],
        md5_keys: List[Union[str, int]],
        size_keys: List[Union[str, int]],
        url: str = None,
        offical: bool = True,
        level: LEVEL = "standard",
        encode_session: EncodeSession = None,
        cookies: Dict = None,
        method: str = "get",
        **kwargs
    ) -> Optional[Dict]:
        """
        获取音乐文件信息
        :param url: 第三方文件的 URL
        :param offical: 是否获取官方文件
        :param level: 音乐品质
        :param encode_session: 编码会话，如果未提供则使用实例中的会话
        :param cookies: Cookie 字典
        :param method: 请求方法
        :param url_key: 用于提取文件 URL 的键列表
        :param md5_key: 用于提取文件 MD5 的键列表
        :param size_key: 用于提取文件大小的键列表
        :param kwargs: 其他关键字参数
        :return: 文件信息字典
        """
        if encode_session is None:
            encode_session = self.encode_session
        if offical:
            return self.__get_file_offical(encode_session=encode_session, level=level)
        else:
            return self.__get_file_third_party(
                url=url,
                cookies=cookies,
                method=method,
                url_keys=url_keys,
                md5_keys=md5_keys,
                size_keys=size_keys,
                kwargs=kwargs,
            )

    def __get_file_third_party(
        self,
        method: str,
        url: str,
        cookies: dict,
        url_keys: List[Union[str, int]],
        md5_keys: List[Union[str, int]],
        size_keys: List[Union[str, int]],
        **kwargs
    ) -> Optional[Dict]:
        """
        从第三方获取文件信息
        :param method: 请求方法
        :param url: URL
        :param cookies: Cookie 字典
        :param url_key: 用于提取文件 URL 的键列表
        :param md5_key: 用于提取文件 MD5 的键列表
        :param size_key: 用于提取文件大小的键列表
        :param kwargs: 其他关键字参数
        :return: 文件信息字典
        """
        session = Session()
        session.cookies = cookiejar_from_dict(cookie_dict=cookies)
        data = {}
        data.update(**kwargs)
        response = session.request(method=method, url=url, data=data).json()
        result = self.extract_file(response, url_keys, md5_keys, size_keys)
        return result

    def __get_file_offical(
        self, encode_session: EncodeSession = None, level: LEVEL = "standard"
    ) -> Optional[Dict]:
        """
        从官方获取音乐文件信息
        :param encode_session: 编码会话，如果未提供则使用实例中的会话
        :param level: 音乐品质
        :return: 文件信息字典
        """
        if encode_session is None:
            encode_session = self.encode_session
        if level in ["standard", "higher", "exhigh"]:
            self.__file_encode_data["encodeType"] = "mp3"
        else:
            self.__file_encode_data["encodeType"] = "aac"
        self.__file_encode_data["level"] = level
        self.file_info_raw = encode_session.get_response(
            url=FILE_URL,
            encode_data=self.__file_encode_data,
        )["data"][0]
        result = self.extract_file(self.file_info_raw)
        return result

    def extract_file(
        self,
        origin: Dict,
        url_keys: List[Union[str, int]] = ["url"],
        md5_keys: List[Union[str, int]] = ["md5"],
        size_keys: List[Union[str, int]] = ["size"],
    ) -> Optional[Dict]:
        self.file_url = str(extract(origin, url_keys, str))
        if self.file_url.find("?authSecret") != -1:
            self.file_url = self.file_url[: self.file_url.find("?authSecret")]
        self.file_md5 = extract(origin, md5_keys, str)
        self.file_size = extract(origin, size_keys, int)
        result = {
            "file_url": self.file_url,
            "file_md5": self.file_md5,
            "file_size": self.file_size,
        }
        return result

    def get_detail(
        self,
        encode_session: EncodeSession = None,
    ) -> Optional[Dict]:
        """
        获取音乐详细信息。
        :param encode_session: 编码会话实例，默认为 None。
        :return: 音乐详细信息字典或 None。
        """
        if encode_session is None:
            encode_session = self.encode_session
        self.detail_info_raw = encode_session.get_response(
            url=DETAIL_URL,
            encode_data=self.__detail_encode_data,
        )["songs"][0]
        origin = self.detail_info_raw
        result = self.extract_detail(origin=origin)
        return result

    def extract_detail(
        self,
        origin: Dict,
        id_keys: List[Union[str, int]] = ["id"],
        title_keys: List[Union[str, int]] = ["name"],
        album_keys: List[Union[str, int]] = ["al", "name"],
        subtitle_keys: List[Union[str, int]] = ["alia", 0],
        trans_title_keys: List[Union[str, int]] = ["tns", 0],
        trans_album_keys: List[Union[str, int]] = ["al", "tns", 0],
        artist_list_keys: List[Union[str, int]] = ["ar"],
        artist_keys: List[Union[str, int]] = ["name"],
        trans_artist_keys: List[Union[str, int]] = ["tns"],
        publish_time_keys: List[Union[str, int]] = ["publishTime"],
    ) -> Optional[Dict]:
        """
        从原始的详细信息中提取所需信息。
        :param origin: 原始的详细信息字典。
        :param id_keys: 用于提取音乐 ID 的键列表，默认为["id"]。
        :param title_keys: 用于提取音乐标题的键列表，默认为["name"]。
        :param album_keys: 用于提取音乐专辑的键列表，默认为["al", "name"]。
        :param subtitle_keys: 用于提取音乐副标题的键列表，默认为["alia", 0]。
        :param trans_title_keys: 用于提取音乐翻译标题的键列表，默认为["tns", 0]。
        :param trans_album_keys: 用于提取音乐翻译专辑的键列表，默认为["al", "tns", 0]。
        :param artist_list_keys: 用于提取音乐歌手列表的键列表，默认为["ar"]。
        :param artist_keys: 用于提取音乐歌手的键列表，默认为["name"]。
        :param trans_artist_keys: 用于提取音乐翻译歌手的键列表，默认为["tns"]。
        :param publish_time_keys: 用于提取音乐发布时间的键列表，默认为["publishTime"]。
        :return: 提取后的音乐详细信息字典或 None。
        """
        self.id = extract(origin, id_keys, int)
        self.title = extract(origin, title_keys, str)
        self.album = extract(origin, album_keys, str)
        self.subtitle = extract(origin, subtitle_keys, str)
        self.trans_title = extract(origin, trans_title_keys, str)
        self.trans_album = extract(origin, trans_album_keys, str)
        artists = extract(origin, artist_list_keys, list)
        self.artist = extract_in_list(artists, artist_keys, str)
        self.trans_artist = extract_in_list(artists, trans_artist_keys, str)
        publish_time = time.localtime(
            int(extract(origin, publish_time_keys, int)) / 1000
        )
        self.publish_time = list(publish_time[0:3])
        return self.info_dict()

    def get_lyric(self, encode_session: EncodeSession = None) -> Optional[Dict]:
        """
        获取音乐歌词信息。
        :param encode_session: 编码会话实例，默认为 None。
        :return: 音乐歌词信息字典或 None。
        """
        if encode_session is None:
            encode_session = self.encode_session
        self.lyric_info_raw = encode_session.get_response(
            url=LYRIC_URL,
            encode_data=self.__lyric_encode_data,
        )
        origin = self.lyric_info_raw
        result = self.extract_lyric(origin)
        return result

    def extract_lyric(
        self,
        origin: Dict,
        lyric_keys: List[Union[str, int]] = ["lrc", "lyric"],
        trans_lyric_keys: List[Union[str, int]] = ["tlyric", "lyric"],
        trans_lyric_uploader_keys: List[Union[str, int]] = ["transUser", "nickname"],
        lyric_update_time_keys: List[Union[str, int]] = ["transUser", "uptime"],
    ) -> Optional[Dict]:
        """
        从原始的歌词信息中提取所需信息。
        :param origin: 原始的歌词信息字典。
        :param lyric_keys: 用于提取歌词的键列表，默认为["lrc", "lyric"]。
        :param trans_lyric_keys: 用于提取翻译歌词的键列表，默认为["tlyric", "lyric"]。
        :param trans_lyric_uploader_keys: 用于提取翻译歌词上传者的键列表，默认为["transUser", "nickname"]。
        :param lyric_update_time_keys: 用于提取歌词更新时间的键列表，默认为["transUser", "uptime"]。
        :return: 提取后的音乐歌词信息字典或 None。
        """
        self.lyric = extract(origin, lyric_keys, str)
        self.trans_lyric = extract(origin, trans_lyric_keys, str)
        self.trans_lyric_uploader = extract(origin, trans_lyric_uploader_keys, str)
        lyric_update_time = time.localtime(
            int(extract(origin, lyric_update_time_keys, int)) / 1000
        )
        self.lyric_update_time = list(lyric_update_time[0:5])
        result = {
            "lyric": self.lyric,
            "trans_lyric": self.trans_lyric,
            "trans_lyric_uploader": self.trans_lyric_uploader,
            "lyric_update_time": self.lyric_update_time,
        }
        return result


def url_to_id(url: str) -> str:
    """
    从给定的 URL 中提取歌曲 ID。
    :param url: 包含歌曲 ID 的 URL。
    :return: 提取出的歌曲 ID。
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
    将歌手列表连接为一个字符串。
    :param artist: 歌手列表。
    :param separator: 分隔符，默认为", "。
    :return: 连接后的字符串。
    """
    artist_str = ""
    for i in artist[:-1]:
        artist_str += i + separator
    artist_str += artist[-1]
    return artist_str
