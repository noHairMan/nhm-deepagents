import os

import pytest
from fastapi.testclient import TestClient

# 设置环境变量以确保配置正确加载
os.environ["TOMORROW_APP"] = "tomorrow"
os.environ["TOMORROW_SETTINGS_MODULE"] = "tomorrow.settings"
os.environ["RAINY_APP"] = "rainy"
os.environ["RAINY_SETTINGS_MODULE"] = "rainy.settings"

from rainy.app import app

client = TestClient(app)


def test_health_check_wrapped():
    """验证健康检查路径现在也被包装"""
    # 注意：urls.py 中有 prefix="/api"，所以路径是 /api/health
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    # 现在 /api/health 不在排除列表中，所以应该被包装
    assert "code" in data
    assert data["code"] == 0
    assert "data" in data
    assert data["data"] == {"status": "ok"}
    assert data["message"] == "成功"


def test_chat_response_wrapped():
    """验证聊天接口返回被包装"""
    response = client.post("/api/chat", json={"message": "hello"})
    assert response.status_code == 200
    data = response.json()
    assert "code" in data
    assert data["code"] == 0
    assert "data" in data
    assert data["data"] is None  # chat 接口目前返回 None
    assert data["message"] == "成功"


if __name__ == "__main__":
    # 手动运行测试
    test_health_check_wrapped()
    test_chat_response_wrapped()
    print("Tests passed!")
