@echo off
chcp 65001 >nul
title SkyMark v2.0
cd /d "%~dp0"
py skymark.py
