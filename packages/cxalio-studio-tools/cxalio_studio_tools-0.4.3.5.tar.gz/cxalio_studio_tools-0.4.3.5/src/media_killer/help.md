# MediaKiller

当前版本 0.4.0

MediaKiller 可以通过配置文件操纵 ffmpeg 批量地对大量媒体文件转码。

> MediaKiller 并不能作为 ffmpeg 的替代。

和直接使用 ffmpeg 相比， MediaKiller 有如下优缺点：

- 可以进行大量视频批量处理
- 使用 **可复用的配置文件** 进行操作管理
- 每个转码任务可以通过文本模板的形式支持多文件输入和多文件输出
- 可以通过指定文件夹作为源文件的方式来批量添加任务
- 可以根据源文件路径保留指定层级的上层目录结构
- 可以读取`xml`、`fcpxml`、`csv`等文件中提供的源文件信息
- 拥有漂亮的进度监控和提示信息

*目录*
<!-- vscode-markdown-toc -->
* 1. [基本使用说明](#)
	* 1.1. [生成配置文件](#-1)
	* 1.2. [执行任务](#-1)
		* 1.2.1. [来源文件的解析](#-1)
		* 1.2.2. [相对路径 vs 绝对路径](#vs)
	* 1.3. [生成可执行脚本](#-1)
	* 1.4. [调试与测试](#-1)
* 2. [配置文件详解](#-1)
	* 2.1. [配置文件结构](#-1)
		* 2.1.1. [general](#general)
		* 2.1.2. [custom](#custom)
		* 2.1.3. [source](#source)
		* 2.1.4. [target](#target)
		* 2.1.5. [input 组 和 output 组](#inputoutput)
	* 2.2. [数据标签](#-1)

<!-- vscode-markdown-toc-config
	numbering=true
	autoSave=true
	/vscode-markdown-toc-config -->
<!-- /vscode-markdown-toc -->

##  1. <a name=''></a>基本使用说明

###  1.1. <a name='-1'></a>生成配置文件

MediaKiller 使用`toml配置文件`描述工作内容。

使用配置文件可以方便地复用设置，
你可以保存多个不同的配置文件，并在将来对不同的视频文件进行同样的操作；
或者是在源文件修改后，一键重新运行转码任务，以快速更新目标文件。

使用 `--generate` 选项生成一个示例文件：

```shell
mediakiller '文件名.toml' --generate
# 或
mediakiller '文件名.toml' -g
```

> 在示例文件中包含所有选项的说明。

###  1.2. <a name='-1'></a>执行任务

不加任何选项地，指定配置文件和源文件即可开始执行。

```shell
mediakiller '配置文件.toml' '需要转码的文件.mp4' 
# 可以有多个配置文件和来源文件
```

> 配置文件中不包含来源文件的信息。

####  1.2.1. <a name='-1'></a>来源文件的解析

在使用来源文件之前，MediaKiller 将会进行一系列处理：

1. 从输入的一堆文件中筛选`配置文件`，并解析它们

2. 初始化`扩展名列表`，
    - 将`配置文件`中的`input.suffix_includes`添加到`扩展名列表`，
    - 将`配置文件`中的`input.suffix_excludes`中包含的项目从`扩展名列表`中移除
    - 如果在`配置文件`中设置了忽略默认扩展名列表，则初始化的扩展名列表为空，这时如果不指定上面两项内容的话，则不会处理任何文件

4. 遍历所有来源路径，并将所有的文件夹递归地展开，
   并将扩展名符合`扩展名列表`的文件添加到`源文件列表`

5. 根据路径排序`源文件列表`，并去除重复的或不存在的文件

6. 将每个`配置文件`应用到每个`来源文件`中，并创建`任务`

之后将会依次执行`任务`。

####  1.2.2. <a name='vs'></a>相对路径 vs 绝对路径

无论配置文件中，还是指定的来源路径列表，都可以使用相对路径或绝对路径。

相对路径将会相对于当前工作目录进行解析。

###  1.3. <a name='-1'></a>生成可执行脚本

如果指定了`--make-script`选项，
MediaKiller 不会自动转码，而是会生成一个脚本文件。
当然，**必须指定脚本文件的保存位置**。

你可以使用任何手段对脚本文件进行编辑，
也可以将脚本文件复制到没有安装 MediaKiller 的环境中运行。

```shell
mediakiller 'example.toml' --make-script 'script.sh'
# 或
mediakiller 'example.toml' -s 'script.ps1'
# -s 是 --make-script 的缩写
```

生成的脚本文件仅仅是普通的文本文件而已，
既**不包含 shebang**，也**没有运行权限**。
所以运行时你需要自己指定使用的 shell：

```shell
media 'example.toml' --make-script 'script.ps1'
pwsh 'script.ps1'
```

###  1.4. <a name='-1'></a>调试与测试

MediaKiller 包含 2 个选项用于调试和测试目的。

- `--pretend` `-p` 选项通知 MediaKiller 进入模拟运行状态。

  此状态下会正常运行所有功能，但是并不会运行 ffmpeg 进行转码。
  但是`--make-script`选项仍然会正常输出脚本。

- `--debug` `-d` 选项为 MediaKiller 开启调试模式。

调试模式下将会启用大量的运行细节输出，便于查找到底出了什么问题。

##  2. <a name='-1'></a>配置文件详解

配置文件本身是一个标准的 TOML 文件，关于 TOML 格式的详细说明，
请参阅 [TOML白皮书](https://toml.io/cn/v1.0.0)。

###  2.1. <a name='-1'></a>配置文件结构

以下是配置文件中各个节的详细说明，**请结合示例配置文件中的注释阅读**：

####  2.1.1. <a name='general'></a>general

general 节定义了此配置的基本信息。

```toml
[general]
profile_id = 'example-profile'
name = "示例"
description = "不进行转码，只是拷贝音视频流"
ffmpeg = "ffmpeg"
```

`profile_id`定义当前配置文件的id，建议使用英文。
此ID用于配置文件的识别，即使不需要使用，也建议设定为一个随机值。

`name`为当前配置文件的名称。

`description`定义当前配置文件的描述。应当尽可能简短的描述此配置文件适用的情况。

`ffmpeg`用于手动定义ffmpeg的可执行文件。
默认情况下，此选项的值为'ffmpeg'，此时将会调用系统环境中的ffmpeg。
如果你没有正常安装，或希望使用其它的可执行文件，应当在此指定其完整路径。

> 为了准确地计算转码进度，MediaKiller使用ffprobe获取源文件的元数据。
> 所以尽量确保它被安装在ffmpeg的旁边。

####  2.1.2. <a name='custom'></a>custom
custom 节中，你可以定义自己的常量，并在其它的小节中引用。
请参阅后面*数据标签*章节。

> custom节中的数据不可以引用其它数据。

####  2.1.3. <a name='source'></a>source

source 节中设置关于获取来源的信息。
```toml
[source]
suffix_includes = []
suffix_excludes = []
ignore_default_suffixes = false
```

MediaKiller 内置了一套常用的扩展名清单，用于过滤来源文件。
所以一般情况下不需要设置这些选项。

`suffix_includes` 定义一套列表，其中每一项是一个扩展名。
MediaKiller 将会把这些扩展名添加到扩展名清单中。

`suffix_excludes` 则相反，其中定义的扩展名将会从扩展名清单中移除。

经过以上两项处理之后的扩展名清单，将作为白名单过滤来源文件。

`ignore_default_suffixes` 设置为 true 时，将会忽略默认的扩展名清单。
此时 `suffix_inlcudes` 就会作为过滤源文件的唯一依据了。

####  2.1.4. <a name='target'></a>target

target 节设置任务目标的相关信息。

```toml
[target]
suffix = "mov"
folder = "${profile:name}"
keep_parent_level = 0
```

`suffix` 用于设置目标文件的扩展名。

`folder` 用于设置目标输出目录。

> 当运行MediaKiller时指定了 `--output` 路径时，
> `folder`将会仅保留目录名并放置在`output`之内。

此选项默认值为当前配置文件的名称。

`keep_parent_level`设置在目标文件之前是否安装源文件的父级目录建立文件夹。
此数值为保留的层级，0为不保留。

下面是一个例子：

如果有一套target设置如下：
```toml
[target]
suffix = 'mp4'
folder = '转码输出'
keep_parent_level=2
```

那么来源文件：
```
/Media/Project/Footage/source.media.mp4
```

对应的目标文件路径为：

```
./转码输出/Project/Footage/source.media.mov
```

> 这样的设计对于一次性处理不同来源的源文件很有用。

####  2.1.5. <a name='inputoutput'></a>input 组 和 output 组
可以指定多组 input，用于为ffmpeg指定多个输入来源。

```toml
[[input]]
filename = "${source:absolute}"
options = ""
[[output]]
filename = "${target:absolute}"
options = '-c:v hevc_nvenc -filter:v "scale=-1:${custom:v1}" -c:a copy'
```

默认情况下，只有一个输入和一个输出，即解析的源文件以及生成的目标文件。

通过增加input和output，可以为转码任务指定其它的输入来源或多种转码目标。
借助`数据标签`可以实现动态指定。

`options` 选项则用于设定对应的输入和输出的选项。

###  2.2. <a name='-1'></a>数据标签

Mediakiller 本身并不兼容 TOML 的数据引用功能，
但是它本身提供了类似的`数据标签`功能。

`数据标签`是形式如`${数据集:选项}`形式的标签，将它输入在文本内容中后，Mediakiller在运行前会自动将其置换为指定的值。

比如在默认的input组中，`filename`被设置为`${source:absolute}`，即`源文件的绝对路径`。

下面是MediaKiller提供的数据标签：
| 数据集        | 选项        | 说明                            |
|---------------|-------------|-------------------------------|
| source        | absolute    | 源文件的绝对路径                |
|               | dot_suffix  | 包含点的源文件扩展名            |
|               | suffix      | 不包含点的源文件扩展名          |
|               | parent      | 源文件的父目录                  |
|               | parent_name | 源文件父目录的名字              |
|               | name        | 源文件的基本名称                |
|               | basename    | 源文件的基础名称，完全不含扩展名 |
| target        | 同上        | 和source完全一样的定义          |
| source_parent | {数字}      | 源文件指定层级的上层目录        |
| target_parent | {数字}      | 目标文件指定层级的上层目录      |
| custom        | 常量名      | 配置文件custom节中定义的常量    |


-----
项目主页: https://gitee.com/xiii_1991/cxalio-studio-tools

作者: xiii_1991@163.com

