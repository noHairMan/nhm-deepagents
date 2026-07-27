# NHM-深度代理

[![Build Status](https://github.com/noHairMan/nhm-deepagents/actions/workflows/build.yml/badge.svg)](https://github.com/noHairMan/nhm-deepagents/actions/workflows/build.yml)[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/noHairMan/nhm-deepagents/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/noHairMan/nhm-deepagents/blob/python-coverage-comment-action-data/htmlcov/index.html)[![Lint: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)[![Python Version](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/release/python-3140/)[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)[![Repo Size](https://img.shields.io/github/repo-size/noHairMan/nhm-deepagents)](https://github.com/noHairMan/nhm-deepagents)[![Last Commit](https://img.shields.io/github/last-commit/noHairMan/nhm-deepagents)](https://github.com/noHairMan/nhm-deepagents)

[簡體中文](/docs/README.zh.md)\|[英語](/docs/README.en.md)\|[日本人](/docs/README.ja.md)\|[繁體中文](/docs/README.zh-TW.md)

一個使用現代 LLM 框架建構和運行 Deep Agents 的 Python 專案。

## 🌟 專案概況

`nhm-deepagents`是一個專注於深度代理的專業Python專案。它利用現代Python功能（3.14+）和強大的工具，為AI代理研究和應用提供高品質的開發體驗。

此項目包含三個主要模組：

-   **`tomorrow`**：核心代理模組。代號取自遊戲《死亡擱淺2：海灘》中的角色**明天**（艾莉·範甯飾演）。在劇情中，她是主角山姆·布里奇斯的女兒，而山姆·布里奇斯也被揭露為前作中的角色。**大樓**(BB-28)。
-   **`rainy`**：基於FastAPI的API服務模組。代號也取自《死亡擱淺 2》中的一個角色**下雨天**（久奈詩織飾演）。在遊戲中，她擁有引發「Timefall」和治療「Corefall」的神奇力量，被描述為既能傷害又能治癒的「Pharmakon」。
-   **`fragile`**：基於 Typer 的命令列用戶端，用於直接向 Tomorrow 代理提問或啟動互動式會話。它的名字取自同一作品中的一個角色**脆弱的**。 Fragile是Fragile Express的創辦人和快遞員。他因暴露在時間的雨露中而迅速衰老，但他始終在危險的環境中為他人運送重要的物資。這種看似「脆弱」的外表，卻依然堅持連結和傳遞使命的形象，就是這個客戶名字的背景。

該專案提供了一個通用的智慧助理代理，它利用`deepagents`此框架分析使用者輸入並傳遞`rainy`此模組提供外部同步（`/api/chat`）和**串流（`/api/chat/stream`）**API介面。

### 核心功能

-   **深層代理**： 融合的`deepagents`支援複雜任務處理和狀態管理的框架。
-   **技能模組**: 支持透過`TOMORROW_SKILLS`配置技能目錄以載入代理程式的可擴充網域功能。
-   **子代理**: 支持透過`TOMORROW_SUBAGENTS`配置專用子代理程式及其模型、技能和系統提示。
-   **程式碼解釋器**：整合QuickJS中間件，為代理提供程式碼執行能力。
-   **遞迴控制**: 支持透過`TOMORROW_RECURSION_LIMIT`限制代理遞歸呼叫的深度。
-   **生命週期管理**： 介紹`AgentManager`統一管理代理實例的建立和銷毀，確保資源的正常初始化。
-   **高性能API**：基於FastAPI構建，支援同步回應和伺服器發送事件（SSE）流輸出。
-   **互動式CLI**:`fragile`支援`/new`建立新會話，`/history`在持久的歷史會話之間瀏覽和切換，`/quit`退出、會話恢復、輸入歷史記錄、斜杠命令完成和多行編輯。
-   **可靠性有保證**：強制類型提示、Ruff 靜態檢查、100% 測試覆蓋率要求。

## ⚙️ CI/CD

該專案整合了 GitHub Actions 工作流程，包括：

-   **測試和覆蓋範圍**：自動執行測試並檢查程式碼覆蓋率。
-   **文件翻譯**： 自動地`README.zh.md`翻譯成多種語言（英文、日文、繁體中文）。
-   **程式碼規範**：自動執行`ruff`檢查並格式化以確保一致的程式碼風格和高品質。
-   **CI流程優化**：增強工作流程觸發路徑規則，僅在相關程式碼或配置發生變化時觸發構建，提高效率。

## 🛠️技術棧

-   **語言**:[Python](https://www.python.org/)>= 3.14
-   **套件管理器**:[紫外線](https://github.com/astral-sh/uv)
-   **API框架**:[迅速](https://fastapi.tiangolo.com/)
-   **網路伺服器**:[獨角獸](https://www.uvicorn.org/)
-   **代理框架**:[深度代理](https://github.com/zongxuheng/deepagents)（基於LangGraph/LangChain）
-   **法學碩士提供者**:[成為](https://ollama.com/)、[抱臉](https://huggingface.co/)和[人擇](https://www.anthropic.com/)
-   **程式碼執行**:[langchain-quickjs](https://github.com/langchain-ai/langchainjs)提供QuickJS中介軟體
-   **終端交互**:[提示工具包](https://github.com/prompt-toolkit/python-prompt-toolkit)提供輸入歷史記錄、命令完成和多行編輯，[富有的](https://github.com/Textualize/rich)提供終端輸出樣式。
-   **配置管理**:[懸垂設定](https://docs.pydantic.dev/latest/usage/settings/)
-   **例外處理**：自訂異常系統（`TomorrowError`及其子類別），涵蓋模型、後端、儲存和檢查點錯誤。
-   **代碼品質**:[拉夫](https://github.com/astral-sh/ruff)（取代 Black 和 Isort），`pre-commit`, 嚴格類型提示
-   **測試和覆蓋範圍**:`pytest`,`coverage`

## 📋環境要求

-   **Python 3.14+**
-   **紫外線**：快速的 Python 套件安裝程式和解析器。
-   **法學碩士提供者**： 當前的`.env`使用 Anthropic 相容介面，無需運行 Ollama。
-   **法學碩士模式**：目前配置使用`deepseek-v4-flash`;你也可以透過`TOMORROW_MODEL`切換到 O​​llama 或 HuggingFace。

## 🚀 快速入門

### 安裝

1.  **安裝`uv`**：
    請關注[uv官方倉庫](https://github.com/astral-sh/uv)請按照 中的說明進行操作。

2.  **克隆倉庫**:
    ```bash
    git clone <repository-url>
    cd nhm-deepagents
    ```

3.  **同步依賴並建立虛擬環境**:
    ```bash
    uv sync
    ```

4.  **安裝預提交鉤子**:
    ```bash
    uv run pre-commit install
    ```

5.  **配置法學碩士**:
    ```bash
    export TOMORROW_MODEL__TYPE="anthropic"
    export TOMORROW_MODEL__ANTHROPIC__BASE_URL="https://www.llmgateway.cn"
    export TOMORROW_MODEL__ANTHROPIC__MODEL="deepseek-v4-flash"
    export TOMORROW_MODEL__ANTHROPIC__API_KEY="your-api-key"
    ```

### 運行應用程式

運行主入口點：

```bash
uv run python src/main.py
```

使用`langgraph-cli`啟動代理API服務：

```bash
uv run langgraph dev
```

CLI 將讀取根目錄`langgraph.json`，並公開名字`tomorrow`圖形。

使用`fragile`命令列客戶端啟動互動式會話：

```bash
uv run fragile
```

經過`--thread`或者`-t`傳入UUID可以恢復一個已有的會話；如果不傳入，會自動建立一個新執行緒。互動時輸入`/new`若要清除螢幕並開始新會話，請輸入`/history`若要查看已儲存的會話並按號碼或 UUID 切換，請輸入`/quit`出口;您也可以連續按兩次`Ctrl+C`若要在短時間內退出會話，請按`Esc`按 Enter 鍵插入換行符號。

## ⚙️配置

該項目使用**懸垂設定**執行配置管理。設定分別定義在`src/tomorrow/settings.py`（明天），`src/rainy/settings.py`（下雨）和`src/fragile/settings.py`（脆弱），您可以使用環境變數或`.env`文件被覆蓋。環境變數的優先權最高，分別由三個模組使用。`TOMORROW_`、`RAINY_`和`FRAGILE_`前綴；也可以透過`TOMORROW_ENV_FILE`、`RAINY_ENV_FILE`或者`FRAGILE_ENV_FILE`指定設定檔路徑。

### 環境變數

環境變數預設帶有前綴`TOMORROW_`（核心模組），`RAINY_`（API 模組）或`FRAGILE_`（CLI 模組）開始。

#### 明天配置（核心）

| 多變的                        | 描述                                  | 預設值                                        |
| -------------------------- | ----------------------------------- | ------------------------------------------ |
| `TOMORROW_APP`             | 應用程式名稱（用作環境變數前綴）                    | `tomorrow`                                 |
| `TOMORROW_MODEL`           | 模型配置，支援OLLAMA、HUGGINGFACE和ANTHROPIC | 目前的`.env`使用`anthropic`/`deepseek-v4-flash` |
| `TOMORROW_CHECKPOINT`      | 檢查點配置，支援MEMORY和SQLITE               | `{"type":"memory"}`                        |
| `TOMORROW_BACKEND`         | 後端配置，支援FILESYSTEM和LOCAL_SHELL       | `{"type":"filesystem"}`                    |
| `TOMORROW_STORE`           | 儲存配置，支援MEMORY和SQLITE                | `{"type":"sqlite"}`                        |
| `TOMORROW_SKILLS`          | 技能目錄列表                              | `["skills/"]`                              |
| `TOMORROW_SUBAGENTS`       | 子代理配置列表                             | `[]`                                       |
| `TOMORROW_RECURSION_LIMIT` | 代理遞歸呼叫上限                            | `100`                                      |

型號配置透過`TOMORROW_MODEL`或傳入嵌套的環境變數。目前的`.env`使用 Anthropic 相容介面和`deepseek-v4-flash`;使用其他提供者時，請進行對應配置`ollama`或者`huggingface`目的。例如：

```bash
export TOMORROW_MODEL__TYPE="anthropic"
export TOMORROW_MODEL__ANTHROPIC__BASE_URL="https://www.llmgateway.cn"
export TOMORROW_MODEL__ANTHROPIC__MODEL="deepseek-v4-flash"
export TOMORROW_MODEL__ANTHROPIC__API_KEY="your-api-key"
```

具體欄位和預設值請參考`src/tomorrow/settings.py`。

子代理配置已通過`TOMORROW_SUBAGENTS`傳入後，每個子代理至少需要`name`、`description`和`system_prompt`字段，您也可以指定`model`和`skills`，例如：

```bash
export TOMORROW_SUBAGENTS='[{"name":"researcher","description":"负责资料检索","system_prompt":"你是一名研究助手。","skills":["skills/research/"]}]'
```

#### 雨天配置（API）

| 多變的                | 描述               | 預設值         |
| ------------------ | ---------------- | ----------- |
| `RAINY_HOST`       | API服務監聽位址        | `localhost` |
| `RAINY_PORT`       | API服務埠           | `8000`      |
| `RAINY_APP`        | 應用程式名稱（用作環境變數前綴） | `rainy`     |
| `RAINY_MIDDLEWARE` | 啟用的中間件列表         | （請參閱設定.py）  |

#### 脆弱配置 (CLI)

| 多變的                                | 描述                       | 預設值                    |
| ---------------------------------- | ------------------------ | ---------------------- |
| `FRAGILE_APP`                      | 應用程式名稱（用作環境變數前綴）         | `fragile`              |
| `FRAGILE_INTERRUPT_EXIT_THRESHOLD` | 兩次`Ctrl+C`觸發退出之間的最大間隔（秒） | `0.5`                  |
| `FRAGILE_ENABLED_COMMANDS`         | 啟用互動式命令類路徑列表             | `quit`、`new`、`history` |

Fragile 的其他互動行為是透過命令列選項和內建斜杠命令控制的。命令透過註冊表統一發現和處理，使用`FRAGILE_ENABLED_COMMANDS`調整啟用的命令。

## 📜 劇本

常用的開發腳本：

-   **檢查並格式化程式碼**:
    ```bash
    uv run ruff check . --fix
    uv run ruff format .
    ```

-   **手動運行預提交掛鉤**:
    ```bash
    uv run pre-commit run --all-files
    ```

## 📂 專案結構

-   `src/main.py`：Rainy API 服務的主要入口點。設定環境並啟動 Uvicorn 伺服器。
-   `src/fragile/`：命令列客戶端包目錄。
    -   `cli.py`： 定義`fragile`命令列輸入。
    -   `commands/interactive/`：互動式會話實現，支援會話復原、新會話、命令補全和多行輸入。
        -   `agent.py`：管理與明天代理的交互。
        -   `commands/`：互動式斜槓命令實作和命令註冊表。
            -   `base.py`：定義交互命令的基本介面和處理結果。
            -   `history.py`：查詢並選擇持久化的歷史會話。
            -   `new.py`：建立一個新會話。
            -   `quit.py`：退出互動會話。
        -   `display.py`：管理終端顯示。
        -   `input.py`：管理輸入歷史記錄、命令完成和多行編輯。
        -   `session.py`：管理互動式會話的流程。
    -   `conf/config.py`：提供延遲載入的 CLI 全域配置。
    -   `models/session.py`：定義互動式會話狀態模型。
    -   `models/constants/command.py`：定義指令處理結果常數。
    -   `settings.py`：CLI 模組預設配置。
-   `src/tomorrow/`：核心代理程式包目錄。
    -   `graph.py`:`langgraph-cli`要使用的圖形條目。
    -   `core/agent.py`：定義深度代理及其指令，提供`AgentManager`執行生命週期管理。
    -   `core/backend/`：統一後端載入邏輯，支持`FILESYSTEM`和`LOCAL_SHELL`。
    -   `core/checkpoint/`：檢查點實施、支持`MEMORY`和`SQLITE`。
    -   `core/model/`：模型載入實現，支持`OLLAMA`、`HUGGINGFACE`和`ANTHROPIC`。
    -   `core/store/`：儲存實作、支援`MEMORY`和`SQLITE`。
    -   `exceptions.py`：定義特定於應用程式的異常類別系統。
    -   `models/constants/`：定義各種類型的常數（Backend、Checkpoint、Model、Store）。
    -   `settings.py`：預設配置值。
    -   `utils/functional.py`：功能實用程式。
-   `src/rainy/`：API服務包目錄。
    -   `app.py`：FastAPI應用程式定義，整合生命週期管理和路由。
    -   `lifespan.py`：處理應用程式的啟動和關閉邏輯，管理代理實例的生命週期。
    -   `api/endpoints/`：API路由定義。
        -   `chat.py`：同步串流聊天介面，整合深度代理模組（回應由中間件統一封裝）。
            -   `POST /api/chat`：同步聊天回覆。
            -   `POST /api/chat/stream`：SSE 串流響應。
            -   `POST /api/chat/stream/event`：事件流響應。
        -   `health.py`：健康檢查介面（`GET /api/health`)。
        -   `urls.py`：統一路由掛載。
    -   `middleware/`：自訂中間件（處理時間，統一回應格式）。
    -   `settings.py`：API模組預設配置。
-   `tests/`：測試目錄、結構及`src`保持一致。
-   `docs/`：多語言文檔。
-   `pyproject.toml`：項目元資料、依賴項和工具配置。
-   `langgraph.json`:`langgraph-cli`圖和環境配置。
-   `uv.lock`：鎖定依賴版本。
-   `LICENSE`：Apache許可證2.0。

## 🧪 測試

項目使用`pytest`進行測試並詢問**100%**測試覆蓋率。

### 運行測試

-   **運行明天測試**:
    ```bash
    PYTHONPATH=src TOMORROW_APP=tomorrow uv run pytest tests/tomorrow
    ```

-   **運行雨天測試**:
    ```bash
    PYTHONPATH=src RAINY_APP=rainy uv run pytest tests/rainy
    ```

-   **運行脆弱測試**:
    ```bash
    PYTHONPATH=src FRAGILE_APP=fragile uv run pytest tests/fragile
    ```

### 運行覆蓋率測試

要求測試覆蓋率必須達到**100%**。

```bash
PYTHONPATH=src \
TOMORROW_APP=tomorrow \
RAINY_APP=rainy \
FRAGILE_APP=fragile \
uv run coverage run --rcfile=pyproject.toml -m pytest && uv run coverage report --rcfile=pyproject.toml
```

## 📄 許可證

該項目使用**阿帕契許可證 2.0**執照。詳情請參閱[執照](LICENSE)文件.
