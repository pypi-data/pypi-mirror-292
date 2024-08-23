from ffmpeg import Progress
from ffmpeg.asyncio import FFmpeg
from ffmpeg.errors import FFmpegError
from pathlib import Path
import json, asyncio
from cx_core.filesystem.path_utils import is_file_in_dir
from cx_core import DataPackage
from .env import env
from .mission_maker import Mission


class Transcoder:
    def __init__(self, mission: Mission) -> None:
        self.task = None
        self.mission = mission
        self.is_valid = True
        self.media_info = None
        self.ffmpeg = None
        self.duration = None

    def __enter__(self):
        self.task = env.progress.add_task(
            description=self.mission.source.name, visible=False, total=None
        )

        for o in self.mission.outputs:
            f = o.filename
            if f.exists() and not self.mission.overwrite:
                env.warning(f"目标文件[red]{f}[/red]已存在且不可覆盖，该任务无法执行")
                self.is_valid = False
                break

        for i in self.mission.inputs:
            if not i.filename.exists():
                env.warning(f"文件[red]{i.filename}[/red]不存在，该任务无法执行")
                self.is_valid = False
                break
            if is_file_in_dir(i.filename, self.mission.target_folder):
                env.warning(
                    f"文件[red]{i.filename}[/red]存在于目标目录中，此任务无法执行"
                )
                self.is_valid = False
                break

        ffprobe_bin = Path(str(self.mission.ffmpeg).replace("ffmpeg", "ffprobe"))
        probe_file = self.mission.source
        if not probe_file.exists():
            probe_file = None
            for f in self.mission.inputs:
                if f.filename.exists():
                    probe_file = f.filename
                    break

        if not probe_file:
            env.warning(
                f"从源文件[red]{self.mission.source.name}[/red]获取媒体元数据失败"
            )
        else:
            ffprobe = FFmpeg(executable=ffprobe_bin).input(
                probe_file, print_format="json", show_format=None
            )
            media = None
            try:
                media = json.loads(asyncio.run(ffprobe.execute()))
            finally:
                if (media is not None) and any(media):
                    self.media_info = DataPackage(**media)
                else:
                    env.warning(
                        f"无法为[cyan]{self.mission.source.name}[/cyan]读取元数据，无法进行时间估计"
                    )

        if self.media_info:
            self.duration = float(self.media_info.format.duration)
            env.progress.update(self.task, total=float(self.duration))

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        result = False
        if exc_type is None:
            pass
        elif issubclass(exc_type, FFmpegError):
            env.critical(f"FFMPEG执行出错：[red]{exc_val}[/red]")
            result = True
        env.progress.stop_task(self.task)
        env.progress.remove_task(self.task)
        return result

    async def transcode(self):
        if env.wanna_quit:
            env.debug(f"检测到用户中断，直接跳过任务")
            return

        if not self.is_valid:
            env.debug(f"任务非法，跳过执行")
            return

        env.progress.update(
            self.task, description="检查目标目录可用性…", completed=0.0, visible=True
        )
        env.progress.start_task(self.task)
        for o in self.mission.outputs:
            f = o.filename.parent
            if not f.exists():
                f.mkdir(parents=True, exist_ok=True)
                env.debug(f"创建文件夹{f}")

        self.ffmpeg = FFmpeg(self.mission.ffmpeg)
        env.debug(f"创建ffmpeg对象 {self.ffmpeg} ({self.mission.ffmpeg})")

        env.progress.update(self.task, description="写入全局参数…")
        for k, v in self.mission.general.iter_options():
            self.ffmpeg.option(k, v)
            env.debug(f"写入全局选项: [blue]{k}[/blue] : [yellow]{v}[/yellow]")

        for i in env.progress.track(
            self.mission.inputs, task_id=self.task, description="写入输入参数…"
        ):
            self.ffmpeg.input(i.filename.absolute(), i.data)
            env.debug(f"为[cyan]{i.filename}[/cyan]添加输入选项：{i.data}")

        for o in env.progress.track(
            self.mission.outputs, task_id=self.task, description="写入输出参数…"
        ):
            self.ffmpeg.output(o.filename.absolute(), o.data)
            env.debug(f"为[cyan]{o.filename}[/cyan]添加输出选项：{o.data}")

        env.progress.update(self.task, description="设置事件监听器…")

        @self.ffmpeg.on("progress")
        def on_progress(progress: Progress):
            desc = f"{self.mission.source.name} [yellow]x{progress.speed:.2f}[/yellow] [green]{progress.bitrate:.2f}k/s[/green]"
            current = progress.time.total_seconds()
            env.progress.update(
                self.task,
                description=desc,
                completed=float(current),
                total=self.duration,
            )
            if env.wanna_quit:
                self.ffmpeg.terminate()

        @self.ffmpeg.on("stderr")
        def on_stderr(line):
            env.debug(f"[grey]FFMPEG标准错误：[/grey]{line}")

        @self.ffmpeg.on("start")
        def on_start(arguments):
            env.debug(f"FFMPEG启动：[grey]{" ".join(arguments)}[/grey]")

        @self.ffmpeg.on("completed")
        def on_completed():
            env.debug(f"[green]{self.mission.source.name}[/green]执行完毕")
            env.progress.update(self.task, description="转码完成")

        @self.ffmpeg.on("terminated")
        def on_terminated():
            env.warning("[purple]FFMPEG被终止[/purple]")
            env.progress.update(self.task, description="尝试移除未完成的目标文件…")
            for t in self.mission.outputs:
                f = t.filename
                if f.exists:
                    f.unlink(missing_ok=True)
                    env.print(f"移除未完成的目标文件[red]{f}[/red]")

        try:
            env.progress.update(self.task, description="正在启动…")
            await self.ffmpeg.execute()
        except FFmpegError as e:
            env.error(f"FFMPEG运行异常：[red]{e.message}[/red]")
            self.ffmpeg.terminate()

    def run(self):
        asyncio.run(self.transcode())
