# 微信通知 SOP

目标：你不在电脑旁时，自动化结果通过微信提醒你。

## 推荐方案

第一选择：企业微信群机器人 webhook。

- 稳定。
- 不需要保存你的微信密码。
- 可以建一个只有你自己的企业微信群，把机器人加进去。
- Codex 只需要 webhook URL。

第二选择：Server酱 SendKey。

- 推送到个人微信服务通知。
- 适合只接收文本提醒。

无法扫码时：iMessage。

- 只要这台 Mac 的“信息”已登录 Apple ID，就能发到你的手机。
- 不需要微信扫码。
- 需要填你的手机号或 Apple ID 邮箱。

## 本地配置

复制示例：

```bash
cp platform-intelligence/config/notification.example.env platform-intelligence/config/notification.env
```

填入其中一种：

```bash
WECHAT_WORK_BOT_WEBHOOK="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxx"
```

或：

```bash
SERVERCHAN_SENDKEY="SCTxxxxxxxxxxxxxxxx"
```

或：

```bash
IMESSAGE_RECIPIENT="+8613800000000"
```

脚本会自动读取这个文件，不需要每次手动 `source`。

## 测试

如果你拿到了 Server酱 SendKey，直接运行：

```bash
python3 platform-intelligence/scripts/setup_wechat_notification.py \
  --serverchan-sendkey "SCTxxxxxxxxxxxxxxxx" \
  --test
```

如果你拿到了企业微信群机器人 webhook，直接运行：

```bash
python3 platform-intelligence/scripts/setup_wechat_notification.py \
  --wecom-webhook "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxx" \
  --test
```

如果你无法扫码，但这台 Mac 能发 iMessage，直接运行：

```bash
python3 platform-intelligence/scripts/setup_wechat_notification.py \
  --imessage-recipient "+8613800000000" \
  --test
```

也可以只干跑查看内容：

```bash
python3 platform-intelligence/scripts/notify_user.py \
  --title "测试通知" \
  --body "如果你在微信看到这条，说明通知通道已打通。" \
  --dry-run
```

去掉 `--dry-run` 才会真正发送。

## 自动化里怎么用

9 点复盘和 12 点选题自动化完成报告后，如果发现环境里配置了：

- `WECHAT_WORK_BOT_WEBHOOK`
- 或 `SERVERCHAN_SENDKEY`

就调用：

```bash
python3 platform-intelligence/scripts/notify_user.py \
  --title "每日口播工作室自动化完成" \
  --body "简短结论" \
  --file "报告路径"
```

## 边界

- 不通过微信收账号密码。
- 不在微信或 iMessage 里直接确认发布。
- 微信/iMessage 只做提醒和摘要。
- 真正发布、HeyGen 扣额度、账号设置修改，仍需你明确确认。
