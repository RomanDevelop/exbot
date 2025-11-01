#!/bin/bash
# Скрипт для запуска PolExamBot

cd "$(dirname "$0")"
source venv/bin/activate
python pol_exam_bot.py

