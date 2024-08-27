from pathlib import Path
import subprocess
from collections import defaultdict
from .env import env
from functools import cache
from typing import Union, Iterable
from ffmpeg import FFmpeg
import json
from cx_core import DataPackage


class FFmpegChecker:
    @staticmethod
    def check_ffmpeg_binary(ff) -> bool:
        result = subprocess.run([str(ff), "-L"], check=False)
        return result.returncode == 0

    def __init__(self) -> None:
        self.caches = defaultdict(bool)

    def __call__(self, ffmpeg) -> bool:
        key = str(ffmpeg)
        env.debug(f"检查ffmpeg合法性：{key}…")
        if key not in self.caches:
            self.caches[key] = FFmpegChecker.check_ffmpeg_binary(key)
        return self.caches[key]


class DurationManager:
    _cache = defaultdict(float)

    def __init__(self, ffmpeg) -> None:
        self.ffmpeg = str(ffmpeg)

    @property
    @cache
    def ffprobe(self):
        if "ffmpeg" in self.ffmpeg:
            return self.ffmpeg.replace("ffmpeg", "ffprobe")
        return "ffprobe"

    def _probe_file(self, source: Path) -> float:
        source = Path(source)
        if not source.exists():
            return 0
        result = 0
        try:
            ff = FFmpeg(executable=self.ffprobe).input(
                source, print_format="json", show_format=None
            )
            data = json.loads(ff.execute())
            mediainfo = DataPackage(**data)
            if any(mediainfo):
                result = float(mediainfo.format.duration)
        except:
            pass
        finally:
            return result

    def _check_duration(self, source: Path) -> float:
        key = str(source.resolve())
        if key not in self._cache:
            self._cache[key] = self._probe_file(source)
        return self._cache[key]

    def duration(self, source: Union[Path | Iterable]) -> float:
        sources = []
        if isinstance(source, Iterable):
            sources = [Path(x) for x in source]
        else:
            sources = [Path(str(source))]

        durations = map(self._check_duration, sources)
        return max(durations)
