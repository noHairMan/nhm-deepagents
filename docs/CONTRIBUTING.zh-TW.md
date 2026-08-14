# 貢獻指南

[簡體中文](/docs/CONTRIBUTING.zh.md)\|[英語](/docs/CONTRIBUTING.en.md)\|[日本人](/docs/CONTRIBUTING.ja.md)\|[繁體中文](/docs/CONTRIBUTING.zh-TW.md)

本文檔針對專案開發者與貢獻者，介紹開發環境、程式碼結構、品質檢查與測試方法。專案的背景、安裝、運作和設定說明請參閱[自述文件](README.zh.md)。

## 🛠️ 技術棧

-   **語言**:[Python](https://www.python.org/)>= 3.14
-   **套件管理器**:[紫外線](https://github.com/astral-sh/uv)
-   **API 框架**:[迅速](https://fastapi.tiangolo.com/)
-   **Web 伺服器**:[獨角獸](https://www.uvicorn.org/)
-   **智能體框架**:[深度代理](https://github.com/zongxuheng/deepagents)（基於 LangGraph/LangChain）
-   **LLM 提供者**:[成為](https://ollama.com/)、[人擇](https://www.anthropic.com/)和[開放人工智慧](https://openai.com/)
-   **程式碼執行**:[langchain-quickjs](https://github.com/langchain-ai/langchainjs)提供的 QuickJS 中介軟體
-   **終端交互**:`asyncclick`、`prompt-toolkit`和`Rich`
-   **配置管理**:[懸垂設定](https://docs.pydantic.dev/latest/usage/settings/)
-   **代碼品質**:[拉夫](https://github.com/astral-sh/ruff)、`pre-commit`和強制類型提示
-   **測試與覆蓋率**:`pytest`、`coverage`

## ⚙️ CI/CD

專案整合了 GitHub Actions 工作流程，包括：

-   **測試與覆蓋率**: 自動執行測試並檢查程式碼覆蓋率。
-   **文件翻譯**: 自動將`README.zh.md`和`CONTRIBUTING.zh.md`翻译为 English、日本語和繁体中文。
-   **程式碼規範**: 自動執行`ruff`檢查與格式化，確保程式碼風格統一。
-   **CI 流程優化**: 根據相關程式碼或配置變更觸發構建，減少不必要的建置任務。

## 📜 開發腳本

同步依賴並建立虛擬環境：

```bash
uv sync
```

檢查並格式化程式碼：

```bash
uv run ruff check . --fix
uv run ruff format .
```

手動運行`pre-commit`鉤子：

```bash
uv run pre-commit run --all-files
```

## 📂 專案結構

-   `src/main.py`: Rainy API 服務的主入口點。
-   `src/fragile/`: 非同步命令列客戶端，包含互動式會話、斜線命令、顯示和輸入處理。
-   `src/tomorrow/`: 核心智能體，實現 graph、模型、後端、檢查點、儲存和生命週期管理。
-   `src/rainy/`: API 服務，實現應用生命週期、聊天介面、健康檢查和中間件。
-   `tests/`: 測試目錄，結構與`src`保持一致。
-   `docs/`: 多國語言文件。
-   `pyproject.toml`: 專案元資料、依賴項和工具配置。
-   `langgraph.json`:`langgraph-cli`的 graph 與環境配置。
-   `uv.lock`: 鎖定依賴版本。

## 🧪 測試

項目使用`pytest`進行測試，並要求測試覆蓋率達到**100%**。

運行各模組測試：

```bash
PYTHONPATH=src TOMORROW_APP=tomorrow uv run pytest tests/tomorrow
PYTHONPATH=src RAINY_APP=rainy uv run pytest tests/rainy
PYTHONPATH=src FRAGILE_APP=fragile uv run pytest tests/fragile
```

執行完整覆蓋率測試：

```bash
PYTHONPATH=src \
TOMORROW_APP=tomorrow \
RAINY_APP=rainy \
FRAGILE_APP=fragile \
uv run coverage run --rcfile=pyproject.toml -m pytest -q && uv run coverage report --rcfile=pyproject.toml
```

測試文件應依照`src/`的模組路徑組織，並使用以`Test`開頭的測試類別包裹測試方法。
