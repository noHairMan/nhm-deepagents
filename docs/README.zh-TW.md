# NHM-深度代理

[![Imports: isort](https://img.shields.io/badge/imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://isort.readthedocs.io/)[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/noHairMan/nhm-deepagents/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/noHairMan/nhm-deepagents/blob/python-coverage-comment-action-data/htmlcov/index.html)

[簡體中文](/docs/README.zh.md)\|[英語](/docs/README.en.md)\|[日本人](/docs/README.ja.md)\|[繁體中文](/docs/README.zh-TW.md)

一個使用現代 LLM 框架建構和運行「深度智能體」（Deep Agents）的 Python 專案。

## 🌟 專案概覽

`nhm-deepagents`是一個專注於深度智能體的專業 Python 專案。它利用現代 Python 特性 (3.14+) 和強大的工具，為 AI 智能體研究和應用提供高品質的開發體驗。

專案內部包含兩個主要模組：

-   **`tomorrow`**: 核心智能體模組。代號取自遊戲《死亡擱淺 2：冥灘之上》（Death Stranding 2: On the Beach）中的角色**明天**（艾莉·範甯飾演）。在劇情中，她是主角山姆布里吉斯（Sam Bridges）的女兒，也被揭露為前作中的**大樓**(BB-28)。
-   **`rainy`**: 基於 FastAPI 的 API 服務模組。代號同樣取自《死亡擱淺 2》中的角色**下雨天**（由忽那汐裡飾演）。在遊戲中，她擁有引發「時間雨」（Timefall）和具有治癒能力的「核心雨」（Corefall）的神奇力量，被描述為既能傷害也能治癒的「藥（Pharmakon）」。本模組整合了統一回應格式、處理時間中間件等功能。

該專案目前包含一個通用的智慧助理智能體，可以使用`deepagents`框架分析使用者輸入並提供建議，並透過`rainy`模組對外提供同步（`/api/chat`）及流式（`/api/chat/stream`） API 介面。

## ⚙️ CI/CD

專案整合了 GitHub Actions 工作流程，包括：

-   **測試與覆蓋率**: 自動執行測試並檢查程式碼覆蓋率。
-   **文件翻譯**: 自動將`README.zh.md`翻译为多种语言（English, 日本語, 繁体中文）。
-   **程式碼規範**: 自動執行`black`和`isort`檢查。

## 🛠️ 技術棧

-   **語言**:[Python](https://www.python.org/)>= 3.14
-   **套件管理器**:[紫外線](https://github.com/astral-sh/uv)
-   **API 框架**:[迅速](https://fastapi.tiangolo.com/)
-   **Web 伺服器**:[獨角獸](https://www.uvicorn.org/)
-   **智能體框架**:[深度代理](https://github.com/zongxuheng/deepagents)(基於 LangGraph/LangChain)
-   **LLM 提供者**:[成為](https://ollama.com/)(透過`langchain-ollama`)
-   **配置管理**:[動態會議](https://www.dynaconf.com/)
-   **代碼品質**:`black`,`isort`,`pre-commit`, 類型提示 (Type Hinting)
-   **測試與覆蓋率**:`pytest`,`coverage`

## 📋 環境要求

-   **Python 3.14+**
-   **紫外線**: 一個快速的 Python 套件安裝和解析器。
-   **成為**: 必須正在運行且可存取。
-   **LLM 模型**: 預設使用的模型是`qwen3.5:9b`。您可以使用以下命令取得：
    ```bash
    ollama pull qwen3.5:9b
    ```

## 🚀 快速入門

### 安裝

1.  **安裝`uv`**:
    請按照[uv 官方倉庫](https://github.com/astral-sh/uv)中的說明進行操作。

2.  **克隆倉庫**:
    ```bash
    git clone <repository-url>
    cd nhm-deepagents
    ```

3.  **同步依賴並建立虛擬環境**:
    ```bash
    uv sync
    ```

4.  **安裝 pre-commit 鉤子**:
    ```bash
    uv run pre-commit install
    ```

5.  **啟動 Ollama 並取得模型**:
    ```bash
    ollama pull qwen3.5:9b
    ```

### 運行應用

運行主入口點：

```bash
uv run python src/main.py
```

## ⚙️ 配置

該項目使用**動態會議**進行配置管理。設定分別定義在`src/tomorrow/settings.py`（明天）和`src/rainy/settings.py`(Rainy) 中，可以透過環境變數或`.env`文件進行覆蓋。

### 環境變數

環境變數預設以前綴`TOMORROW_`(核心模組) 或`RAINY_`(API 模組) 開頭。

#### Tomorrow 配置 (核心)

| 變數                         | 描述             | 預設值                      |
| -------------------------- | -------------- | ------------------------ |
| `TOMORROW_OLLAMA_BASE_URL` | Ollama 服務的基底地址 | `http://localhost:11434` |
| `TOMORROW_DEFAULT_MODEL`   | 預設使用的 LLM 模型   | `qwen3.5:9b`             |
| `TOMORROW_APP`             | 應用名稱（用作環境變數前綴） | `tomorrow`               |
| `TOMORROW_SETTINGS_MODULE` | 設定模組的路徑        | `tomorrow.settings`      |
| `TOMORROW_CHECKPOINT`      | 檢查點配置          | `{"type": "memory"}`     |

#### Rainy 設定 (API)

| 變數                      | 描述             | 預設值              |
| ----------------------- | -------------- | ---------------- |
| `RAINY_HOST`            | API 服務監聽位址     | `localhost`      |
| `RAINY_PORT`            | API 服務連接埠      | `8000`           |
| `RAINY_APP`             | 應用名稱（用作環境變數前綴） | `rainy`          |
| `RAINY_SETTINGS_MODULE` | 設定模組的路徑        | `rainy.settings` |
| `RAINY_MIDDLEWARE`      | 啟用的中間件列表       | (見 settings.py)  |

## 📜 腳本

常用的開發腳本：

-   **格式化程式碼**:
    ```bash
    uv run black .
    uv run isort .
    ```

-   **手動運行 pre-commit 鉤子**:
    ```bash
    uv run pre-commit run --all-files
    ```

## 📂 專案結構

-   `src/main.py`: 應用的主入口點。設定環境並啟動 Uvicorn 伺服器。
-   `src/tomorrow/`: 核心智能體包目錄。
    -   `core/agent.py`: 定義深度智能體及其指令。
    -   `core/checkpoints/`: 檢查點實作（Memory, SQLite 等）。
    -   `settings.py`: 預設配置值。
    -   `utils/functional.py`: 功能實用程式。
-   `src/rainy/`: API 服務包目錄。
    -   `app.py`: FastAPI 應用程式定義。
    -   `api/endpoints/`: API 路由定義。
        -   `chat.py`: 同步及串流聊天接口，整合了深度智能體模組。
        -   `health.py`: 健康檢查介面。
        -   `urls.py`: 統一路由掛載。
    -   `middleware/`: 自訂中間件（處理時間、統一回應格式）。
    -   `settings.py`: API 模組預設配置。
-   `tests/`: 測試目錄，結構與`src`保持一致。
-   `docs/`: 多國語言文件。
-   `pyproject.toml`: 專案元資料、依賴項和工具配置。
-   `uv.lock`: 鎖定依賴版本。
-   `LICENSE`：Apache許可證2.0。

## 🧪 測試

項目使用`pytest`進行測試，並要求**100%**的測試覆蓋率。

### 運行測試

-   **運行 Tomorrow 測試**:
    ```bash
    PYTHONPATH=src TOMORROW_APP=tomorrow TOMORROW_SETTINGS_MODULE=tomorrow.settings uv run pytest tests/tomorrow
    ```

-   **運行 Rainy 測試**:
    ```bash
    PYTHONPATH=src RAINY_APP=rainy RAINY_SETTINGS_MODULE=rainy.settings uv run pytest tests/rainy
    ```

### 運行覆蓋率測試

要求測試覆蓋率必須達到**100%**。

```bash
PYTHONPATH=src \
TOMORROW_APP=tomorrow TOMORROW_SETTINGS_MODULE=tomorrow.settings \
RAINY_APP=rainy RAINY_SETTINGS_MODULE=rainy.settings \
uv run coverage run --rcfile=pyproject.toml -m pytest && uv run coverage report --rcfile=pyproject.toml
```

## 📄 許可證

本項目採用**阿帕契許可證 2.0**許可證。詳情請參閱[執照](LICENSE)文件。
