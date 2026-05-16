# Jenkins 配置指南 — Mock CPE DevOps CI/CD Pipeline

> 目标：Git Push → Jenkins 自动拉取代码 → Docker 里跑测试 → Allure 集成报告

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

## 安装 Allure Jenkins Plugin（两种方案通用）

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

### 第 2 步：配置 Git 仓库

1. 在 **Pipeline** 区域，**Definition** 选择 `Pipeline script from SCM`
2. **SCM** 选择 `Git`
3. **Repository URL** 填入你的 Git 仓库地址，例如：
   ```
   https://github.com/yourname/mock-cpe-devops-test.git
   ```
   > 如果是本地仓库，可以用 `file:///C:/Users/LPC/mock-cpe-devops-test`
4. **Branch Specifier** 保持 `*/main`（或你的默认分支）
5. **Script Path** 保持 `Jenkinsfile`

### 第 3 步：配置 Allure Report

1. 在任务配置页找到 **Post-build Actions**
2. 点击 **Add post-build action** → 选择 **Allure Report**
3. **Path** 配置如下（Jenkinsfile 中 Allure 步骤会自动生成报告，这里是 UI 显示的兜底）：
   - Results → 不用填（Jenkinsfile 里的 `allure` pipeline 步骤已处理）

> Jenkinsfile 里的 `allure` DSL 步骤会自动聚合 `allure-results/unit`、`allure-results/api`、`allure-results/ui`，无需额外配置。

### 第 4 步：配置构建触发器（自动触发）

1. 在 **Build Triggers** 区域
2. 勾选 **Poll SCM**
3. Schedule 填入：`H/5 * * * *`（每 5 分钟检查一次 Git 变更）
4. 或者用 Webhook（需要 GitHub/GitLab 配置，Poll SCM 更简单）

### 第 5 步：保存

点击 **Save**

---

## 首次构建验证

1. 在任务页面点击 **Build Now**（左侧）
2. 等待构建完成
3. 观察 **Stage View** — 应该看到 9 个阶段依次变绿
4. 构建完成后页面出现 **Allure Report** 图标
5. 点击图标查看集成测试报告

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