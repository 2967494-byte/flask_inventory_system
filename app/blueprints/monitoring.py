from flask import Blueprint, jsonify, current_app
from sqlalchemy import text
import psutil
import os
import time
from app import db

monitoring_bp = Blueprint('monitoring_bp', __name__, url_prefix='/monitoring')

@monitoring_bp.route('/basic')
def basic_check():
    """Базовая проверка доступности сервера (Liveness probe)"""
    return jsonify({
        "status": "ok",
        "message": "Service is running",
        "timestamp": time.time()
    }), 200

@monitoring_bp.route('/app')
def app_check():
    """Проверка зависимостей приложения (Database)"""
    status = "ok"
    details = {}
    http_status = 200

    # Проверка БД
    try:
        db.session.execute(text('SELECT 1'))
        details['database'] = "connected"
    except Exception as e:
        status = "error"
        details['database'] = f"error: {str(e)}"
        http_status = 503

    return jsonify({
        "status": status,
        "details": details,
        "timestamp": time.time()
    }), http_status

@monitoring_bp.route('/infra')
def infra_check():
    """Мониторинг инфраструктуры (CPU, RAM, Disk)"""
    try:
        # CPU
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # Memory
        memory = psutil.virtual_memory()
        memory_info = {
            "total": memory.total,
            "available": memory.available,
            "percent": memory.percent,
            "used": memory.used
        }

        # Disk
        disk = psutil.disk_usage('/')
        disk_info = {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent
        }

        # Uptime (boot time)
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time

        return jsonify({
            "status": "ok",
            "cpu": {
                "percent": cpu_percent
            },
            "memory": memory_info,
            "disk": disk_info,
            "uptime_seconds": uptime_seconds,
            "timestamp": time.time()
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
