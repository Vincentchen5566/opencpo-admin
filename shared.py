"""
Shared helpers for CPO Admin route modules.

All route modules import from here — never from main.py.
"""
import os
import logging

import httpx
from fastapi.templating import Jinja2Templates

logger = logging.getLogger(__name__)

# OCPP Core API
CORE_API = os.getenv("OCPP_CORE_API_URL", os.getenv("OCPP_CORE_API", "http://localhost:8000")) #
CORE_API_KEY = os.getenv("MANAGEMENT_API_KEY", "MySuperSecretKey123") # new add 01/06/2026 強行綁定key值，確保後台能正常認證做測試用
APP_TITLE = os.getenv("APP_TITLE", "OpenCPO Admin")
PKI_DATA_DIR = os.getenv("PKI_DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "ocpp-core", "data", "pki"))

# Templates (shared instance)
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))
templates.env.globals["app_title"] = APP_TITLE


# async def api(path: str, method: str = "GET", json: dict = None) -> dict:
#     """Call OCPP Core API."""
#     headers = {"X-API-Key": CORE_API_KEY} if CORE_API_KEY else {}
#     async with httpx.AsyncClient(base_url=CORE_API, timeout=10, headers=headers) as client:
#         if method == "GET":
#             r = await client.get(f"/api/v1{path}")
#         elif method == "POST":
#             r = await client.post(f"/api/v1{path}", json=json)
#         elif method == "PUT":
#             r = await client.put(f"/api/v1{path}", json=json)
#         elif method == "DELETE":
#             r = await client.delete(f"/api/v1{path}")
#         r.raise_for_status()
#         return r.json()
async def api(path: str, method: str = "GET", json: dict = None) -> dict:
    """Call OCPP Core API."""
    headers = {"X-API-Key": CORE_API_KEY} if CORE_API_KEY else {}

   # 🌟 這裡就是後台的 console.log！
    # print("\n" + "═"*30 + " 📡 【後台發送端 Debug】 " + "═"*30)
    # print(f"  👉 正在請求路徑 (Path): [{method}] {path}")
    # print(f"  👉 從 .env 讀到的 MANAGEMENT_API_KEY 值為: '{CORE_API_KEY}'")
    # print(f"  👉 實際塞進 HTTP 信封 Header 的 X-API-Key 為: '{headers.get('X-API-Key')}'")
    # print("═"*85 + "\n")

    # 后台log記錄：每次發送API請求時，將請求方法、路徑和使用的API Key（從環境變量讀取）打印出來，方便調試和追蹤。這樣即使前端沒有提供API Key，後台也能清楚看到實際使用的值，幫助定位問題。

    async with httpx.AsyncClient(base_url=CORE_API, timeout=10, headers=headers) as client:
        try:
            if method == "GET":
                r = await client.get(f"/api/v1{path}")
            elif method == "POST":
                r = await client.post(f"/api/v1{path}", json=json)
            elif method == "PUT":
                r = await client.put(f"/api/v1{path}", json=json)
            elif method == "DELETE":
                r = await client.delete(f"/api/v1{path}")
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.error(f"⚠️ API 請求被攔截 [{path}]: {e}")
            # 如果是 PKI 統計接口崩潰，直接返回安全預設結構，絕不向上拋出錯誤
            if "pki" in path:
                return {"status": "unknown", "total": 0, "active": 0, "expired": 0, "certs": []}
            return {}