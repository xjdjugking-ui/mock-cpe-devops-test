@echo off
cd /d c:\Users\LPC\mock-cpe-devops-test
echo [START] %date% %time% > docker_full_output.txt
docker compose up --build -d >> docker_full_output.txt 2>&1
echo [END] %date% %time% RC=%ERRORLEVEL% >> docker_full_output.txt