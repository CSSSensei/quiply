import logging
import sys
import os
import json
from datetime import datetime
from typing import Any, Dict, Optional, Union
from flask import request, g, current_app


class CustomJSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }
        
        if hasattr(request, 'endpoint'):
            if request.endpoint:
                log_record['endpoint'] = request.endpoint
            if request.method:
                log_record['method'] = request.method
            if request.path:
                log_record['path'] = request.path
            if request.remote_addr:
                log_record['remote_addr'] = request.remote_addr
        
        if hasattr(g, 'user_id'):
            log_record['user_id'] = g.user_id
        
        if hasattr(record, '__dict__'):
            extra_data = {k: v for k, v in record.__dict__.items()
                         if k not in ['name', 'msg', 'args', 'levelname', 'levelno',
                                    'pathname', 'filename', 'module', 'lineno',
                                    'funcName', 'created', 'msecs', 'relativeCreated',
                                    'thread', 'threadName', 'processName', 'process',
                                    'getMessage', 'exc_info', 'exc_text', 'stack_info']}
            log_record.update(extra_data)
        
        return json.dumps(log_record)


def setup_logger(app_name: str = 'quiply', log_level: str = 'INFO') -> logging.Logger:
    logger = logging.getLogger(app_name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    if not logger.handlers:
        formatter = CustomJSONFormatter()
        
        try:
            log_file = current_app.config.get('LOG_FILE')
            log_dir = current_app.config.get('LOG_DIR', 'logs')
        except RuntimeError:
            log_file = None
            log_dir = 'logs'
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        if log_file:
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            log_path = os.path.join(log_dir, log_file)
            file_handler = logging.FileHandler(log_path)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
    
    return logger


def log_error(logger: logging.Logger, error: Exception, context: Optional[Dict[str, Any]] = None):
    error_data: Dict[str, Union[str, int, Dict[str, Any]]] = {
        'error_type': type(error).__name__,
        'error_message': str(error),
    }
    
    if hasattr(error, 'status_code'):
        error_data['status_code'] = getattr(error, 'status_code')
    if hasattr(error, 'error_code'):
        error_data['error_code'] = getattr(error, 'error_code')
    if hasattr(error, 'details'):
        error_data['error_details'] = getattr(error, 'details')
    
    if context:
        error_data['context'] = context
    
    logger.error('Error occurred', extra={'extra_data': error_data})


def log_info(logger: logging.Logger, message: str, context: Optional[Dict[str, Any]] = None):
    log_data: Dict[str, Any] = {}
    if context:
        log_data['context'] = context
    
    logger.info(message, extra={'extra_data': log_data})


def log_warning(logger: logging.Logger, message: str, context: Optional[Dict[str, Any]] = None):
    log_data: Dict[str, Any] = {}
    if context:
        log_data['context'] = context
    
    logger.warning(message, extra={'extra_data': log_data})
