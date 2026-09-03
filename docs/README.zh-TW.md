# NHM-深度代理

[![Build Status](https://github.com/noHairMan/nhm-deepagents/actions/workflows/build.yml/badge.svg)](https://github.com/noHairMan/nhm-deepagents/actions/workflows/build.yml)[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/noHairMan/nhm-deepagents/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/noHairMan/nhm-deepagents/blob/python-coverage-comment-action-data/htmlcov/index.html)[![Lint: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)[![Python Version](https://img.shields.io/badge/python-3.14-blue.svg)](https://www.python.org/downloads/release/python-3140/)[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)[![Repo Size](https://img.shields.io/github/repo-size/noHairMan/nhm-deepagents)](https://github.com/noHairMan/nhm-deepagents)[![Last Commit](https://img.shields.io/github/last-commit/noHairMan/nhm-deepagents)](https://github.com/noHairMan/nhm-deepagents)

[簡體中文](/docs/README.zh.md)\|[英語](/docs/README.en.md)\|[日本人](/docs/README.ja.md)\|[繁體中文](/docs/README.zh-TW.md)

![Fragile banner](/docs/images/fragile.png)

一個使用現代 LLM 框架建構和運行「深度智能體」（Deep Agents）的 Python 專案。

開發環境、專案結構、程式碼規格和測試方法請參閱[貢獻指南](CONTRIBUTING.zh.md)。

## 🌟 專案概覽

`nhm-deepagents`是一個專注於深度智能體的專業 Python 專案。它利用 Python 3.14 和強大的工具，為 AI 智能體研究和應用提供高品質的開發體驗。

專案內部包含三個主要模組：

-   **`tomorrow`**: 核心智能體模組。代號取自遊戲《死亡擱淺 2：冥灘之上》（Death Stranding 2: On the Beach）中的角色**明天**（艾莉·範甯飾演）。在劇情中，她是主角山姆布里吉斯（Sam Bridges）的女兒，也被揭露為前作中的**大樓**(BB-28)。
-   **`rainy`**: 基於 FastAPI 的 API 服務模組。代號同樣取自《死亡擱淺 2》中的角色**下雨天**（由忽那汐裡飾演）。在遊戲中，她擁有引發「時間雨」（Timefall）和具有治癒能力的「核心雨」（Corefall）的神奇力量，被描述為既能傷害也能治癒的「藥（Pharmakon）」。
-   **`fragile`**: 基於`asyncclick`的非同步命令列客戶端，用於直接向 Tomorrow 智能體提問或啟動互動式會話。其名稱取自同一作品中的角色**脆弱的**。 Fragile 是 Fragile Express 的創辦人和快遞員，因接觸時間雨而快速衰老，卻始終在危險環境中為他人運送重要物資；這種「脆弱」外表下仍堅持承擔連接與傳遞使命的形象，正是該客戶端名稱的背景。

該專案提供了一個通用的智慧助理智能體，利用`deepagents`框架分析使用者輸入，並透過`rainy`模組對外提供同步（`/api/chat`）及**流式（`/api/chat/stream`）**API 介面。

### 核心功能

-   **深度智能體**: 集成`deepagents`框架，支援複雜任務處理與狀態管理。
-   **技能模組**: 支持透過`TOMORROW_SKILLS`配置技能目錄，為智能體載入可擴充的領域能力。
-   **子代理**: 支持透過`TOMORROW_SUBAGENTS`配置專用子代理程式及其模型、技能和系統提示詞。
-   **遞迴控制**: 支持透過`TOMORROW_RECURSION_LIMIT`限制智能體遞歸調用深度。
-   **生命週期管理**: 引入`AgentManager`統一管理智能體實例的創建與銷毀，確保資源的優雅初始化。
-   **高效能 API**: 基於 FastAPI 構建，支援同步回應與 Server-Sent Events (SSE) 串流輸出。
-   **互動式 CLI**:`fragile`支援`/new`建立新會話、`/history`瀏覽並切換已持久化的歷史會話、`/account`配置外部模型帳戶、`/model`選擇模型、`/quit`退出、會話恢復、輸入歷史記錄、斜線命令補全和多行編輯，並以追加式時間軸顯示模型摘要、工具呼叫、命令結果和最終答案。
-   **帳戶配置持久化**: 支援透過互動式指令保存 Anthropic 和 OpenAI 的 API 憑證，並在後續會話中自動復原。
-   **可靠性保障**: 強制類型提示、Ruff 靜態檢查、100% 測試覆蓋率要求。

## 🛠️ 技術棧

-   **語言**:[Python](https://www.python.org/)>= 3.14, &lt; 3.15
-   **套件管理器**:[紫外線](https://github.com/astral-sh/uv)
-   **API 框架**:[迅速](https://fastapi.tiangolo.com/)
-   **Web 伺服器**:[獨角獸](https://www.uvicorn.org/)
-   **智能体框架**:[深度代理](https://github.com/zongxuheng/deepagents)(基於 LangGraph/LangChain)
-   **LLM 提供者**:[人擇](https://www.anthropic.com/)和[開放人工智慧](https://openai.com/)
-   **終端交互**:[非同步點擊](https://github.com/python-trio/asyncclick)提供非同步 CLI 命令、參數解析和幫助資訊；[提示工具包](https://github.com/prompt-toolkit/python-prompt-toolkit)提供非同步輸入、輸入歷史記錄、命令補全和多行編輯；[富有的](https://github.com/Textualize/rich)提供終端輸出樣式。
-   **配置管理**:[金字塔設置](https://docs.pydantic.dev/latest/usage/settings/)
-   **例外處理**: 自訂異常體系 (`TomorrowError`及其子類)，涵蓋模型、後端、儲存和檢查點錯誤。
-   **代碼品質**:[魯夫](https://github.com/astral-sh/ruff)(替代 Black 和 Isort)、`pre-commit`、強制型別提示 (Strict Type Hinting)
-   **測試與覆蓋率**:`pytest`,`coverage`

## 📋 環境要求

-   **Python 3.14（不支援 3.15 及更高版本）**
-   **紫外線**: 一個快速的 Python 套件安裝和解析器。
-   **LLM 提供者**: 支援 Anthropic 和 OpenAI 相容接口，需要透過環境變數或`.env`配置 API Key。
-   **LLM 模型**: 預設使用 Anthropic 的`claude-sonnet-5`，也可以透過`TOMORROW_MODEL__TYPE`切換到 O​​penAI。

## 🚀 快速入門

### 安裝

1.  **安裝`uv`**:
    請按照[uv 官方倉庫](https://github.com/astral-sh/uv)中的說明進行操作。

2.  **克隆倉庫**:
    ```bash
    git clone https://github.com/noHairMan/nhm-deepagents.git
    cd nhm-deepagents
    ```

3.  **同步依賴並建立虛擬環境**:
    ```bash
    uv sync
    ```

4.  **安裝`fragile`命令**:

    ```bash
    uv tool install .
    ```

    安裝完成後，可直接使用`fragile`命令啟動命令列客戶端。

### 運行應用

運行主入口點：

```bash
uv run python src/main.py
```

此指令啟動 Rainy API，預設監聽`http://localhost:8000`。也可以使用 Uvicorn 直接啟動：

```bash
uv run uvicorn main:app --app-dir src --host localhost --port 8000
```

使用`langgraph-cli`啟動智能體 API 服務：

```bash
uv run langgraph dev
```

CLI 會讀取根目錄的`langgraph.json`，並暴露名為`tomorrow`的 graph。

Rainy API 的請求體包含必填的`message`字段和可選的會話`thread_id`。同步介面返回智能體的最終回覆：

```bash
curl -X POST http://localhost:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"你好"}'
```

需要逐步接收回應時，可調用`/api/chat/stream`取得 SSE 資料流；`/api/chat/stream/event`會傳回更完整的 LangGraph 事件流。健康檢查介面為`GET /api/health`。

使用`fragile`命令列客戶端啟動互動式會話：

```bash
fragile
```

如果尚未使用`uv tool install .`安裝命令，也可以在專案環境中執行：

```bash
uv run fragile
```

透過`--thread`或`-t`傳入 UUID 可以恢復已有會話；不傳入時會自動建立新的執行緒。互動過程中輸入`/new`可清屏並開始新會話，輸入`/history`可查看已儲存的會話並按編號或 UUID 切換，輸入`/quit`退出；也可以連續兩次按`Ctrl+C`在短時間內退出會話，按`Esc`後回車可插入換行。

#### Fragile 輸出時間軸

每次普通對話都會依執行順序追加顯示以下區塊：

-   `Thinking (provider summary)`：僅顯示模型提供者明確回傳的 thinking/reasoning 摘要，不推斷或產生私有思維鏈。
-   `Tool`：顯示工具名稱、脫敏後的參數和運作狀態；`execute`也會突出顯示實際命令。
-   `Completed`/`Failed`：顯示工具結果或失敗訊息；過長內容會在終端機中標記截斷。
-   `Assistant`：最終答案仍依模型傳回的片段連續流式輸出。

工具、命令、階段和模型摘要會與答案一起保存，使用`/history`切換會話時按原始順序回放。時間軸採用與全螢幕輸入相容的追加式輸出，不使用動態分割畫面面板；參數、結果和錯誤中的 API Key、Authorization、密碼及 URL 憑證會先脫敏後顯示並儲存。

首次使用其他模型提供者時，可在互動會話中輸入`/account`，按提示選擇提供者並填寫 Base URL 和 API Key。模型名稱等其他配置仍透過`TOMORROW_MODEL`或對應的環境變數設定。憑證會持久化到本機資料庫，後續啟動`fragile`時自動恢復；如需修改配置，再次執行`/account`即可。

`fragile`的 CLI 入口和`purge`子命令均使用非同步命令函數，避免在已運行的事件循環中嵌套調用`asyncio.run()`。清理已持久化的會話記錄：

```bash
fragile purge
```

## ⚙️ 配置

該項目使用**金字塔設置**進行配置管理。設定分別定義在`src/tomorrow/settings.py`（明天），`src/rainy/settings.py`(Rainy) 和`src/fragile/settings.py`(Fragile) 中，可以透過環境變數或`.env`文件進行覆蓋。環境變數優先權最高，三個模組分別使用`TOMORROW_`、`RAINY_`和`FRAGILE_`前綴；也可以透過`TOMORROW_ENV_FILE`、`RAINY_ENV_FILE`或`FRAGILE_ENV_FILE`指定設定檔路徑。

### 環境變數

環境變數預設以前綴`TOMORROW_`(核心模組)、`RAINY_`(API 模組) 或`FRAGILE_`(CLI 模組) 開頭。

#### Tomorrow 配置 (核心)

| 變數                                                  | 描述                                              | 預設值                           |
| --------------------------------------------------- | ----------------------------------------------- | ----------------------------- |
| `TOMORROW_APP`                                      | 應用名稱（用作環境變數前綴）                                  | `tomorrow`                    |
| `TOMORROW_MODEL`                                    | 模型配置，支持`ANTHROPIC`和`OPENAI`                     | `anthropic`/`claude-sonnet-5` |
| `TOMORROW_CHECKPOINT`                               | 檢查點配置，支援 MEMORY 和 SQLITE                        | `{"type":"memory"}`           |
| `TOMORROW_BACKEND`                                  | 後端配置，支援 FILESYSTEM 和 LOCAL_SHELL                | `{"type":"filesystem"}`       |
| `TOMORROW_STORE`                                    | 儲存配置，支援 MEMORY 和 SQLITE                         | `{"type":"sqlite"}`           |
| `TOMORROW_SKILLS`                                   | 技能目錄列表                                          | `[]`                          |
| `TOMORROW_SUBAGENTS`                                | 子代理配置列表                                         | `[]`                          |
| `TOMORROW_RECURSION_LIMIT`                          | 智能體遞歸調用上限                                       | `100`                         |
| `TOMORROW_MODEL__ANTHROPIC__THINKING_ENABLED`       | 是否請求 Anthropic thinking 輸出                      | `false`                       |
| `TOMORROW_MODEL__ANTHROPIC__THINKING_BUDGET_TOKENS` | Anthropic thinking 的 token 預算（啟用時必填）            | 未設定                           |
| `TOMORROW_MODEL__OPENAI__REASONING_EFFORT`          | OpenAI reasoning 強度：`low`、`medium`或`high`       | 未設定                           |
| `TOMORROW_MODEL__OPENAI__REASONING_SUMMARY`         | OpenAI reasoning 摘要：`auto`、`concise`或`detailed` | 未設定                           |

模型配置透過`TOMORROW_MODEL`或嵌套環境變數傳入。預設使用 Anthropic 的`claude-sonnet-5`，也可以設定 Anthropic 相容介面。例如：

```bash
export TOMORROW_MODEL__TYPE="anthropic"
export TOMORROW_MODEL__ANTHROPIC__BASE_URL="https://api.anthropic.com"
export TOMORROW_MODEL__ANTHROPIC__MODEL="claude-sonnet-5"
export TOMORROW_MODEL__ANTHROPIC__API_KEY="your-api-key"
```

選擇 OpenAI 或相容 OpenAI API 的服務時，可以使用以下巢狀環境變數來配置模型名稱、API Key、可選的 Base URL 和溫度：

```bash
export TOMORROW_MODEL__TYPE="openai"
export TOMORROW_MODEL__OPENAI__MODEL="gpt-4o-mini"
export TOMORROW_MODEL__OPENAI__API_KEY="your-api-key"
export TOMORROW_MODEL__OPENAI__BASE_URL="https://api.openai.com/v1"
export TOMORROW_MODEL__OPENAI__TEMPERATURE="0"
```

thinking/reasoning 預設為關閉。需要在`fragile`CLI 中查看模型明確傳回的 thinking 或 reasoning 摘要時，按提供者配置對應參數；此功能可能會增加 token 消耗和回應延遲。例如：

```bash
export TOMORROW_MODEL__ANTHROPIC__THINKING_ENABLED="true"
export TOMORROW_MODEL__ANTHROPIC__THINKING_BUDGET_TOKENS="2048"

export TOMORROW_MODEL__OPENAI__REASONING_EFFORT="medium"
export TOMORROW_MODEL__OPENAI__REASONING_SUMMARY="auto"
```

Fragile 只展示提供者傳回的 thinking/reasoning 內容，不會產生或推斷模型未回傳的內部思考；Rainy API 的現有回應協定不受影響。未配置或模型不支援對應能力時，仍只顯示最終答案。 thinking/reasoning 可能會增加 token 消耗和回應延遲，具體內容取決於模型提供者。

具體欄位和預設值請參閱`src/tomorrow/settings.py`。

子代理配置透過`TOMORROW_SUBAGENTS`傳入，每個子代理至少需要`name`、`description`和`system_prompt`字段，也可以指定`model`與`skills`，例如：

```bash
export TOMORROW_SUBAGENTS='[{"name":"researcher","description":"负责资料检索","system_prompt":"你是一名研究助手。","skills":["skills/research/"]}]'
```

#### Rainy 設定 (API)

| 變數                                    | 描述             | 預設值                              |
| ------------------------------------- | -------------- | -------------------------------- |
| `RAINY_HOST`                          | API 服務監聽位址     | `localhost`                      |
| `RAINY_PORT`                          | API 服務連接埠      | `8000`                           |
| `RAINY_APP`                           | 應用名稱（用作環境變數前綴） | `rainy`                          |
| `RAINY_MIDDLEWARE`                    | 啟用的中間件列表       | 統一回應格式、處理時間                      |
| `RAINY_UNIFY_RESPONSE_FORMAT_EXCLUDE` | 不進行統一回應包裝的路徑   | `/docs`、`/redoc`、`/openapi.json` |
| `RAINY_LOG_LEVEL`                     | 日誌等級           | `INFO`                           |

#### Fragile 設定 (CLI)

| 變數                                 | 描述                     | 預設值                                      |
| ---------------------------------- | ---------------------- | ---------------------------------------- |
| `FRAGILE_APP`                      | 應用名稱（用作環境變數前綴）         | `fragile`                                |
| `FRAGILE_INTERRUPT_EXIT_THRESHOLD` | 兩次`Ctrl+C`觸發退出的最大間隔（秒） | `0.5`                                    |
| `FRAGILE_ENABLED_COMMANDS`         | 啟用的互動式命令類別路徑列表         | `quit`、`new`、`history`、`account`、`model` |

Fragile 的其他互動行為透過命令列選項和內建斜線命令控制。命令透過註冊表統一發現和處理，可使用`FRAGILE_ENABLED_COMMANDS`調整啟用的命令。帳戶憑證由`Account`模型以單例形式保存於 Fragile 的資料庫中，啟動交互會話時會恢復到 Tomorrow 的模型配置；環境變數仍可作為配置來源並擁有更高優先權。

## 📄 許可證

本項目採用**阿帕契許可證 2.0**許可證。詳情請參閱[執照](/LICENSE)文件。
