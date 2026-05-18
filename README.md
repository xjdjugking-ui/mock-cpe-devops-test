## 项目背景
1.本项目的开发主要用于支撑本人在西安交通大学城市学院通信工程专业本科毕业设计的实践部分，为论文《面向 DevOps 持续交付的智能网关 Web 自动化测试设计与实施》提供系统实现、测试验证和实验数据等方面的佐证。
2.也为CICD/敏捷/嵌入式设备开发/devops的开发思想提供一个很好的切入点。


## 个人夙愿

本项目不仅服务于本科毕业设计的系统实现与论文论证，也希望为 CI/CD、敏捷开发、嵌入式设备开发以及 DevOps 工程思想提供一个较好的实践切入点。通过模拟企业级开发、测试、运维协同流程，项目展示了自动化测试与持续交付在嵌入式设备软件开发中的应用价值，为提升软件交付质量、降低人工测试成本、增强团队协作效率提供参考。

**论文题目：** 面向 DevOps 持续交付的智能网关 Web 自动化测试设计与实施

---
## 项目简介

在快速迭代的软件开发过程中，团队协作、自动化测试和持续交付能力是保障软件质量的重要基础。针对传统嵌入式设备开发中测试流程分散、回归效率较低、交付过程缺少统一追踪等问题，本项目以 CPE 智能网关设备为代表，构建了一套面向 DevOps 的敏捷开发与自动化测试体系。

本项目基于 Flask 搭建 Mock CPE Web 管理平台，在devops的思想下，搭建从开发到上线交付用户的全流程。模拟企业级开发、测试、运维协同场景，并结合 pytest、Selenium、Allure、pytest-cov 和 Jenkins Pipeline 等工具，实现功能开发、接口测试、UI 自动化测试、测试报告生成、覆盖率统计和 CI/CD 流水线集成，形成较完整的软件开发交付流程。

。

**系统限制（Mock 模式）：**
-全流程在mock-docker环境，模拟开发-测试-交付-上线-用户体验
---

## 技术栈

| 层次 | 技术 |
|------|------|
| Web 框架 | Python 3.10+ / Flask 3.0 |
| 数据库 | SQLite 3 |
| 前端 | HTML5 / CSS3 / Jinja2 |
| 单元测试 | pytest 8.2 |
| API 测试 | pytest + Flask test_client |
| UI 自动化 | Selenium 4 + Chrome WebDriver |
| 测试报告 | Allure + pytest-html |
| 覆盖率 | pytest-cov |
| CI/CD | Jenkins Pipeline (Jenkinsfile) |
|环境|docker|
---

## 功能模块

| 模块 | 路由 | 说明 |
|------|------|------|
| 登录认证 | /login | 管理员登录，Session 管理 |
| 控制台 | /dashboard | 设备状态、在线终端、活动日志 |
| 网络配置 | /network | Wi-Fi SSID、密码、模式、信道 |
| 固件升级校验 | /upgrade | 固件文件名格式校验 |
| 运行诊断 | /diagnostics | Ping / DNS / 云端连通性模拟 |
| 固件制品管理 | /artifacts | 固件制品登记、列表 |
| 升级任务 | /jobs | 模拟升级流程执行、结果记录 |
| 实验统计 | /stats | 通过率、覆盖率、Flaky 率、平均耗时 |

---

## 目录结构

```
mock-cpe-devops-test/
├── app/
│   ├── __init__.py          # Flask 应用工厂
│   ├── config.py            # 配置（密钥、数据库路径、管理员账号）
│   ├── routes.py            # Web 路由 + API v1 接口
│   ├── service.py           # 业务逻辑层 GatewayService
│   ├── repository.py        # SQLite 数据访问层 StateRepository
│   ├── device_adapter.py    # 设备适配层（MockDeviceAdapter + 预留类）
│   ├── templates/           # Jinja2 HTML 模板（8 个页面）
│   └── static/style.css     # 统一样式
├── cpe_devops/
│   ├── base_page.py         # Selenium BasePage 基类
│   └── pages/               # Page Object Model
│       ├── login_page.py
│       ├── dashboard_page.py
│       ├── network_page.py
│       ├── upgrade_page.py
│       ├── artifacts_page.py
│       ├── jobs_page.py
│       └── stats_page.py
├── tests/
│   ├── unit/
│   │   ├── test_service.py        # 服务层单元测试（9 个用例）
│   │   ├── test_repository.py     # 数据层单元测试（6 个用例）
│   │   └── test_device_adapter.py # 适配层单元测试（7 个用例）
│   ├── api/
│   │   └── test_api.py            # API 接口测试（13 个用例）
│   └── ui/
│       ├── conftest.py            # Selenium fixtures
│       └── test_ui_smoke.py       # UI 冒烟测试（8 个用例）
├── scripts/
│   └── collect_test_metrics.py   # 论文第 5 章实验数据收集脚本
├── reports/                      # 测试报告输出目录
├── allure-results/               # Allure 原始结果
├── screenshots/                  # UI 测试失败截图
├── data/mock_cpe.db              # SQLite 数据库（自动初始化）
├── artifacts/                    # 固件制品存储目录
├── run.py                        # 启动入口
├── requirements.txt              # Python 依赖
├── pytest.ini                    # pytest 配置
├── Jenkinsfile                   # Jenkins CI/CD 流水线
└── README.md
```

---

## 本地启动步骤

```bash
# 1. 创建虚拟环境
python -m venv .venv

# 2. 激活虚拟环境（Windows）
.\.venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动 Web 服务
python run.py
# 访问 http://127.0.0.1:5000
# 账号: admin  密码: admin123
```

---

## 测试命令

### 单元测试
```bash
pytest tests/unit -v
```

### API 测试
```bash
pytest tests/api -v
```

### UI 测试（需先启动 Web 服务）
```bash
# 无界面模式（默认）
pytest tests/ui -v

# 有界面模式
set HEADLESS=0 && pytest tests/ui -v
```

### 生成 Allure 原始结果
```bash
pytest tests --alluredir=allure-results
allure serve allure-results
```

### 生成覆盖率报告
```bash
pytest tests/unit tests/api --cov=app --cov=cpe_devops --cov-report=term-missing
```

### 收集论文实验数据
```bash
python scripts/collect_test_metrics.py --unit 19 --api 13 --ui 8 --coverage 0.91 --flaky 0.02 --avg-duration 1.8
# 输出到 reports/test_metrics.json
```

---

## API 接口列表

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/health | 健康检查 |
| GET | /api/v1/readiness | 就绪检查 |
| GET | /api/v1/dashboard | 控制台数据 |
| GET | /api/v1/network | 获取网络配置 |
| POST | /api/v1/network | 保存网络配置 |
| POST | /api/v1/upgrade | 固件文件名校验 |
| GET | /api/v1/artifacts | 固件制品列表 |
| POST | /api/v1/artifacts | 登记固件制品 |
| GET | /api/v1/upgrade-jobs | 升级任务列表 |
| POST | /api/v1/upgrade-jobs | 执行升级任务 |
| GET | /api/v1/experiments | 实验统计结果 |
| GET | /api/v1/diagnostics | 获取诊断状态 |
| POST | /api/v1/diagnostics | 刷新诊断状态 |

---

## Jenkinsfile 阶段说明

| 阶段 | 说明 |
|------|------|
| Checkout | 拉取源代码 |
| Setup Python | 创建 Python 虚拟环境 |
| Install Dependencies | 安装 requirements.txt |
| Start Mock CPE | 后台启动 Flask 服务（供 UI 测试使用） |
| Run Unit Tests | 执行 tests/unit，输出 Allure 结果 |
| Run API Tests | 执行 tests/api，输出 Allure 结果 |
| Run UI Tests | 执行 tests/ui（Chrome headless），输出 Allure 结果 |
| Generate Coverage | 生成代码覆盖率报告 |
| Collect Test Metrics | 生成论文第 5 章实验数据 JSON |
| Generate Allure Results | 聚合 Allure 报告（需 Allure Jenkins Plugin） |
| Archive Reports | 归档 reports/、allure-results/、screenshots/ |

---

## 数据库表结构

| 表名 | 说明 |
|------|------|
| singleton_state | 系统/网络/升级/诊断状态（JSON 键值） |
| clients | 在线终端列表 |
| activities | 活动日志 |
| firmware_artifacts | 固件制品元数据 |
| upgrade_jobs | 升级任务执行记录 |
| experiment_runs | 实验运行指标记录 |

---

## 论文对应关系

| 论文章节 | 对应内容 |
|----------|----------|
| 第 3 章 系统设计 | Flask 分层架构、MockDeviceAdapter、数据库设计、API 设计 |
| 第 4 章 系统详细实现 | app/ 目录下所有源码、8 大 Web 模块、API 接口实现 |
| 第 5 章 系统测试与结果分析 | tests/ 目录、Allure 报告、reports/test_metrics.json |
| 第 6 章 持续交付流程 | Jenkinsfile、Jenkins CI/CD 流水线设计 |

---

## 测试用例统计

| 类型 | 文件 | 用例数 |
|------|------|--------|
| 单元测试 | test_service.py | 9 |
| 单元测试 | test_repository.py | 6 |
| 单元测试 | test_device_adapter.py | 7 |
| API 测试 | test_api.py | 16 |
| UI 测试 | test_ui_smoke.py | 8 |
| 合计 | | 46 |
