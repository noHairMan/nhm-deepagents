# NHM-深度代理

一個用於深度智能體（deep agents）的 Python 專案。

## 概覽

`nhm-deepagents`是一個專注於深度智能體的 Python 專案。它使用現代 Python 特性和工具，以提供穩健的開發體驗。

## 環境要求

-   **Python**: >= 3.14
-   **套件管理器**:[紫外線](https://github.com/astral-sh/uv)

## 安裝與設定

請依照以下步驟開始開發：

1.  **安裝`uv`**:
    如果您還沒有安裝`uv`，可以按照其[官方倉庫](https://github.com/astral-sh/uv)中的說明進行操作。

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

## 開發腳本

該項目使用`black`和`isort`進行格式化，並使用`pre-commit`進行品質檢查。

-   **格式化程式碼**:
    ```bash
    uv run black .
    uv run isort .
    ```

-   **手動運行 pre-commit 鉤子**:
    ```bash
    uv run pre-commit run --all-files
    ```

## 專案結構

-   `src/tomorrow/`: 核心包目錄。
-   `pyproject.toml`: 專案配置和依賴管理。
-   `.pre-commit-config.yaml`: pre-commit 鉤子配置。
-   `LICENSE`：Apache許可證2.0。

## 環境變數

-   TODO: 在此記錄任何所需的環境變數。

## 測試

-   TODO: 新增測試並記錄如何運行它們（例如`uv run pytest`）。

## 許可證

本項目採用**阿帕契許可證 2.0**許可證。有關詳情，請參閱[執照](../LICENSE)文件。
