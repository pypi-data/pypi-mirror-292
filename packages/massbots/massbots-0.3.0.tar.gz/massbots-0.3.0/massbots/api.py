import time
import typing
from typing import Callable

from massbots.openapi import ApiClient
from massbots.openapi import Configuration as ApiConfig
from massbots.openapi import ApiGroup, YoutubeGroup, DownloadGroup

from massbots.error import error_wrap
from massbots.models import yt, dl


def class_cast(cls):
    def decorator(func):
        def wrapper(*args, **kwargs):
            r = func(*args, **kwargs)
            r = typing.cast(cls, r)
            r.__class__ = cls
            return r

        return wrapper

    return decorator


class Api:
    def __init__(self, token):
        config = ApiConfig(host="https://api.massbots.xyz")
        config.api_key["Token"] = token
        self._client = ApiClient(config)
        self._api = ApiGroup(self._client)

    @error_wrap
    def balance(self) -> int:
        r = self._api.balance_get()
        return r.balance

    class ApiYoutube:
        def __init__(self, api: YoutubeGroup):
            self._api = api

        @error_wrap
        @class_cast(yt.Video)
        def video(self, video_id) -> yt.Video:
            return self._api.yt_video_id_get(video_id)

        @error_wrap
        @class_cast(yt.Channel)
        def channel(self, channel_id) -> yt.Channel:
            return self._api.yt_channel_id_get(channel_id)

        @error_wrap
        @class_cast(list[yt.Video])
        def search(self, query) -> list[yt.Video]:
            return self._api.yt_search_get(query)

    class ApiDownload:
        def __init__(self, api: DownloadGroup):
            self._api = api

        @error_wrap
        @class_cast(dl.Video)
        def video(self, video_id) -> dl.Video:
            return self._api.dl_video_id_get(video_id)

        @error_wrap
        def video_cached(self, video_id, format) -> str:
            r = self._api.dl_video_id_cached_f_get(video_id, format)
            return r.file_id

        @error_wrap
        @class_cast(dl.Result)
        def _video_download(self, video_id, format) -> dl.Result:
            return self._api.dl_video_id_download_f_get(video_id, format)

        class Result(dl.Result):
            def __init__(self, r: dl.Result, g, video_id, format):
                super().__init__(**r.to_dict())
                self._g = g
                self._video_id = video_id
                self._format = format

            def wait_until_ready(
                self,
                delay: float = 5.0,
                callback: Callable[[dl.Result], bool] = None,
            ) -> dl.Result:
                """
                Waits until the download result is ready or failed.

                Args:
                    delay (float): Interval between polling requests. Default is 5.0 seconds.
                    callback (Callable[[dl.Result], bool]): Callback function for each iteration.
                """
                if not delay or delay <= 0:
                    delay = 1.0

                while True:
                    r = self._g._video_download(self._video_id, self._format)
                    if callback and callback(r):
                        return r
                    if r.status in ("ready", "failed"):
                        return r
                    time.sleep(delay)

        def video_download(self, video_id, format) -> Result:
            r = self._video_download(video_id, format)
            return self.Result(r, self, video_id, format)

    @property
    def yt(self):
        return self.ApiYoutube(YoutubeGroup(self._client))

    @property
    def dl(self):
        return self.ApiDownload(DownloadGroup(self._client))
