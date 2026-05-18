#!/bin/bash
set -e
cd /tmp
echo "Downloading Allure CLI..."
curl -L -o allure.tgz https://github.com/allure-framework/allure2/releases/download/2.33.0/allure-2.33.0.tgz
ls -la allure.tgz
mkdir -p /opt/allure
tar -xzf allure.tgz -C /opt/allure --strip-components=1
chmod +x /opt/allure/bin/allure
/opt/allure/bin/allure --version
echo "Allure installed successfully!"