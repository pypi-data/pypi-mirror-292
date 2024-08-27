from pathlib import Path
from cx_core.text.text_utils import quote_text
from .env import env
from .mission_maker import Mission


class ScriptWriter:
    def __init__(self, target) -> None:
        self.target = Path(target).absolute()
        self.output = None
        self.planned_folders = set()
        self.task = None

    def __enter__(self):
        self.task = env.progress.add_task(description="写入脚本文件…", total=None)
        self.output = open(self.target, "wt")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        result = False
        self.output.flush()
        self.output.close()
        env.print(f"脚本文件 [cyan]{self.target.absolute()}[/cyan] 已关闭")
        env.progress.stop_task(self.task)
        env.progress.remove_task(self.task)
        if exc_type is None:
            pass
        return result

    @staticmethod
    def compile_cmd(mission: Mission):
        line = [mission.ffmpeg]
        line += mission.general.iter_arguments()
        for i in mission.inputs:
            line += i.iter_arguments()
            line += ["-i", quote_text(i.filename)]
        for o in mission.outputs:
            line += o.iter_arguments()
            line.append(quote_text(o.filename))
        return " ".join([str(item) for item in line if item is not None])

    def write(self, mission: Mission):
        env.progress.update(
            self.task,
            description=f"正在为[cyan]{mission.source.name}[/cyan]检测目标目录…",
        )
        for o in mission.outputs:
            folder = o.filename.parent
            if folder not in self.planned_folders:
                self.output.write(f"mkdir -p {quote_text(folder.absolute())}\n")
                self.planned_folders.add(folder)
                env.debug(f"添加新建目录指令:{folder}")

        env.progress.update(
            self.task, description=f"为[cyan]{mission.source.name}[/cyan]写入命令…"
        )
        cmd = ScriptWriter.compile_cmd(mission)
        self.output.write(f"{cmd}\n")
        env.info(f"写入命令 [purple]{cmd}[/purple]")

    def write_all(self, missions: list[Mission]):
        for m in env.progress.track(missions, task_id=self.task):
            self.write(m)
