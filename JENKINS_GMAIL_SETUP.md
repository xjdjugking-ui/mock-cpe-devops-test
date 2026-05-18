# Jenkins Gmail 报告推送配置

目标：每次 Git 触发 Jenkins 全量测试后，把控制台日志、CI Dashboard、coverage.xml 和指标 JSON 推送到 Gmail。

## 1. 准备 Gmail App Password

1. 打开 Google Account。
2. 进入 Security。
3. 确认 2-Step Verification 已开启。
4. 进入 App passwords。
5. 新建一个 app password，例如名称填 `Jenkins Mock CPE`。
6. 保存生成的 16 位密码。这个密码只填到 Jenkins，不提交到 Git。

## 2. Jenkins 全局 SMTP

路径：Manage Jenkins -> System

在 Extended E-mail Notification 中填写：

- SMTP server: `smtp.gmail.com`
- SMTP Port: `587`
- Use TLS: 勾选
- Use SSL: 不勾选
- SMTP Username: 你的 Gmail 地址，例如 `xjdjugking@gmail.com`
- SMTP Password: 第 1 步生成的 App Password
- Default user e-mail suffix: `@gmail.com`
- Default Content Type: `HTML (text/html)`

在 E-mail Notification 中也填写：

- SMTP server: `smtp.gmail.com`
- Use SMTP Authentication: 勾选
- User Name: 你的 Gmail 地址
- Password: Gmail App Password
- Use TLS: 勾选
- SMTP Port: `587`
- Reply-To Address: 你的 Gmail 地址

点击 Test configuration，确认 Jenkins 能发出测试邮件，然后 Save。

## 3. Pipeline 参数

Jenkinsfile 已经提供 `EMAIL_TO` 参数，默认：

```text
xjdjugking@gmail.com
```

如果要发到其他 Gmail，在 Jenkins 构建参数里修改 `EMAIL_TO` 即可。

## 4. 成功后邮件内容

每封邮件会包含：

- Jenkins Build 链接
- Blue Ocean Pipeline 链接
- Console Output 链接
- Allure Report 链接
- 压缩后的控制台日志附件
- `reports/jenkins-dashboard.html`
- `reports/coverage.xml`
- `reports/test_metrics.json`

如果 SMTP 或 Gmail App Password 未配置好，流水线会在邮件步骤明确失败，避免出现 Jenkins 成功但邮箱没有报告的情况。
