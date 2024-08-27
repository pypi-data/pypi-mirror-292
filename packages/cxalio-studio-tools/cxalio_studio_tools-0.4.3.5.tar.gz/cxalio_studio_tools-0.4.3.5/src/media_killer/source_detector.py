from cx_core.filesystem import PathExpander, SuffixValidator
from pathlib import Path
from typing import Iterable
from .env import env
from . import source_adapter as Adapters
import concurrent.futures


class SourceDetector:
    DEFAULT_SUFFIXES = {
        ".mov",
        ".mkv",
        ".mp4",
        ".flv",
        ".3gp",
        ".3gpp",
        ".rmvb",
        ".mp3",
        ".aac",
        ".mxf",
        ".mxf_op1a",
        ".vob",
        ".wmv",
        ".wma",
        ".srt",
        ".ass",
        ".aas",
        ".ttml",
        ".ogg",
        ".oga",
        ".ogv",
        ".m4a",
        ".m4v",
        ".3g2",
        ".mpeg",
        ".mpg",
        ".ts",
        ".lrc",
        ".h264",
        ".flac",
        ".ast",
        ".asf",
        ".gif",
    }

    ADDITIONAL_SUFFIXES = {".xml", ".txt", "csv"}

    def __init__(self, args=None) -> None:
        self.args = args
        self.task = None
        self.exp_settings = None
        self._sources = set()

    def __enter__(self):
        self.task = env.progress.add_task("解析源路径")
        suffixes = SourceDetector.DEFAULT_SUFFIXES
        if self.args.source:
            includes = {
                "." + str(x).strip().strip(".")
                for x in self.args.source.suffix_includes
            }
            excludes = {
                "." + str(x).strip().strip(".")
                for x in self.args.source.suffix_excludes
            }
            if self.args.ignore_default_suffixes:
                suffixes.clear()
            suffixes = suffixes | includes - excludes
        self.acceptable_suffixes = suffixes
        env.debug("最终的可接受扩展名白名单为：", self.acceptable_suffixes)
        self.exp_settings = PathExpander.Settings(
            file_validator=SuffixValidator(self.acceptable_suffixes), accept_dir=False
        )
        return self

    def __exit__(self, et, ev, eb):
        env.progress.remove_task(self.task)
        return False

    def detect(self, source):
        source = Path(source)
        if not source.exists():
            return

        new_tasks = []

        env.progress.update(self.task, description="正在探测文件…")

        if source.is_dir():
            expander = PathExpander(source, self.exp_settings)
            new_tasks += [x for x in expander]
            env.print(f"探测到[cyan]{len(new_tasks)}[/cyan]个有效的文件")
        else:
            suffix = source.suffix.lower().strip(".")
            if suffix in Adapters.adapters:
                with Adapters.adapters[suffix](source) as adapter:
                    new_tasks += adapter.items()
            else:
                new_tasks.append(source)

        env.progress.update(self.task, completed=0, total=len(new_tasks))
        for t in new_tasks:
            tt = Path(t)
            self._sources.add(tt)
            env.progress.update(self.task, description=tt.name)
            env.progress.advance(self.task)

    def arrange_tasks(self):
        def filter_task(task):
            a = Path(task)
            if a.exists and a.is_file:
                suffix = a.suffix.lower()
                if suffix in self.acceptable_suffixes:
                    return a
            return None

        env.progress.update(self.task, description="正在整理任务列表…")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            _checked_tasks = executor.map(filter_task, self._sources)
            filtered_tasks = {x for x in _checked_tasks if x is not None}

        env.print(f"整理完成后，共有[cyan]{len(filtered_tasks)}[/cyan]个待处理文件")
        self._sources = filtered_tasks
        return self._sources
