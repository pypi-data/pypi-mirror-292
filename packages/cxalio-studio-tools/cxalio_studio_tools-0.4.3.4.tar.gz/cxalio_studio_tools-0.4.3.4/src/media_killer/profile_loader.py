from pathlib import Path
from .env import env
from cx_core.misc import DataPackage
import tomllib


class ProfileLoader:
    def __init__(self, filename: Path, args: DataPackage = None) -> None:
        self.task = None
        self.filename = filename
        self.args = args

    def __enter__(self):
        self.task = env.progress.add_task(
            "解析配置：[yellow]{self.filename}[/yellow]",
            start=False,
            visible=True,
            total=None,
        )
        return self

    def __exit__(self, a, b, c):
        env.progress.stop_task(self.task)
        env.progress.remove_task(self.task)
        return False

    def load(self) -> DataPackage:
        data = {}
        env.progress.start_task(self.task)
        with env.progress.open(self.filename, "rb", task_id=self.task) as f:
            data.update(tomllib.load(f))
        data["path"] = Path(self.filename).resolve()
        env.debug("toml解析结果", data)

        result = DataPackage(**data)
        env.print(
            f"发现配置文件 <[cyan]{result.general.name}[/cyan]> [yellow]{result.general.description}[/yellow]"
        )

        if self.args and self.args.output_dir:
            result.target.folder = (
                Path(self.args.output_dir) / Path(result.target.folder).name
            ).resolve()
            env.print(
                f"因指定了输出目录，配置文件的输出位置将被设置为: [green]{result.target.folder}[/green]"
            )

        if not result.general.ffmpeg:
            result.general.ffmpeg = "ffmpeg"
            env.print("使用系统环境中的 ffmpeg")

        if result.general.overwrite is None:
            result.general.overwrite = False
            env.print("未指定覆写模式，默认关闭")

        if not result.target.folder:
            result.target.folder = "."
            env.print("未指定目标目录，将使用当前工作目录")

        if not result.target.keep_parent_level:
            result.target.keep_parent_level = 0
            env.print("未指定目标父目录保留层级，默认不保留")

        result.path = Path(self.filename)

        env.debug(f"参数包解析结果：{result}")
        return result
