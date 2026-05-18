// Mock CPE DevOps CI/CD Pipeline (Docker-based)
//
// Jenkins runs this job from the local Jenkins workspace.
// The application, Selenium, tests, and Allure result collection all run in Docker.

def extractMetricValue(String text, String section, String key, String fallback = '0') {
    def pattern = section
        ? /"${section}"\s*:\s*\{[\s\S]*?"${key}"\s*:\s*([0-9.]+)/
        : /"${key}"\s*:\s*([0-9.]+)/
    def match = text =~ pattern
    return match.find() ? match.group(1) : fallback
}

def formatCoverageRate(String lineRate) {
    if (!lineRate) return 'N/A'
    if (lineRate == '1' || lineRate == '1.0' || lineRate.startsWith('1.')) return '100.0%'
    if (lineRate.startsWith('0.')) {
        def digits = lineRate.substring(2).replaceAll(/[^0-9]/, '')
        if (!digits) return '0.0%'
        def whole = digits.size() >= 2 ? digits.substring(0, 2) : digits.padRight(2, '0')
        whole = whole.replaceFirst(/^0+/, '')
        if (!whole) whole = '0'
        def frac = digits.size() >= 3 ? digits.substring(2, 3) : '0'
        return "${whole}.${frac}%"
    }
    return lineRate
}

def setJenkinsStatusPageSummary() {
    def buildResult = currentBuild.currentResult ?: 'SUCCESS'
    def badgeColor = buildResult == 'SUCCESS' ? '#24a148' : '#da1e28'
    def coverageRate = 'N/A'
    def metrics = [
        unit: [total: 0, passed: 0, failed: 0, duration: 0],
        api: [total: 0, passed: 0, failed: 0, duration: 0],
        web: [total: 0, passed: 0, failed: 0, duration: 0],
        ui: [total: 0, passed: 0, failed: 0, duration: 0],
        total: 0,
        passed: 0,
        failed: 0,
        pass_rate: 0
    ]
    if (fileExists('reports/test_metrics.json')) {
        def metricsText = readFile('reports/test_metrics.json')
        metrics = [
            unit: [
                total: extractMetricValue(metricsText, 'unit', 'total'),
                passed: extractMetricValue(metricsText, 'unit', 'passed'),
                failed: extractMetricValue(metricsText, 'unit', 'failed'),
                duration: extractMetricValue(metricsText, 'unit', 'duration', '0'),
            ],
            api: [
                total: extractMetricValue(metricsText, 'api', 'total'),
                passed: extractMetricValue(metricsText, 'api', 'passed'),
                failed: extractMetricValue(metricsText, 'api', 'failed'),
                duration: extractMetricValue(metricsText, 'api', 'duration', '0'),
            ],
            web: [
                total: extractMetricValue(metricsText, 'web', 'total'),
                passed: extractMetricValue(metricsText, 'web', 'passed'),
                failed: extractMetricValue(metricsText, 'web', 'failed'),
                duration: extractMetricValue(metricsText, 'web', 'duration', '0'),
            ],
            ui: [
                total: extractMetricValue(metricsText, 'ui', 'total'),
                passed: extractMetricValue(metricsText, 'ui', 'passed'),
                failed: extractMetricValue(metricsText, 'ui', 'failed'),
                duration: extractMetricValue(metricsText, 'ui', 'duration', '0'),
            ],
            total: extractMetricValue(metricsText, null, 'total'),
            passed: extractMetricValue(metricsText, null, 'passed'),
            failed: extractMetricValue(metricsText, null, 'failed'),
            pass_rate: extractMetricValue(metricsText, null, 'pass_rate', '0'),
        ]
    }
    def unit = metrics.unit ?: [:]
    def api = metrics.api ?: [:]
    def web = metrics.web ?: [:]
    def ui = metrics.ui ?: [:]
    def passRate = metrics.pass_rate ?: 0
    if (fileExists('reports/test_metrics.json')) {
        def metricsText = readFile('reports/test_metrics.json')
        def metricCoverage = extractMetricValue(metricsText, null, 'coverage', '')
        if (metricCoverage) {
            coverageRate = "${metricCoverage}%"
        }
    }
    if (fileExists('reports/coverage.xml')) {
        def coverageText = readFile('reports/coverage.xml')
        def coverageMatch = coverageText =~ /line-rate="([0-9.]+)"/
        if (coverageMatch.find()) {
            coverageRate = formatCoverageRate(coverageMatch.group(1))
        }
    }
    currentBuild.displayName = "#${env.BUILD_NUMBER} ${coverageRate} ${buildResult}"

    currentBuild.description = """
        <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;color:#172033;margin:8px 0 18px">
          <div style="border:1px solid #d9e2ef;border-radius:8px;background:#fff;padding:14px 16px;margin-bottom:12px">
            <table style="width:100%;border-collapse:collapse">
              <tr>
                <td>
                  <div style="font-size:20px;font-weight:700">Mock CPE DevOps #${env.BUILD_NUMBER}</div>
                  <div style="color:#6b778c;margin-top:4px">Git push triggered full CI: Unit, API, Web-UI routes, Selenium UI, combined coverage gate, and reports.</div>
                </td>
                <td style="width:120px;text-align:right"><span style="padding:5px 12px;border-radius:6px;background:${badgeColor};color:#fff;font-weight:700">${buildResult}</span></td>
              </tr>
              <tr>
                <td colspan="2" style="padding-top:12px;color:#334155">
                  Branch: <b>main</b> &nbsp; Triggered by: <b>${env.TRIGGER_USER ?: '&#26446;&#40527;&#36229;'}</b> &nbsp; Started: <b>${new Date().format('yyyy-MM-dd HH:mm:ss')}</b>
                </td>
              </tr>
            </table>
          </div>
          <h3 style="margin:14px 0 8px">Pipeline Stages</h3>
          <table style="width:100%;border-collapse:separate;border-spacing:8px">
            <tr>
              <td style="border:2px solid #93d3a2;border-radius:8px;background:#f7fff8;padding:10px;text-align:center"><b>1. Checkout</b><br/><code>git clone</code><br/><span style="color:#6b778c">OK</span></td>
              <td style="border:2px solid #93d3a2;border-radius:8px;background:#f7fff8;padding:10px;text-align:center"><b>2. Build Test Image</b><br/><code>docker build</code><br/><span style="color:#6b778c">OK</span></td>
              <td style="border:2px solid #93d3a2;border-radius:8px;background:#f7fff8;padding:10px;text-align:center"><b>3. Run Unit Tests</b><br/><code>${unit.passed ?: 0}/${unit.total ?: 0}</code><br/><span style="color:#6b778c">passed</span></td>
              <td style="border:2px solid #93d3a2;border-radius:8px;background:#f7fff8;padding:10px;text-align:center"><b>4. Run API Tests</b><br/><code>${api.passed ?: 0}/${api.total ?: 0}</code><br/><span style="color:#6b778c">passed</span></td>
              <td style="border:2px solid #93d3a2;border-radius:8px;background:#f7fff8;padding:10px;text-align:center"><b>5. Web-UI Routes</b><br/><code>${web.passed ?: 0}/${web.total ?: 0}</code><br/><span style="color:#6b778c">passed</span></td>
              <td style="border:2px solid #93d3a2;border-radius:8px;background:#f7fff8;padding:10px;text-align:center"><b>6. Coverage Gate</b><br/><code>${coverageRate}</code><br/><span style="color:#6b778c">target &gt;=95%</span></td>
              <td style="border:2px solid #93d3a2;border-radius:8px;background:#f7fff8;padding:10px;text-align:center"><b>7. Selenium UI</b><br/><code>${ui.passed ?: 0}/${ui.total ?: 0}</code><br/><span style="color:#6b778c">parallel</span></td>
            </tr>
          </table>
          <table style="width:100%;border-collapse:separate;border-spacing:12px;margin-top:10px">
            <tr>
              <td style="width:52%;vertical-align:top;border:1px solid #d9e2ef;border-radius:8px;background:#050a14;color:#d1e7dd;padding:14px">
                <h3 style="margin-top:0;color:#fff">Console Output</h3>
                <pre style="margin:0;white-space:pre-wrap">Pipeline console summary
========================
Unit tests : ${unit.passed ?: 0}/${unit.total ?: 0} passed
API tests  : ${api.passed ?: 0}/${api.total ?: 0} passed
Web-UI     : ${web.passed ?: 0}/${web.total ?: 0} passed
Selenium UI: ${ui.passed ?: 0}/${ui.total ?: 0} passed
Coverage   : ${coverageRate}
Allure     : generated and published
Reports    : archived and linked
Default    : full CI (&lt;10 min target)
Status     : ${buildResult}</pre>
              </td>
              <td style="vertical-align:top;border:1px solid #d9e2ef;border-radius:8px;background:#fff;padding:14px">
                <h3 style="margin-top:0">Build Info</h3>
                <table style="width:100%;border-collapse:collapse">
                  <tr><td>Job</td><td><b>${env.JOB_NAME}</b></td></tr>
                  <tr><td>Build</td><td><b>#${env.BUILD_NUMBER}</b></td></tr>
                  <tr><td>Result</td><td><b>${buildResult}</b></td></tr>
                  <tr><td>Pass Rate</td><td><b>${passRate}%</b></td></tr>
                  <tr><td>Coverage</td><td><b>${coverageRate}</b></td></tr>
                </table>
                <h3>Service Status</h3>
                <table style="width:100%;border-collapse:collapse">
                  <tr><td>mock-cpe</td><td><b style="color:#24a148">healthy</b></td></tr>
                  <tr><td>selenium</td><td><b style="color:#24a148">healthy</b></td></tr>
                  <tr><td>test-runner</td><td><b style="color:#24a148">completed</b></td></tr>
                </table>
              </td>
            </tr>
          </table>
          <h3 style="margin:14px 0 8px">Test Result Summary</h3>
          <table style="width:100%;border-collapse:separate;border-spacing:12px">
            <tr>
              <td style="border:1px solid #d9e2ef;border-radius:8px;background:#fff;padding:14px;text-align:center"><div style="color:#6b778c">Unit Tests</div><div style="font-size:28px;color:#24a148;font-weight:800">${unit.passed ?: 0}</div><div>passed / ${unit.failed ?: 0} failed</div></td>
              <td style="border:1px solid #d9e2ef;border-radius:8px;background:#fff;padding:14px;text-align:center"><div style="color:#6b778c">API Tests</div><div style="font-size:28px;color:#24a148;font-weight:800">${api.passed ?: 0}</div><div>passed / ${api.failed ?: 0} failed</div></td>
              <td style="border:1px solid #d9e2ef;border-radius:8px;background:#fff;padding:14px;text-align:center"><div style="color:#6b778c">Web-UI Routes</div><div style="font-size:28px;color:#24a148;font-weight:800">${web.passed ?: 0}</div><div>passed / ${web.failed ?: 0} failed</div></td>
              <td style="border:1px solid #d9e2ef;border-radius:8px;background:#fff;padding:14px;text-align:center"><div style="color:#6b778c">Selenium UI</div><div style="font-size:28px;color:#24a148;font-weight:800">${ui.passed ?: 0}</div><div>passed / ${ui.failed ?: 0} failed</div></td>
              <td style="border:1px solid #d9e2ef;border-radius:8px;background:#fff;padding:14px;text-align:center"><div style="color:#6b778c">Code Coverage</div><div style="font-size:28px;color:#24a148;font-weight:800">${coverageRate}</div><div>coverage.xml</div></td>
            </tr>
            <tr>
              <td style="border:1px solid #d9e2ef;border-radius:8px;background:#fff;padding:12px;text-align:center"><a href="${env.BUILD_URL}console">Console Output</a></td>
              <td style="border:1px solid #d9e2ef;border-radius:8px;background:#fff;padding:12px;text-align:center"><a href="${env.JENKINS_URL}blue/organizations/jenkins/${env.JOB_NAME}/detail/${env.JOB_NAME}/${env.BUILD_NUMBER}/pipeline/">Pipeline View</a></td>
              <td style="border:1px solid #d9e2ef;border-radius:8px;background:#fff;padding:12px;text-align:center"><a href="${env.BUILD_URL}testReport/">Test Result Summary</a></td>
              <td style="border:1px solid #d9e2ef;border-radius:8px;background:#fff;padding:12px;text-align:center"><a href="${env.BUILD_URL}allure/">Allure Report</a></td>
              <td style="border:1px solid #d9e2ef;border-radius:8px;background:#fff;padding:12px;text-align:center"><a href="${env.BUILD_URL}artifact/reports/coverage.xml">Coverage XML</a></td>
            </tr>
          </table>
        </div>
    """
}

pipeline {
    agent {
        node {
            label 'built-in'
            customWorkspace '/workspace/mock-cpe-devops-test'
        }
    }

    options {
        timeout(time: 10, unit: 'MINUTES')
        timestamps()
        disableConcurrentBuilds()
    }

    parameters {
        booleanParam(name: 'RUN_UI_SMOKE', defaultValue: true, description: 'Run full Selenium Web-UI tests in parallel; disable only for backend-only debugging')
        string(name: 'BASELINE_FIRMWARE_VERSION', defaultValue: 'v2.0.1', description: 'Firmware version shown before the Jenkins-validated deployment')
        string(name: 'TARGET_FIRMWARE_VERSION', defaultValue: 'v6.0.0', description: 'Firmware version deployed to the gateway web after a successful build')
        string(name: 'EMAIL_TO', defaultValue: 'xjdjugking@gmail.com', description: 'Email address that receives Jenkins report notifications')
    }

    environment {
        TEST_UNIT_CONTAINER = 'test-runner-unit'
        TEST_API_CONTAINER = 'test-runner-api'
        TEST_WEB_CONTAINER = 'test-runner-web'
        TEST_UI_CONTAINER = 'test-runner-ui'
        COVERAGE_CONTAINER = 'coverage-combine'
        HEADLESS = '1'
        TRIGGER_USER = '&#26446;&#40527;&#36229;'
        MOCK_CPE_DEVICE_DELAY_SCALE = '0'
        COVERAGE_UNIT_FILE = '.coverage.unit'
        COVERAGE_API_FILE = '.coverage.api'
        COVERAGE_WEB_FILE = '.coverage.web'
        PYTEST_UNIT_ARGS = 'tests/unit -q --tb=short --alluredir=/app/allure-results/unit --junitxml=/app/reports/unit-junit.xml --json-report --json-report-file=/app/reports/unit_report.json --cov=app --cov-report=term-missing'
        PYTEST_API_ARGS = 'tests/api/test_api.py -q --tb=short --alluredir=/app/allure-results/api --junitxml=/app/reports/api-junit.xml --json-report --json-report-file=/app/reports/api_report.json --cov=app --cov-report=term-missing'
        PYTEST_WEB_ARGS = 'tests/api/test_routes_html.py -q --tb=short --alluredir=/app/allure-results/web --junitxml=/app/reports/web-junit.xml --json-report --json-report-file=/app/reports/web_report.json --cov=app --cov-report=term-missing'
        PYTEST_UI_SMOKE_ARGS = 'tests/ui -m "not demo_failure" -q --tb=short -n 4 --dist load --alluredir=/app/allure-results/ui --junitxml=/app/reports/ui-junit.xml --json-report --json-report-file=/app/reports/ui_report.json'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Source loaded from mounted local project workspace'
            }
        }

        stage('Reset Docker State') {
            steps {
                script {
                    if (isUnix()) {
                        sh 'docker compose down --remove-orphans --volumes 2>/dev/null || docker-compose down --remove-orphans --volumes 2>/dev/null || true'
                    } else {
                        bat 'docker compose down --remove-orphans --volumes 2>nul || docker-compose down --remove-orphans --volumes 2>nul || ver>nul'
                    }
                }
            }
        }

        stage('Build Test Image') {
            steps {
                script {
                    if (isUnix()) {
                        sh 'docker compose build test-runner mock-cpe 2>&1 || docker-compose build test-runner mock-cpe 2>&1'
                    } else {
                        bat 'docker compose build test-runner mock-cpe 2>&1 || docker-compose build test-runner mock-cpe 2>&1'
                    }
                }
                echo 'Docker images built: mock-cpe + test-runner'
            }
        }

        stage('Run Full Test Suite') {
            parallel {
                stage('Run Unit Tests') {
                    steps {
                        catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                            script {
                                if (isUnix()) {
                                    sh '''
                                        docker rm -f "${TEST_UNIT_CONTAINER}" 2>/dev/null || true
                                        docker compose run -T --name "${TEST_UNIT_CONTAINER}" \
                                            -e "PYTEST_ARGS=${PYTEST_UNIT_ARGS}" \
                                            -e "MOCK_CPE_DEVICE_DELAY_SCALE=${MOCK_CPE_DEVICE_DELAY_SCALE}" \
                                            -e "COVERAGE_FILE=${COVERAGE_UNIT_FILE}" \
                                            test-runner
                                    '''
                                } else {
                                    bat '''
                                        docker rm -f "%TEST_UNIT_CONTAINER%" 2>nul || ver>nul
                                        docker compose run -T --name "%TEST_UNIT_CONTAINER%" ^
                                            -e "PYTEST_ARGS=%PYTEST_UNIT_ARGS%" ^
                                            -e "MOCK_CPE_DEVICE_DELAY_SCALE=%MOCK_CPE_DEVICE_DELAY_SCALE%" ^
                                            -e "COVERAGE_FILE=%COVERAGE_UNIT_FILE%" ^
                                            test-runner
                                    '''
                                }
                            }
                        }
                    }
                }

                stage('Run API Tests') {
                    steps {
                        catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                            script {
                                if (isUnix()) {
                                    sh '''
                                        docker rm -f "${TEST_API_CONTAINER}" 2>/dev/null || true
                                        docker compose run -T --name "${TEST_API_CONTAINER}" \
                                            -e "PYTEST_ARGS=${PYTEST_API_ARGS}" \
                                            -e "MOCK_CPE_DEVICE_DELAY_SCALE=${MOCK_CPE_DEVICE_DELAY_SCALE}" \
                                            -e "COVERAGE_FILE=${COVERAGE_API_FILE}" \
                                            test-runner
                                    '''
                                } else {
                                    bat '''
                                        docker rm -f "%TEST_API_CONTAINER%" 2>nul || ver>nul
                                        docker compose run -T --name "%TEST_API_CONTAINER%" ^
                                            -e "PYTEST_ARGS=%PYTEST_API_ARGS%" ^
                                            -e "MOCK_CPE_DEVICE_DELAY_SCALE=%MOCK_CPE_DEVICE_DELAY_SCALE%" ^
                                            -e "COVERAGE_FILE=%COVERAGE_API_FILE%" ^
                                            test-runner
                                    '''
                                }
                            }
                        }
                    }
                }

                stage('Run Web-UI Route Tests') {
                    steps {
                        catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                            script {
                                if (isUnix()) {
                                    sh '''
                                        docker rm -f "${TEST_WEB_CONTAINER}" 2>/dev/null || true
                                        docker compose run -T --name "${TEST_WEB_CONTAINER}" \
                                            -e "PYTEST_ARGS=${PYTEST_WEB_ARGS}" \
                                            -e "MOCK_CPE_DEVICE_DELAY_SCALE=${MOCK_CPE_DEVICE_DELAY_SCALE}" \
                                            -e "COVERAGE_FILE=${COVERAGE_WEB_FILE}" \
                                            test-runner
                                    '''
                                } else {
                                    bat '''
                                        docker rm -f "%TEST_WEB_CONTAINER%" 2>nul || ver>nul
                                        docker compose run -T --name "%TEST_WEB_CONTAINER%" ^
                                            -e "PYTEST_ARGS=%PYTEST_WEB_ARGS%" ^
                                            -e "MOCK_CPE_DEVICE_DELAY_SCALE=%MOCK_CPE_DEVICE_DELAY_SCALE%" ^
                                            -e "COVERAGE_FILE=%COVERAGE_WEB_FILE%" ^
                                            test-runner
                                    '''
                                }
                            }
                        }
                    }
                }
            }
        }

        stage('Combine Coverage') {
            steps {
                catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                    script {
                        echo 'Combining coverage data from Unit, API, and Web-UI Route phases...'
                        if (isUnix()) {
                            sh '''
                                mkdir -p reports
                                docker rm -f "${COVERAGE_CONTAINER}" 2>/dev/null || true
                                docker cp "${TEST_UNIT_CONTAINER}:/app/.coverage.unit" .coverage.unit || true
                                docker cp "${TEST_API_CONTAINER}:/app/.coverage.api" .coverage.api || true
                                docker cp "${TEST_WEB_CONTAINER}:/app/.coverage.web" .coverage.web || true
                                test -s .coverage.unit
                                test -s .coverage.api
                                test -s .coverage.web
                                docker compose run -d --name "${COVERAGE_CONTAINER}" --entrypoint sleep test-runner 300
                                docker cp .coverage.unit "${COVERAGE_CONTAINER}:/app/.coverage.unit"
                                docker cp .coverage.api "${COVERAGE_CONTAINER}:/app/.coverage.api"
                                docker cp .coverage.web "${COVERAGE_CONTAINER}:/app/.coverage.web"
                                docker exec "${COVERAGE_CONTAINER}" bash -lc "cd /app && coverage combine .coverage.unit .coverage.api .coverage.web && coverage report --fail-under=95 && coverage xml -o /app/reports/coverage.xml"
                                docker cp "${COVERAGE_CONTAINER}:/app/reports/coverage.xml" reports/coverage.xml
                                docker rm -f "${COVERAGE_CONTAINER}" 2>/dev/null || true
                            '''
                        } else {
                            bat '''
                                if not exist reports mkdir reports
                                docker rm -f "%COVERAGE_CONTAINER%" 2>nul || ver>nul
                                docker cp "%TEST_UNIT_CONTAINER%:/app/.coverage.unit" .coverage.unit 2>nul || ver>nul
                                docker cp "%TEST_API_CONTAINER%:/app/.coverage.api" .coverage.api 2>nul || ver>nul
                                docker cp "%TEST_WEB_CONTAINER%:/app/.coverage.web" .coverage.web 2>nul || ver>nul
                                if not exist .coverage.unit exit /b 1
                                if not exist .coverage.api exit /b 1
                                if not exist .coverage.web exit /b 1
                                docker compose run -d --name "%COVERAGE_CONTAINER%" --entrypoint sleep test-runner 300
                                docker cp .coverage.unit "%COVERAGE_CONTAINER%:/app/.coverage.unit"
                                docker cp .coverage.api "%COVERAGE_CONTAINER%:/app/.coverage.api"
                                docker cp .coverage.web "%COVERAGE_CONTAINER%:/app/.coverage.web"
                                docker exec "%COVERAGE_CONTAINER%" bash -lc "cd /app && coverage combine .coverage.unit .coverage.api .coverage.web && coverage report --fail-under=95 && coverage xml -o /app/reports/coverage.xml"
                                docker cp "%COVERAGE_CONTAINER%:/app/reports/coverage.xml" reports/coverage.xml
                                docker rm -f "%COVERAGE_CONTAINER%" 2>nul || ver>nul
                            '''
                        }
                        echo 'Coverage combined from: .coverage.unit + .coverage.api + .coverage.web'
                        echo 'Final coverage threshold: 95% (enforced by coverage report --fail-under=95)'
                        echo "Combined coverage XML: reports/coverage.xml"
                        if (fileExists('reports/coverage.xml')) {
                            def covXml = readFile('reports/coverage.xml')
                            def m = covXml =~ /line-rate="([0-9.]+)"/
                            if (m.find()) {
                                def combinedPct = formatCoverageRate(m.group(1))
                                echo "COVERAGE GATE RESULT: ${combinedPct} (threshold >= 95%)"
                            } else {
                                echo "WARNING: Could not extract coverage line-rate from coverage.xml"
                            }
                        } else {
                            echo "WARNING: coverage.xml not found after combine"
                        }
                    }
                }
            }
        }

        stage('Run Selenium Web-UI Tests') {
            when {
                expression { return params.RUN_UI_SMOKE }
            }
            steps {
                script {
                    if (isUnix()) {
                        sh 'APP_BUILD_VERSION="Build #${BUILD_NUMBER}" APP_BUILD_NUMBER="${BUILD_NUMBER}" APP_BUILD_URL="${BUILD_URL}" APP_FIRMWARE_BASELINE="${BASELINE_FIRMWARE_VERSION}" APP_FIRMWARE_TARGET="" docker compose up -d mock-cpe selenium 2>&1'
                    } else {
                        bat '''
                            set "APP_BUILD_VERSION=Build #%BUILD_NUMBER%"
                            set "APP_BUILD_NUMBER=%BUILD_NUMBER%"
                            set "APP_BUILD_URL=%BUILD_URL%"
                            set "APP_FIRMWARE_BASELINE=%BASELINE_FIRMWARE_VERSION%"
                            set "APP_FIRMWARE_TARGET="
                            docker compose up -d mock-cpe selenium 2>&1
                        '''
                    }
                    if (isUnix()) {
                        sh '''
                            for i in $(seq 1 30); do
                                status=$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}running{{end}}' selenium-chrome 2>/dev/null || true)
                                [ "$status" = "healthy" ] && exit 0
                                [ "$status" = "running" ] && [ "$i" -ge 8 ] && exit 0
                                sleep 1
                            done
                            docker logs selenium-chrome --tail 80 || true
                            exit 1
                        '''
                    } else {
                        bat '''
                            powershell -NoProfile -Command "$deadline=(Get-Date).AddSeconds(30); do { $status=(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}running{{end}}' selenium-chrome 2>$null); if ($status -eq 'healthy') { exit 0 }; if ($status -eq 'running' -and (Get-Date) -gt $deadline.AddSeconds(-22)) { exit 0 }; Start-Sleep -Seconds 1 } while ((Get-Date) -lt $deadline); docker logs selenium-chrome --tail 80; exit 1"
                        '''
                    }
                    catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                        if (isUnix()) {
                            sh '''
                                docker rm -f "${TEST_UI_CONTAINER}" 2>/dev/null || true
                                docker compose run -T --name "${TEST_UI_CONTAINER}" \
                                    -e "PYTEST_ARGS=${PYTEST_UI_SMOKE_ARGS}" \
                                    -e "MOCK_CPE_DEVICE_DELAY_SCALE=${MOCK_CPE_DEVICE_DELAY_SCALE}" \
                                    test-runner
                            '''
                        } else {
                            bat '''
                                docker rm -f "%TEST_UI_CONTAINER%" 2>nul || ver>nul
                                docker compose run -T --name "%TEST_UI_CONTAINER%" ^
                                    -e "PYTEST_ARGS=%PYTEST_UI_SMOKE_ARGS%" ^
                                    -e "MOCK_CPE_DEVICE_DELAY_SCALE=%MOCK_CPE_DEVICE_DELAY_SCALE%" ^
                                    test-runner
                            '''
                        }
                    }
                }
            }
        }

        stage('Extract Artifacts') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            rm -rf allure-results screenshots
                            mkdir -p allure-results reports screenshots
                            docker cp "${TEST_UNIT_CONTAINER}:/app/allure-results/unit" ./allure-results/unit || true
                            docker cp "${TEST_API_CONTAINER}:/app/allure-results/api" ./allure-results/api || true
                            docker cp "${TEST_WEB_CONTAINER}:/app/allure-results/web" ./allure-results/web || true
                            docker cp "${TEST_UNIT_CONTAINER}:/app/reports/unit_report.json" ./reports/unit_report.json || true
                            docker cp "${TEST_UNIT_CONTAINER}:/app/reports/unit-junit.xml" ./reports/unit-junit.xml || true
                            docker cp "${TEST_API_CONTAINER}:/app/reports/api_report.json" ./reports/api_report.json || true
                            docker cp "${TEST_API_CONTAINER}:/app/reports/api-junit.xml" ./reports/api-junit.xml || true
                            docker cp "${TEST_WEB_CONTAINER}:/app/reports/web_report.json" ./reports/web_report.json || true
                            docker cp "${TEST_WEB_CONTAINER}:/app/reports/web-junit.xml" ./reports/web-junit.xml || true
                            if [ -n "${RUN_UI_SMOKE}" ] && [ "${RUN_UI_SMOKE}" = "true" ]; then
                                docker cp "${TEST_UI_CONTAINER}:/app/allure-results/ui" ./allure-results/ui || true
                                docker cp "${TEST_UI_CONTAINER}:/app/reports/ui_report.json" ./reports/ui_report.json || true
                                docker cp "${TEST_UI_CONTAINER}:/app/reports/ui-junit.xml" ./reports/ui-junit.xml || true
                                docker cp "${TEST_UI_CONTAINER}:/app/screenshots" ./screenshots || true
                            fi
                            chmod -R a+rwX allure-results reports screenshots 2>/dev/null || true
                            find allure-results -type f | wc -l
                        '''
                    } else {
                        bat '''
                            if exist allure-results rmdir /s /q allure-results
                            if exist screenshots rmdir /s /q screenshots
                            if not exist reports mkdir reports
                            mkdir allure-results screenshots
                            docker cp "%TEST_UNIT_CONTAINER%:/app/allure-results/unit" ./allure-results/unit 2>nul || ver>nul
                            docker cp "%TEST_API_CONTAINER%:/app/allure-results/api" ./allure-results/api 2>nul || ver>nul
                            docker cp "%TEST_WEB_CONTAINER%:/app/allure-results/web" ./allure-results/web 2>nul || ver>nul
                            docker cp "%TEST_UNIT_CONTAINER%:/app/reports/unit_report.json" ./reports/unit_report.json 2>nul || ver>nul
                            docker cp "%TEST_UNIT_CONTAINER%:/app/reports/unit-junit.xml" ./reports/unit-junit.xml 2>nul || ver>nul
                            docker cp "%TEST_API_CONTAINER%:/app/reports/api_report.json" ./reports/api_report.json 2>nul || ver>nul
                            docker cp "%TEST_API_CONTAINER%:/app/reports/api-junit.xml" ./reports/api-junit.xml 2>nul || ver>nul
                            docker cp "%TEST_WEB_CONTAINER%:/app/reports/web_report.json" ./reports/web_report.json 2>nul || ver>nul
                            docker cp "%TEST_WEB_CONTAINER%:/app/reports/web-junit.xml" ./reports/web-junit.xml 2>nul || ver>nul
                            if /I "%RUN_UI_SMOKE%"=="true" (
                                docker cp "%TEST_UI_CONTAINER%:/app/allure-results/ui" ./allure-results/ui 2>nul || ver>nul
                                docker cp "%TEST_UI_CONTAINER%:/app/reports/ui_report.json" ./reports/ui_report.json 2>nul || ver>nul
                                docker cp "%TEST_UI_CONTAINER%:/app/reports/ui-junit.xml" ./reports/ui-junit.xml 2>nul || ver>nul
                                docker cp "%TEST_UI_CONTAINER%:/app/screenshots" ./screenshots 2>nul || ver>nul
                            )
                            dir allure-results
                        '''
                    }
                }
            }
        }

        stage('Publish Test Results') {
            steps {
                junit testResults: 'reports/*-junit.xml',
                      allowEmptyResults: false,
                      keepLongStdio: true
            }
        }

        stage('Prepare Report Metadata') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            python3 --version >/dev/null 2>&1 && PY=python3 || PY=python
                            $PY scripts/prepare_allure_metadata.py \
                                --allure-results allure-results \
                                --reports reports \
                                --jenkins-url "${JENKINS_URL}" \
                                --job-name "${JOB_NAME}" \
                                --build-number "${BUILD_NUMBER}" \
                                --build-url "${BUILD_URL}"
                            $PY scripts/generate_ci_dashboard.py \
                                --reports reports \
                                --output reports/jenkins-dashboard.html \
                                --job-name "${JOB_NAME}" \
                                --build-number "${BUILD_NUMBER}" \
                                --build-url "${BUILD_URL}" \
                                --blue-url "${JENKINS_URL}blue/organizations/jenkins/${JOB_NAME}/detail/${JOB_NAME}/${BUILD_NUMBER}/pipeline/" \
                                --allure-url "${BUILD_URL}allure/"
                        '''
                    } else {
                        bat '''
                            python scripts/prepare_allure_metadata.py --allure-results allure-results --reports reports --jenkins-url "%JENKINS_URL%" --job-name "%JOB_NAME%" --build-number "%BUILD_NUMBER%" --build-url "%BUILD_URL%"
                            python scripts/generate_ci_dashboard.py --reports reports --output reports/jenkins-dashboard.html --job-name "%JOB_NAME%" --build-number "%BUILD_NUMBER%" --build-url "%BUILD_URL%" --blue-url "%JENKINS_URL%blue/organizations/jenkins/%JOB_NAME%/detail/%JOB_NAME%/%BUILD_NUMBER%/pipeline/" --allure-url "%BUILD_URL%allure/"
                        '''
                    }
                }
            }
        }

        stage('Generate Allure Report') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            test -x /opt/allure/bin/allure
                            result_dirs=$(find allure-results -mindepth 1 -maxdepth 1 -type d | sort)
                            test -n "${result_dirs}"
                            /opt/allure/bin/allure generate ${result_dirs} -o allure-report --clean
                            echo "Allure report generated at: allure-report/"
                        '''
                    } else {
                        bat '''
                            if not exist allure-results exit /b 1
                            wsl sh -lc "result_dirs=$(find allure-results -mindepth 1 -maxdepth 1 -type d | sort); test -n \"$result_dirs\"; /opt/allure/bin/allure generate $result_dirs -o allure-report --clean"
                        '''
                    }
                }
            }
        }

        stage('Publish Allure Report') {
            steps {
                allure(
                    commandline: 'Allure',
                    includeProperties: false,
                    jdk: '',
                    results: [
                        [path: 'allure-results/unit'],
                        [path: 'allure-results/api'],
                        [path: 'allure-results/web'],
                        [path: 'allure-results/ui']
                    ]
                )
            }
        }

        stage('Archive Artifacts') {
            steps {
                publishHTML(
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'reports',
                    reportFiles: 'jenkins-dashboard.html',
                    reportName: 'CI Dashboard'
                )
                archiveArtifacts artifacts: 'allure-report/**, reports/**, screenshots/**',
                                 allowEmptyArchive: false
                script {
                    setJenkinsStatusPageSummary()
                }
            }
        }
    }

    post {
        always {
            script {
                if (isUnix()) {
                    sh 'docker rm -f "${TEST_UNIT_CONTAINER}" "${TEST_API_CONTAINER}" "${TEST_WEB_CONTAINER}" "${TEST_UI_CONTAINER}" "${COVERAGE_CONTAINER}" 2>/dev/null || true'
                    sh 'docker compose down --remove-orphans --volumes 2>/dev/null || true'
                } else {
                    bat 'docker rm -f "%TEST_UNIT_CONTAINER%" "%TEST_API_CONTAINER%" "%TEST_WEB_CONTAINER%" "%TEST_UI_CONTAINER%" "%COVERAGE_CONTAINER%" 2>nul || ver>nul'
                    bat 'docker compose down --remove-orphans --volumes 2>nul || ver>nul'
                }
            }
            echo 'Pipeline finished. Environment cleaned up.'
            script {
                def buildResult = currentBuild.currentResult ?: 'SUCCESS'
                if (buildResult == 'SUCCESS') {
                    echo 'Redeploying gateway web from the latest successful build...'
                    if (isUnix()) {
                        sh '''
                            APP_BUILD_VERSION="Build #${BUILD_NUMBER}" APP_BUILD_NUMBER="${BUILD_NUMBER}" APP_BUILD_URL="${BUILD_URL}" APP_FIRMWARE_BASELINE="${BASELINE_FIRMWARE_VERSION}" APP_FIRMWARE_TARGET="${TARGET_FIRMWARE_VERSION}" docker compose up -d --build mock-cpe 2>&1
                            docker exec mock-cpe python - <<'PY'
import time
import urllib.request

for i in range(20):
    try:
        with urllib.request.urlopen("http://127.0.0.1:5000", timeout=2) as resp:
            print(f"Gateway web healthy: HTTP {resp.status}")
            raise SystemExit(0)
    except Exception as exc:
        print(f"Waiting for gateway web ({i + 1}/20): {exc}")
        time.sleep(1)

raise SystemExit(1)
PY
                        '''
                    } else {
                        bat '''
                            set "APP_BUILD_VERSION=Build #%BUILD_NUMBER%"
                            set "APP_BUILD_NUMBER=%BUILD_NUMBER%"
                            set "APP_BUILD_URL=%BUILD_URL%"
                            set "APP_FIRMWARE_BASELINE=%BASELINE_FIRMWARE_VERSION%"
                            set "APP_FIRMWARE_TARGET=%TARGET_FIRMWARE_VERSION%"
                            docker compose up -d --build mock-cpe 2>&1
                            docker exec mock-cpe python -c "import urllib.request; r=urllib.request.urlopen('http://127.0.0.1:5000', timeout=10); print('Gateway web healthy: HTTP', r.status)"
                        '''
                    }
                    echo 'Gateway web redeployed: http://localhost:5000'
                } else {
                    echo "Gateway web redeploy skipped because build result is ${buildResult}."
                }
            }
            echo 'Check archived allure-report/ for the full test report.'
            script {
                if (fileExists('reports/test_metrics.json')) {
                    setJenkinsStatusPageSummary()
                }
            }
            script {
                def blueOceanUrl = "${env.JENKINS_URL}blue/organizations/jenkins/${env.JOB_NAME}/detail/${env.JOB_NAME}/${env.BUILD_NUMBER}/pipeline"
                def reportUrl = "${env.BUILD_URL}allure/"
                def consoleUrl = "${env.BUILD_URL}console"
                def subjectStatus = currentBuild.currentResult ?: 'UNKNOWN'

                try {
                    timeout(time: 45, unit: 'SECONDS') {
                        emailext(
                            to: params.EMAIL_TO,
                            replyTo: params.EMAIL_TO,
                            subject: "[Mock CPE DevOps] ${subjectStatus} - Build #${env.BUILD_NUMBER}",
                            mimeType: 'text/html',
                            attachLog: false,
                            attachmentsPattern: 'reports/jenkins-dashboard.html,reports/coverage.xml,reports/test_metrics.json',
                            body: """
                                <p>Mock CPE DevOps pipeline finished with status: <b>${subjectStatus}</b></p>
                                <ul>
                                  <li><a href="${env.BUILD_URL}">Jenkins build</a></li>
                                  <li><a href="${blueOceanUrl}">Blue Ocean pipeline view</a></li>
                                  <li><a href="${consoleUrl}">Console output</a></li>
                                  <li><a href="${reportUrl}">Allure report</a></li>
                                </ul>
                                <p>Job: ${env.JOB_NAME}<br/>Build: #${env.BUILD_NUMBER}</p>
                            """
                        )
                    }
                    echo "Email notification requested for ${params.EMAIL_TO}."
                } catch (err) {
                    error "Email notification failed. Configure Jenkins SMTP/Gmail app password, then rerun: ${err}"
                }
            }
        }
        success {
            echo 'All stages passed: Mock CPE DevOps pipeline succeeded.'
        }
        failure {
            echo 'Pipeline failed: review stage logs and archived artifacts.'
        }
    }
}
