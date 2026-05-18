# Jenkins 配置指南 — Mock CPE DevOps CI/CD Pipeline

> 目标：Git Push → Jenkins 自动拉取代码 → **10 分钟内完成全量测试** → 覆盖率 >= 95% → 生成 Jenkins/Allure/Gmail 报告
> Gmail 报告推送配置见 `JENKINS_GMAIL_SETUP.md`。当前流水线会在 SMTP/Gmail 未配置好时明确失败，避免“构建成功但邮箱没收到报告”。

---

## 快速验证模式（推荐）

当前仓库已经提供一个 **最小 CI/CD 工作流**，用于快速验证整条链路：

- 触发方式：`git push` 后 Jenkins `Poll SCM`
- 流水线模式：**本地 Python quick smoke**（不跑 Docker / 不跑 UI）
- 测试范围：
  - `tests/unit/test_device_adapter.py`
  - `tests/api/test_routes_html.py`
- 报告产物：
  - JUnit XML：`reports/unit_junit.xml`、`reports/api_junit.xml`
  - JSON / Coverage / Dashboard：`reports/`

> 说明：首次构建如果需要创建虚拟环境，耗时可能略高；**后续提交验证通常会明显快于 1 分钟**。

---

## 方案 A：Docker 快速启动 Jenkins（推荐，5 分钟上手）

### 1. 启动 Jenkins 容器

```batch
docker run -d ^
  --name jenkins ^
  --restart=unless-stopped ^
  -p 8080:8080 ^
  -p 50000:50000 ^
  -v jenkins_home:/var/jenkins_home ^
  -v //var/run/docker.sock:/var/run/docker.sock ^
  jenkins/jenkins:lts
```

> **关键**：`-v //var/run/docker.sock:/var/run/docker.sock` 让 Jenkins 容器能调用宿主机的 Docker，实现 "Docker in Docker"。

### 2. 获取初始密码

```batch
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

### 3. 打开浏览器

访问 `http://localhost:8080`，输入上面的密码。

### 4. 安装推荐插件

选择 "Install suggested plugins"，会自动安装 Git、Pipeline 等基础插件。

---

## 方案 B：Windows 本地安装 Jenkins

1. 下载 `jenkins.msi`：https://www.jenkins.io/download/
2. 安装时选择 "Run Jenkins as a Windows service"
3. 安装完成后访问 `http://localhost:8080`
4. 初始密码在 `C:\Program Files\Jenkins\secrets\initialAdminPassword`

---

## 安装 Allure Jenkins Plugin（可选）

### 步骤

1. **Manage Jenkins** → **Plugins** → **Available plugins**
2. 搜索 `Allure`
3. 勾选 **Allure Jenkins Plugin**
4. 点击 **Install without restart**
5. 安装完成后勾选 "Restart Jenkins when installation is complete"

### 配置 Allure 工具

1. **Manage Jenkins** → **Tools**
2. 找到 **Allure Commandline** 区域
3. 点击 **Add Allure Commandline**
4. Name 填：`Allure`
5. 选择 **Install automatically**，版本选最新的（如 2.32.0）
6. 点击 **Save**

![Allure配置截图点](此处)

---

## 创建 Pipeline 任务

### 第 1 步：新建任务

1. Jenkins 首页 → 点击 **New Item**（左上角）
2. 输入任务名称，例如：`MockCPE-DevOps`
3. 选择 **Pipeline**
4. 点击 **OK**

### 第 2 步：配置 Pipeline 脚本

> **为什么不用 Git SCM？** Jenkins 运行在 Docker 容器内，无法直接访问 Windows 宿主机的本地路径（`file:///C:/...`）。
> 解决方案：直接用 "Pipeline script" 模式粘贴 Jenkinsfile 内容。

1. 在 **Pipeline** 区域，**Definition** 选择 `Pipeline script`
2. 打开项目中的 `Jenkinsfile`，**复制全部内容**
3. 粘贴到 **Script** 文本框中

> 如果想用 Git SCM（推送到 GitHub/GitLab 后），需要在创建任务时选 `Pipeline script from SCM`，填入远程仓库 URL。本地仓库不支持。

> **关键建议：如果你想每次 `git push` 后都自动保留最新的“状态集摘要”，优先使用 `Pipeline script from SCM` 并让 Jenkins 直接读取仓库里的 `Jenkinsfile`。**
>
> 如果你当前用的是 **Pipeline script**（把脚本粘贴在 Jenkins UI 里），那么你每次修改本地 `Jenkinsfile` 后，还需要把它重新同步进 Jenkins 任务配置，否则后续构建可能继续跑旧脚本，导致你看到“状态集又消失”。

### 同步 Jenkinsfile 到 Jenkins 任务（适用于 Pipeline script 模式）

如果你的 Jenkins 是 Docker 里的容器，并且任务名是 `MockCPE-DevOps`，可以在项目根目录执行：

```batch
python scripts/_deploy_jenkinsfile.py
```

或者：

```batch
python scripts/update_jenkins_config.py
```

默认配置：
- Jenkins 地址：`http://localhost:8080`
- Job 名称：`MockCPE-DevOps`

也支持环境变量覆盖：

```batch
set JENKINS_URL=http://localhost:8080
set JENKINS_JOB_NAME=MockCPE-DevOps
python scripts/update_jenkins_config.py
```


### 第 3 步：配置 Allure Report

1. 在任务配置页找到 **Post-build Actions**
2. 点击 **Add post-build action** → 选择 **Allure Report**
3. 如果你保留 Allure 插件，可以继续安装；但 **quick smoke 流程的最小依赖并不强制要求 Allure**。
4. 最小工作流主要依赖：
   - Jenkins 控制台输出
   - JUnit 测试结果
   - `reports/jenkins-dashboard.html`

### 第 4 步：配置构建触发器（自动触发）

1. 在 **Build Triggers** 区域
2. 勾选 **Poll SCM**
3. Schedule 填入：`H/1 * * * *`（每 1 分钟检查一次 Git 变更，适合快速验证）
4. 或者用 Webhook（需要 GitHub/GitLab 配置，Poll SCM 更简单）

### 第 5 步：保存

点击 **Save**

---

## 首次构建验证

1. 在任务页面点击 **Build Now**（左侧）
2. 等待构建完成
3. 观察 **Stage View** — 应该看到 9 个阶段依次变绿
4. 构建完成后查看 **Test Result**、**CI Dashboard**、**Artifacts**
5. 打开 `reports/jenkins-dashboard.html` 查看快速测试报告

---

## ✅ 验证清单

| 检查项 | 状态 |
|--------|------|
| Jenkins 访问 `http://localhost:8080` | ☐ |
| Allure Plugin 已安装 | ☐ |
| Pipeline 任务已创建 | ☐ |
| Build Now 可以执行 | ☐ |
| Stage View 各阶段通过 | ☐ |
| Allure Report 图标可见 | ☐ |
| Allure 报告展示 Unit/API/UI 三类测试 | ☐ |

---

## 常见问题

### Q: Docker 命令在 Jenkins 中报 "permission denied"

**解决**（Windows Docker Desktop）：无此问题，`docker.sock` 挂载后自动可用。

**解决**（Linux）：
```bash
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

### Q: UI 测试报 "chrome not reachable"

**原因**：Selenium 容器未启动或网络不通。
**检查**：
```batch
docker compose ps
docker compose logs selenium
```

### Q: Allure Report 不显示

**检查**：
1. Jenkins → Manage Jenkins → Tools → Allure Commandline 是否配置
2. 任务日志中是否有 "Allure report was successfully generated"
3. `allure-results/` 目录下是否有 `.json` 文件

---

## 架构总览

```
┌──────────┐     ┌─────────────────────────────────────────────┐
│ git push │────▶│ Jenkins (http://localhost:8080)              │
└──────────┘     │                                             │
                 │  Pipeline (Jenkinsfile)                     │
                 │  ┌──────────────────────────────────────┐   │
                 │  │ 1. docker compose build              │   │
                 │  │ 2. docker compose up -d mock-cpe     │   │
                 │  │ 3. test-runner → Unit Tests          │   │
                 │  │ 4. test-runner → API Tests           │   │
                 │  │ 5. test-runner → UI Tests            │   │
                 │  │ 6. Coverage Report                   │   │
                 │  │ 7. Allure Report (聚合三类测试)       │   │
                 │  │ 8. docker compose down               │   │
                 │  └──────────────────────────────────────┘   │
                 │                                             │
                 │  📊 Allure Report                           │
                 │  ┌──────────┬──────────┬──────────┐        │
                 │  │ Unit     │ API      │ UI       │        │
                 │  │ 22 tests │ 16 tests │ 8 tests  │        │
                 │  └──────────┴──────────┴──────────┘        │
                 └─────────────────────────────────────────────┘
