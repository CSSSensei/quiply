from typing import Any, Dict, Optional, Tuple
from flask import jsonify, Response


class APIResponse:
    @staticmethod
    def success(data: Any = None, message: Optional[str] = None, status_code: int = 200) -> Tuple[Response, int]:
        response: Dict[str, Any] = {"success": True}
        if data is not None:
            response["data"] = data
        if message:
            response["message"] = message
        return jsonify(response), status_code
    
    @staticmethod
    def error(message: str, status_code: int, error_code: Optional[str] = None, details: Optional[Dict] = None) -> Tuple[Response, int]:
        response: Dict[str, Any] = {"success": False, "message": message}
        if error_code:
            response["error_code"] = error_code
        if details:
            response["details"] = details
        return jsonify(response), status_code
