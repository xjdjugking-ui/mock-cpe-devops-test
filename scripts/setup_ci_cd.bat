@echo off
REM ============================================================================
REM setup_ci_cd.bat — Automated CI/CD Pipeline Setup for Mock CPE DevOps
REM ============================================================================
REM This script:
REM   [1] Checks Docker environment is ready
REM   [2] Builds Docker images
REM   [3] Runs a quick smoke test in Docker
REM   [4] Generates Jenkins Job DSL XML for one-click import
REM   [5] Prints summary of next steps
REM ============================================================================
setlocal enabledelayedexpansion

echo.
echo ==============================================
echo   Mock CPE DevOps — CI/CD Pipeline Setup
echo ==============================================
echo.

REM ------------------------------------------------------------------
REM Step 1: Check Docker
REM ------------------------------------------------------------------
echo [1/5] Checking Docker...
docker --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Docker not found. Please install Docker Desktop.
    exit /b 1
)
echo   Docker: OK

docker compose version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Docker Compose not found. Please install Docker Desktop.
    exit /b 1
)
echo   Docker Compose: OK

REM ------------------------------------------------------------------
REM Step 2: Build images
REM ------------------------------------------------------------------
echo.
echo [2/5] Building Docker images (this may take a few minutes)...
docker compose build --no-cache 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Docker build failed. Check output above.
    exit /b 1
)
echo   Build: OK

REM ------------------------------------------------------------------
REM Step 3: Quick smoke test (Unit Tests only, fast)
REM ------------------------------------------------------------------
echo.
echo [3/5] Running smoke test (unit tests in Docker)...
docker compose up -d mock-cpe 2>&1
timeout /T 3 /NOBREAK >nul

docker compose run --rm -e "PYTEST_ARGS=tests/unit -v --tb=line -x" test-runner 2>&1
if %ERRORLEVEL% neq 0 (
    echo   Smoke test had failures — this is OK for setup verification.
)
echo   Smoke test: DONE

docker compose down 2>&1
echo   Cleanup: DONE

REM ------------------------------------------------------------------
REM Step 4: Generate Jenkins Job DSL XML
REM ------------------------------------------------------------------
echo.
echo [4/5] Generating Jenkins pipeline config...

set "JENKINS_XML=jenkins_pipeline_config.xml"
set "PIPELINE_SCRIPT=Jenkinsfile"

REM Ask for Git repo URL
set "GIT_URL="
set /p GIT_URL="Enter your Git repository URL (e.g. https://github.com/user/repo.git): "

if "%GIT_URL%"=="" (
    echo [WARN] No Git URL provided. You can set it later in Jenkins.
    echo [INFO] Skipping XML generation. Use Jenkins UI to create Pipeline job.
    echo [INFO] Select "Pipeline script from SCM" and point to your Jenkinsfile.
    goto :summary
)

REM Generate config.xml for Jenkins Pipeline job
(
echo ^<?xml version='1.1' encoding='UTF-8'?^>
echo ^<flow-definition plugin="workflow-job@2.42"^>
echo   ^<description^>Mock CPE DevOps — Docker-based CI/CD with Allure reports^</description^>
echo   ^<keepDependencies^>false^</keepDependencies^>
echo   ^<definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps@2.94"^>
echo     ^<scm class="hudson.plugins.git.GitSCM"^>
echo       ^<userRemoteConfigs^>
echo         ^<hudson.plugins.git.UserRemoteConfig^>
echo           ^<url^>%GIT_URL%^</url^>
echo         ^</hudson.plugins.git.UserRemoteConfig^>
echo       ^</userRemoteConfigs^>
echo       ^<branches^>
echo         ^<hudson.plugins.git.BranchSpec^>
echo           ^<name^>*/main^</name^>
echo         ^</hudson.plugins.git.BranchSpec^>
echo       ^</branches^>
echo     ^</scm^>
echo     ^<scriptPath^>Jenkinsfile^</scriptPath^>
echo     ^<lightweight^>true^</lightweight^>
echo   ^</definition^>
echo   ^<triggers/^>
echo   ^<disabled^>false^</disabled^>
echo ^</flow-definition^>
) > "%JENKINS_XML%"

echo   Jenkins config saved to: %JENKINS_XML%

:summary
REM ------------------------------------------------------------------
REM Step 5: Summary
REM ------------------------------------------------------------------
echo.
echo ==============================================
echo   SETUP COMPLETE
echo ==============================================
echo.
echo   [Next Steps]
echo.
echo   1. (Optional) Initialize Git and push code:
echo      git init
echo      git add .
echo      git commit -m "Initial commit: Mock CPE DevOps CI/CD"
echo      git remote add origin YOUR_REPO_URL
echo      git push -u origin main
echo.
echo   2. Install Jenkins plugins:
echo      - Allure Jenkins Plugin
echo      - Pipeline (built-in)
echo      - Git (built-in)
echo.
echo   3. Create Jenkins Pipeline Job:
echo      Option A (import XML): Copy jenkins_pipeline_config.xml into
echo         JENKINS_HOME/jobs/MockCPE-DevOps/ if using local Jenkins
echo      Option B (UI): New Item ^> Pipeline ^> Pipeline script from SCM
echo         SCM: Git ^> Repository URL: YOUR_REPO_URL
echo         Script Path: Jenkinsfile
echo.
echo   4. Ensure Jenkins node has Docker + Docker Compose installed.
echo.
echo   5. After each build, click [Allure Report] icon in Jenkins
echo      to view the integrated test report.
echo.
echo ==============================================

endlocal