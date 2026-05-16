@echo off
cd /d c:\Users\LPC\mock-cpe-devops-test
docker compose up --build -d > docker_build_output.txt 2>&1
echo EXIT_CODE=%ERRORLEVEL% >> docker_build_output.txt