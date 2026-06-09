# nhm-deepagents

[![Lint: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/noHairMan/nhm-deepagents/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/noHairMan/nhm-deepagents/blob/python-coverage-comment-action-data/htmlcov/index.html)

[簡体字中国語](/docs/README.zh.md)\|[英語](/docs/README.en.md)\|[日本語](/docs/README.ja.md)\|[繁体中文](/docs/README.zh-TW.md)

最新の LLM フレームワークを使用して Deep Agent を構築および実行する Python プロジェクト。

## 🌟プロジェクト概要

`nhm-deepagents`は、ディープ エージェントに焦点を当てたプロフェッショナルな Python プロジェクトです。最新の Python 機能 (3.14 以降) と強力なツールを活用して、AI エージェントの研究とアプリケーションに高品質の開発エクスペリエンスを提供します。

プロジェクトには 2 つの主要なモジュールが含まれています。

-   **`tomorrow`**: コアエージェントモジュール。コードネームはゲーム『デス・ストランディング2: オン・ザ・ビーチ』の登場人物から取られている。**明日**（エル・ファニングが演じる）。プロットでは、彼女は主人公サム・ブリッジスの娘であり、前作のキャラクターでもあることが明らかになりました。**ルー**(BB-28)。
-   **`rainy`**: FastAPIをベースとしたAPIサービスモジュール。コードネームもデス・ストランディング2のキャラクターから取られています**雨が降る**（忽那汐里が演じる）。ゲーム内では「タイムフォール」と回復の「コアフォール」を引き起こす魔法の力を持ち、傷つけることも治すこともできる「ファルマコン」として描かれている。応答フォーマットの統一や処理時間のミドルウェアなどの機能を統合したモジュールです。

プロジェクトには現在、使用できる一般的なスマート アシスタント エージェントが含まれています`deepagents`このフレームワークはユーザー入力を分析し、次の方法で提案を提供します。`rainy`このモジュールは外部同期を提供します (`/api/chat`) およびストリーミング (`/api/chat/stream`) API インターフェース。

## ⚙️CI/CD

このプロジェクトには、以下を含む GitHub Actions ワークフローが統合されています。

-   **テストと適用範囲**: テストを自動的に実行し、コード カバレッジをチェックします。
-   **文書翻訳**： 自動的に`README.zh.md`多言語（英語、日本語、繁体字中国語）に翻訳されます。
-   **コード仕様**：自動実行`ruff`確認してフォーマットしてください。

## 🛠️ テクノロジースタック

-   **言語**:[パイソン](https://www.python.org/)>= 3.14
-   **包管理器**:[紫外線](https://github.com/astral-sh/uv)
-   **APIフレームワーク**:[速い](https://fastapi.tiangolo.com/)
-   **ウェブサーバー**:[ユビコーン](https://www.uvicorn.org/)
-   **エージェントフレームワーク**:[ディープエージェント](https://github.com/zongxuheng/deepagents)(LangGraph/LangChainに基づく)
-   **LLMプロバイダー**:[であること](https://ollama.com/)（合格`langchain-ollama`)
-   **配置管理**:[ダイナコンフ](https://www.dynaconf.com/)
-   **コードの品質**:`ruff`,`pre-commit`、タイプヒント
-   **テストと適用範囲**:`pytest`,`coverage`

## 📋 環境要件

-   **Python 3.14+**
-   **紫外線**: 高速な Python パッケージ インストーラーおよびパーサー。
-   **であること**: 実行中でアクセス可能である必要があります。
-   **LLMモデル**: デフォルトで使用されるモデルは`qwen3.5:9b`。次のコマンドを使用して取得できます。
    ```bash
    ollama pull qwen3.5:9b
    ```

## 🚀 クイックスタート

### インストール

1.  **インストール`uv`**:
    フォローしてください[UV公式倉庫](https://github.com/astral-sh/uv)の指示に従ってください。

2.  **リポジトリのクローンを作成する**:
    ```bash
    git clone <repository-url>
    cd nhm-deepagents
    ```

3.  **依存関係を同期し、仮想環境を作成する**:
    ```bash
    uv sync
    ```

4.  **プリコミットフックをインストールする**:
    ```bash
    uv run pre-commit install
    ```

5.  **Ollama を起動してモデルを取得します**:
    ```bash
    ollama pull qwen3.5:9b
    ```

### アプリケーションを実行する

メイン エントリ ポイントを実行します。

```bash
uv run python src/main.py
```

## ⚙️ 配置

このプロジェクトでは、**ダイナコンフ**構成管理を実行します。設定はそれぞれ次のように定義されています。`src/tomorrow/settings.py`(明日)和`src/rainy/settings.py`(雨)、環境変数を使用することも、`.env`ファイルが上書きされます。

### 環境変数

環境変数にはデフォルトで接頭辞が付けられます`TOMORROW_`(コアモジュール) または`RAINY_`(API モジュール) が最初にあります。

#### Tomorrow 配置 (核心)

| 変数                         | 説明する                      | デフォルト値                   |
| -------------------------- | ------------------------- | ------------------------ |
| `TOMORROW_OLLAMA_BASE_URL` | Ollama サービスのベース アドレス      | `http://localhost:11434` |
| `TOMORROW_DEFAULT_MODEL`   | デフォルトで使用される LLM モデル       | `qwen3.5:9b`             |
| `TOMORROW_APP`             | アプリケーション名 (環境変数の接頭辞として使用) | `tomorrow`               |
| `TOMORROW_SETTINGS_MODULE` | モジュールパスを設定する              | `tomorrow.settings`      |
| `TOMORROW_CHECKPOINT`      | チェックポイントの構成               | `{"type": "memory"}`     |

#### Rainy 配置 (API)

| 変数                      | 説明する                      | デフォルト値           |
| ----------------------- | ------------------------- | ---------------- |
| `RAINY_HOST`            | APIサービスリスニングアドレス          | `localhost`      |
| `RAINY_PORT`            | APIサービスポート                | `8000`           |
| `RAINY_APP`             | アプリケーション名 (環境変数の接頭辞として使用) | `rainy`          |
| `RAINY_SETTINGS_MODULE` | モジュールパスを設定する              | `rainy.settings` |
| `RAINY_MIDDLEWARE`      | 有効なミドルウェアのリスト             | (settings.pyを参照) |

## 📜 脚本

一般的に使用される開発スクリプト:

-   **コードをチェックしてフォーマットする**:
    ```bash
    uv run ruff check . --fix
    uv run ruff format .
    ```

-   **コミット前フックを手動で実行する**:
    ```bash
    uv run pre-commit run --all-files
    ```

## 📂 プロジェクトの構造

-   `src/main.py`: アプリケーションのメイン エントリ ポイント。環境をセットアップし、Uvicorn サーバーを起動します。
-   `src/tomorrow/`: コア エージェント パッケージ ディレクトリ。
    -   `core/agent.py`: ディープエージェントとその命令を定義します。
    -   `core/checkpoints/`: チェックポイントの実装 (メモリ、SQLite など)。
    -   `settings.py`: デフォルトの設定値。
    -   `utils/functional.py`：機能ユーティリティ。
-   `src/rainy/`: API サービス パッケージのディレクトリ。
    -   `app.py`: FastAPI アプリケーション定義。
    -   `api/endpoints/`: API ルート定義。
        -   `chat.py`: ディープ エージェント モジュールと統合された同期およびストリーミング チャット インターフェイス。
        -   `health.py`: ヘルスチェックインターフェイス。
        -   `urls.py`：統一配線実装。
    -   `middleware/`：カスタムミドルウェア（処理時間、統一応答形式）。
    -   `settings.py`: API モジュールのデフォルト設定。
-   `tests/`: テストディレクトリ、構造、および`src`保持一致。
-   `docs/`: 多言語ドキュメント。
-   `pyproject.toml`: プロジェクトのメタデータ、依存関係、およびツール構成。
-   `uv.lock`: 依存関係のバージョンをロックします。
-   `LICENSE`: Apache ライセンス 2.0。

## 🧪 テスト

プロジェクト利用`pytest`テストを実行して質問する**100%**テスト範囲。

### テストの実行

-   **明日のテストを実行する**:
    ```bash
    PYTHONPATH=src TOMORROW_APP=tomorrow TOMORROW_SETTINGS_MODULE=tomorrow.settings uv run pytest tests/tomorrow
    ```

-   **Rainy テストを実行する**:
    ```bash
    PYTHONPATH=src RAINY_APP=rainy RAINY_SETTINGS_MODULE=rainy.settings uv run pytest tests/rainy
    ```

### カバレッジテストを実行する

テストカバレッジが以下に達する必要があります**100%**。

```bash
PYTHONPATH=src \
TOMORROW_APP=tomorrow TOMORROW_SETTINGS_MODULE=tomorrow.settings \
RAINY_APP=rainy RAINY_SETTINGS_MODULE=rainy.settings \
uv run coverage run --rcfile=pyproject.toml -m pytest && uv run coverage report --rcfile=pyproject.toml
```

## 📄ライセンス

このプロジェクトでは、**Apache ライセンス 2.0**ライセンス。詳しくはこちらをご覧ください[ライセンス](LICENSE)書類。
