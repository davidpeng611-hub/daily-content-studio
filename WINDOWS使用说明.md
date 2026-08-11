# Windows 使用说明

目标：让这套「每日口播工作室」在 Windows 笔记本上继续使用，重点保留工作流、脚本、模板和账号规则；成品视频、配音、生成图和平台登录状态不走 GitHub。

## 1. 必装软件

Windows 上先安装：

- Git
- Python 3.11 或更高版本
- FFmpeg
- 剪映 Windows 版
- Chrome
- Codex 或 ChatGPT 桌面端

可选：

- Node.js 20 或更高版本，用于篮球快剪工具
- GitHub Desktop，用于不熟悉命令行时管理同步

## 2. 拉取工程

推荐放在 D 盘：

```powershell
cd D:\
git clone git@github.com:davidpeng611-hub/daily-content-studio.git 每日口播工作室
cd D:\每日口播工作室
```

如果 Windows 还没配置 SSH，也可以先用 HTTPS：

```powershell
git clone https://github.com/davidpeng611-hub/daily-content-studio.git 每日口播工作室
```

## 3. 初始化本地目录

在 PowerShell 里运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1
```

它会创建这些本地目录：

- `input`：放当天配音、素材、截图
- `output`：最终视频和封面输出
- `素材库`：长期素材
- `今日推文`：每日视频工程
- `local`：本机配置，不上传 GitHub

## 4. 检查环境

运行：

```powershell
python .\scripts\doctor.py
```

看到 Git、Python、FFmpeg 都通过后，再开始做视频。

## 5. 本地配置

复制示例配置：

```powershell
copy .\config\workflow.example.json .\local\workflow.local.json
```

然后按你的 Windows 实际路径修改：

- `workspace_root`
- `input_dir`
- `output_dir`
- `ffmpeg`

不要把 `local\workflow.local.json` 上传到 GitHub。

## 6. 日常使用方式

把配音放到：

```text
D:\每日口播工作室\input
```

然后在 Codex 里说：

```text
用小红书动画心理工作流 做今天这条
```

或者：

```text
用账号制作工作室 1 做今天这条
```

## 7. 两条账号线不要混

小红书体育哲学动画号：

- 横版 16:9
- 16 张以上高清故事图
- 哲学经典故事开头
- 普通人成长、心理困境、成功方法
- 不做篮球技战术诊断 CTA

账号制作工作室 1：

- 篮球观点、战术、青训、家长、教练
- HeyGen 只生成干净口播
- 必须使用已确认的本人深色 Polo 模板和 Luca 声音
- 真实比赛素材和战术动画在本地后期完成
- 不允许自动换数字人

## 8. 不上传 GitHub 的内容

以下内容只放本地：

- 配音音频
- 成品视频
- 生成图
- 抽帧图
- HeyGen 日志
- cookie
- 平台登录配置
- 剪映工程缓存

## 9. 更新工程

Mac 和 Windows 之间同步代码时：

```powershell
git pull
```

如果 Windows 上也改了脚本：

```powershell
git status
git add .
git commit -m "Update workflow from Windows"
git push
```

提交前确认不要出现 `.mp4`、`.mp3`、`.png`、`.jpg`、`.env`、`cookie`、`local_config`。

