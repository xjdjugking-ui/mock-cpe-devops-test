// Jenkinsfile — Mock CPE DevOps CI/CD Pipeline (Docker-based)
// Thesis: 面向 DevOps 持续交付的智能网关 Web 自动化测试设计与实施
//
// Prerequisites:
//   - Jenkins node with Docker + Docker Compose installed
//   - Allure Jenkins Plugin installed
//   - No real CPE hardware required (MockDeviceAdapter used)
//   - No local Python/ChromeDriver needed (everything runs in Docker)

pipeline {
    agent any

    environment {
        COMPOSE_FILE = 'docker-compose.yml'
        // Allure results aggregated into workspace for Jenkins plugin
        ALLURE_RESULTS_DIR = 'allure-results'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                echo "Source checked out: ${env.GIT_COMMIT}"
            }
        }

        stage('Build Docker Images') {
            steps {
                script {
                    if (isUnix()) {
                        sh 'docker compose build --no-cache'
                    } else {
                        bat 'docker compose build --no-cache'
                    }
                }
                echo "Docker images built: mock-cpe + test-runner"
            }
        }

        stage('Start Services') {
            steps {
                script {
                    if (isUnix()) {
                        sh 'docker compose up -d mock-cpe selenium'
                    } else {
                        bat 'docker compose up -d mock-cpe selenium'
                    }
                }
                // Give services time to be ready
                sleep 10
                echo "Mock CPE + Selenium Chrome services running"
            }
        }

        stage('Run Unit Tests') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''docker compose run --rm \
                            -e PYTEST_ARGS="tests/unit -v --tb=short --alluredir=/app/allure-results/unit --json-report --json-report-file=/app/reports/unit_report.json" \
                            test-runner'''
                    } else {
                        bat '''docker compose run --rm ^
                            -e PYTEST_ARGS="tests/unit -v --tb=short --alluredir=/app/allure-results/unit --json-report --json-report-file=/app/reports/unit_report.json" ^
                            test-runner'''
                    }
                }
            }
        }

        stage('Run API Tests') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''docker compose run --rm \
                            -e PYTEST_ARGS="tests/api -v --tb=short --alluredir=/app/allure-results/api --json-report --json-report-file=/app/reports/api_report.json" \
                            test-runner'''
                    } else {
                        bat '''docker compose run --rm ^
                            -e PYTEST_ARGS="tests/api -v --tb=short --alluredir=/app/allure-results/api --json-report --json-report-file=/app/reports/api_report.json" ^
                            test-runner'''
                    }
                }
            }
        }

        stage('Run UI Tests') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''docker compose run --rm \
                            -e PYTEST_ARGS="tests/ui -v --tb=short --alluredir=/app/allure-results/ui --json-report --json-report-file=/app/reports/ui_report.json" \
                            test-runner'''
                    } else {
                        bat '''docker compose run --rm ^
                            -e PYTEST_ARGS="tests/ui -v --tb=short --alluredir=/app/allure-results/ui --json-report --json-report-file=/app/reports/ui_report.json" ^
                            test-runner'''
                    }
                }
            }
        }

        stage('Generate Coverage') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''docker compose run --rm \
                            -e PYTEST_ARGS="tests/unit tests/api --cov=app --cov=cpe_devops --cov-report=term-missing --cov-report=xml:/app/reports/coverage.xml" \
                            test-runner'''
                    } else {
                        bat '''docker compose run --rm ^
                            -e PYTEST_ARGS="tests/unit tests/api --cov=app --cov=cpe_devops --cov-report=term-missing --cov-report=xml:/app/reports/coverage.xml" ^
                            test-runner'''
                    }
                }
            }
        }

        stage('Generate Allure Report') {
            steps {
                // Jenkins Allure Plugin — aggregate all allure-results subdirectories
                allure includeProperties: false, jdk: '',
                       results: [[path: 'allure-results/unit'],
                                 [path: 'allure-results/api'],
                                 [path: 'allure-results/ui']]
            }
        }

        stage('Archive Artifacts') {
            steps {
                archiveArtifacts artifacts: 'reports/**,allure-results/**,screenshots/**',
                                 allowEmptyArchive: true
            }
        }
    }

    post {
        always {
            script {
                if (isUnix()) {
                    sh 'docker compose down -v 2>/dev/null || true'
                } else {
                    bat 'docker compose down -v 2>nul || ver>nul'
                }
            }
            echo "Pipeline finished. Environment cleaned up."
            echo "Check Allure report for full test results."
        }
        success {
            echo "All stages passed — Mock CPE DevOps pipeline succeeded."
        }
        failure {
            echo "Pipeline failed — review stage logs and Allure report."
        }
    }
}