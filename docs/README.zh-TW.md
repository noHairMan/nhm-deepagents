# NHM-深度代理

[簡體中文](/docs/README.zh.md)\|[英語](/docs/README.en.md)\|[日本人](/docs/README.ja.md)\|[繁體中文](/docs/README.zh-TW.md)

一個使用現代 LLM 框架建構和運行「深度智能體」（Deep Agents）的 Python 專案。

## 🌟 專案概覽

`nhm-deepagents`是一個專注於深度智能體的專業 Python 專案。它利用現代 Python 特性 (3.14+) 和強大的工具，為 AI 智能體研究和應用提供高品質的開發體驗。

專案內部代號及應用前綴**`tomorrow`**取自遊戲《死亡擱淺 2：冥灘之上》（Death Stranding 2: On the Beach）中的角色**明天**（艾莉·範甯飾演）。在劇情中，她是主角山姆布里吉斯（Sam Bridges）的女兒，也被揭露為前作中的**大樓**(BB-28)。

該項目目前包含一個心理專家智能體，可以使用`deepagents`框架分析使用者輸入並提供建議。

## 🛠️ 技術棧

-   **語言**:[Python](https://www.python.org/)>= 3.14
-   **套件管理器**:[紫外線](https://github.com/astral-sh/uv)
-   **智能體框架**:[深度代理](https://github.com/zongxuheng/deepagents)(基於 LangGraph/LangChain)
-   **LLM 提供者**:[成為](https://ollama.com/)(透過`langchain-ollama`)
-   **配置管理**:[動態會議](https://www.dynaconf.com/)
-   **代碼品質**:`black`,`isort`,`pre-commit`

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

### 運行應用

運行主入口點：

```bash
uv run python src/main.py
```

## ⚙️ 配置

該項目使用**動態會議**進行配置管理。設定定義在`src/tomorrow/settings.py`中，可以透過環境變數或`.env`文件進行覆蓋。

### 環境變數

環境變數預設以前綴`TOMORROW_`開頭。

| 變數                         | 描述             | 預設值                      |
| -------------------------- | -------------- | ------------------------ |
| `TOMORROW_OLLAMA_BASE_URL` | Ollama 服務的基底地址 | `http://localhost:11434` |
| `TOMORROW_DEFAULT_MODEL`   | 預設使用的 LLM 模型   | `qwen3.5:9b`             |
| `TOMORROW_APP`             | 應用名稱（用作環境變數前綴） | `tomorrow`               |
| `TOMORROW_SETTINGS_MODULE` | 設定模組的路徑        | `tomorrow.settings`      |

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

-   `src/main.py`: 應用的主入口點。設定環境並調用智能體。
-   `src/tomorrow/`: 核心包目錄。
    -   `core/agent.py`: 定義深度智能體及其指令。
    -   `settings.py`: 預設配置值。
    -   `utils/conf.py`: Dynaconf 初始化邏輯。
    -   `utils/functional.py`: 功能實用程式（例如`SimpleLazyObject`）。
-   `docs/`: 多國語言文件。
-   `pyproject.toml`: 專案元資料、依賴項和工具配置。
-   `uv.lock`: 鎖定依賴版本。
-   `LICENSE`：Apache許可證2.0。

## 🧪 測試

-   TODO: 使用`pytest`實現單元測試和整合測試。
-   TODO: 新增用於自動測試的 CI 流程。

運行測試（實現後）：

```bash
uv run pytest
```

## 📄 許可證

本項目採用**阿帕契許可證 2.0**許可證。詳情請參閱[執照](LICENSE)文件。
