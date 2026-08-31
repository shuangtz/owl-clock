name: Build Android APK

on:
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-22.04

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install Dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libstdc++6 cmake sysstat
          pip install --upgrade "buildozer<2.0.0" "cython<3.0.0"

      # 清除舊有的快取，確保乾淨編譯
      - name: Build with Buildozer
        run: |
          buildozer -v android debug
        env:
          ACCEPT_BUILD_LICENSES: "y"

      - name: Upload APK Artifact
        uses: actions/upload-artifact@v4
        with:
          name: app-debug
          path: bin/*.apk
