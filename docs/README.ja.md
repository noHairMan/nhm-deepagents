# nhm-deepagents

[![Build Status](https://github.com/noHairMan/nhm-deepagents/actions/workflows/build.yml/badge.svg)](https://github.com/noHairMan/nhm-deepagents/actions/workflows/build.yml)[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/noHairMan/nhm-deepagents/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/noHairMan/nhm-deepagents/blob/python-coverage-comment-action-data/htmlcov/index.html)[![Lint: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)[![Python Version](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/release/python-3140/)[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)[![Repo Size](https://img.shields.io/github/repo-size/noHairMan/nhm-deepagents)](https://github.com/noHairMan/nhm-deepagents)[![Last Commit](https://img.shields.io/github/last-commit/noHairMan/nhm-deepagents)](https://github.com/noHairMan/nhm-deepagents)

[簡体字中国語](/docs/README.zh.md)\|[英語](/docs/README.en.md)\|[日本語](/docs/README.ja.md)\|[繁体中文](/docs/README.zh-TW.md)

最新の LLM フレームワークを使用して Deep Agent を構築および実行する Python プロジェクト。

## 🌟プロジェクト概要

`nhm-deepagents`は、ディープ エージェントに焦点を当てたプロフェッショナルな Python プロジェクトです。最新の Python 機能 (3.14 以降) と強力なツールを活用して、AI エージェントの研究とアプリケーションに高品質の開発エクスペリエンスを提供します。

プロジェクトには 2 つの主要モジュールが含まれています。

-   **`tomorrow`**: コアエージェントモジュール。コードネームはゲーム『デス・ストランディング2: オン・ザ・ビーチ』の登場人物から取られている。**明日**（エル・ファニングが演じる）。プロットでは、彼女は主人公サム・ブリッジズの娘であり、前作のキャラクターでもあることが明らかになりました。**ルー**(BB-28)。
-   **`rainy`**: FastAPIをベースとしたAPIサービスモジュール。コードネームもデス・ストランディング2のキャラクターから取られています**雨が降る**（忽那汐里が演じる）。ゲーム内では「タイムフォール」と回復の「コアフォール」を引き起こす魔法の力を持ち、傷つけることも治すこともできる「ファルマコン」として描かれている。

このプロジェクトは、`deepagents`フレームワークはユーザー入力を分析して渡します`rainy`このモジュールは外部同期を提供します (`/api/chat`）そして**ストリーミング (`/api/chat/stream`）**APIインターフェース。

### コア機能

-   **ディープエージェント**: 集成`deepagents`複雑なタスク処理とステータス管理をサポートするフレームワーク。
-   **スキルモジュール**：サポートを通じて`TOMORROW_SKILLS`エージェントのスケーラブルなドメイン機能をロードするようにスキル ディレクトリを構成します。
-   **子代理**：サポートを通じて`TOMORROW_SUBAGENTS`専用サブエージェントとそのモデル、スキル、システム プロンプトを構成します。
-   **コードインタープリタ**: QuickJS ミドルウェアを統合して、エージェントにコード実行機能を提供します。
-   **再帰的制御**：サポートを通じて`TOMORROW_RECURSION_LIMIT`エージェントの再帰呼び出しの深さを制限します。
-   **ライフサイクル管理**： 導入`AgentManager`エージェント インスタンスの作成と破棄を一元管理することで、リソースの適切な初期化が保証されます。
-   **高性能 API**: FastAPI 上に構築され、同期応答と Server-Sent Events (SSE) ストリーミング出力をサポートします。
-   **信頼性の保証**: 強制型ヒント、Ruff 静的チェック、100% のテスト カバレッジ要件。

## ⚙️CI/CD

このプロジェクトには、以下を含む GitHub Actions ワークフローが統合されています。

-   **テストと適用範囲**: テストを自動的に実行し、コード カバレッジをチェックします。
-   **文書翻訳**： 自動的に`README.zh.md`多言語（英語、日本語、繁体字中国語）に翻訳されます。
-   **コード仕様**：自動実行`ruff`チェックしてフォーマットし、一貫したコード スタイルと高品質を確保します。
-   **CIプロセスの最適化**: ワークフロー トリガー パス ルールが強化され、関連するコードまたは構成が変更された場合にのみビルドがトリガーされ、効率が向上します。

## 🛠️ テクノロジースタック

-   **言語**:[パイソン](https://www.python.org/)>= 3.14
-   **包管理器**:[紫外線](https://github.com/astral-sh/uv)
-   **APIフレームワーク**:[早い](https://fastapi.tiangolo.com/)
-   **ウェブサーバー**:[ユビコーン](https://www.uvicorn.org/)
-   **エージェントフレームワーク**:[ディープエージェント](https://github.com/zongxuheng/deepagents)(LangGraph/LangChainに基づく)
-   **LLMプロバイダー**:[であること](https://ollama.com/)、[ハグ顔](https://huggingface.co/)そして[人間的](https://www.anthropic.com/)
-   **コードの実行**:[langchain-quickjs](https://github.com/langchain-ai/langchainjs)QuickJSミドルウェア提供
-   **配置管理**:[ピダンティックな設定](https://docs.pydantic.dev/latest/usage/settings/)
-   **例外処理**: カスタム例外システム (`TomorrowError`とそのサブクラス)、モデル、バックエンド、ストレージ、チェックポイントのエラーをカバーします。
-   **コードの品質**:[ラフ](https://github.com/astral-sh/ruff)(ブラックとアイソートを置き換えます)、`pre-commit`、厳密な型ヒンティング
-   **テストと適用範囲**:`pytest`,`coverage`

## 📋 環境要件

-   **Python 3.14+**
-   **紫外線**: 高速な Python パッケージ インストーラーおよびパーサー。
-   **であること**: 実行中でアクセス可能である必要があります。
-   **LLMモデル**: デフォルトで Ollama を使用します`qwen3.5:9b`。次のコマンドを使用して取得できます。
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

使用`langgraph-cli`エージェント API サービスを開始します。

```bash
uv run langgraph dev
```

CLI はルート ディレクトリを読み取ります。`langgraph.json`、名前を公開します`tomorrow`グラフ。

## ⚙️ 配置

このプロジェクトでは、**ピダンティックな設定**構成管理を実行します。設定はそれぞれ次のように定義されています。`src/tomorrow/settings.py`(明日)和`src/rainy/settings.py`(雨)、環境変数を使用することも、`.env`ファイルが上書きされます。環境変数は最も高い優先度を持ち、Tomorrow によって使用されます。`TOMORROW_`Rainy によって使用されるプレフィックス`RAINY_`接頭語。

### 環境変数

環境変数にはデフォルトで接頭辞が付けられます`TOMORROW_`(コアモジュール) または`RAINY_`(API モジュール) が最初にあります。

#### Tomorrow 配置 (核心)

| 変数                         | 説明する                                      | デフォルト値                             |
| -------------------------- | ----------------------------------------- | ---------------------------------- |
| `TOMORROW_APP`             | アプリケーション名 (環境変数の接頭辞として使用)                 | `tomorrow`                         |
| `TOMORROW_MODEL`           | モデル構成、OLLAMA、HUGGINGFACE、ANTHROPIC をサポート  | `{"type": ModelType.OLLAMA, ...}`  |
| `TOMORROW_CHECKPOINT`      | チェックポイント構成、MEMORY および SQLITE をサポート        | `{"type": CheckpointType.MEMORY}`  |
| `TOMORROW_BACKEND`         | バックエンド構成、FILESYSTEM および LOCAL_SHELL をサポート | `{"type": BackendType.FILESYSTEM}` |
| `TOMORROW_STORE`           | ストレージ構成、MEMORY および SQLITE をサポート           | `{"type": StoreType.SQLITE}`       |
| `TOMORROW_SKILLS`          | スキルカタログ一覧                                 | `["skills/"]`                      |
| `TOMORROW_SUBAGENTS`       | サブエージェント構成リスト                             | `[]`                               |
| `TOMORROW_RECURSION_LIMIT` | エージェント再帰呼び出しの上限                           | `100`                              |

モデル設定が渡されました`TOMORROW_MODEL`入ってくる。 Anthropic を使用する場合は、モデル タイプを次のように設定します。`anthropic`、モデル名と API キーを指定します。例:

```bash
export TOMORROW_MODEL='{"type":"anthropic","anthropic":{"model":"claude-sonnet-5","api_key":"your-anthropic-api-key"}}'
```

Ollama または HuggingFace を使用する場合、それらを個別に設定できます`ollama`または`huggingface`物体;特定のフィールドとデフォルト値については、を参照してください。`src/tomorrow/settings.py`。

サブエージェント構成が渡されました`TOMORROW_SUBAGENTS`渡される各サブエージェントには少なくとも次のものが必要です`name`、`description`そして`system_prompt`フィールドに指定することもできます`model`そして`skills`、例えば：

```bash
export TOMORROW_SUBAGENTS='[{"name":"researcher","description":"负责资料检索","system_prompt":"你是一名研究助手。","skills":["skills/research/"]}]'
```

#### Rainy 配置 (API)

| 変数                 | 説明する                      | デフォルト値           |
| ------------------ | ------------------------- | ---------------- |
| `RAINY_HOST`       | APIサービスリスニングアドレス          | `localhost`      |
| `RAINY_PORT`       | APIサービスポート                | `8000`           |
| `RAINY_APP`        | アプリケーション名 (環境変数の接頭辞として使用) | `rainy`          |
| `RAINY_MIDDLEWARE` | 有効なミドルウェアのリスト             | (settings.pyを参照) |

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
    -   `graph.py`:`langgraph-cli`使用するグラフエントリ。
    -   `core/agent.py`: ディープ エージェントとその命令を定義します。`AgentManager`ライフサイクル管理を実行します。
    -   `core/backend/`: バックエンド読み込みロジックの統合、サポート`FILESYSTEM`そして`LOCAL_SHELL`。
    -   `core/checkpoint/`: チェックポイントの実装、サポート`MEMORY`そして`SQLITE`。
    -   `core/model/`：モデルローディングの実装、サポート`OLLAMA`、`HUGGINGFACE`そして`ANTHROPIC`。
    -   `core/store/`: ストレージ実装、サポート`MEMORY`そして`SQLITE`。
    -   `exceptions.py`: アプリケーション固有の例外クラス システムを定義します。
    -   `models/constants/`: さまざまなタイプの定数 (バックエンド、チェックポイント、モデル、ストア) を定義します。
    -   `settings.py`: デフォルトの設定値。
    -   `utils/functional.py`：機能ユーティリティ。
-   `src/rainy/`: API サービス パッケージのディレクトリ。
    -   `app.py`: FastAPI アプリケーション定義、統合されたライフサイクル管理およびルーティング。
    -   `lifespan.py`: アプリケーションの起動およびシャットダウン ロジックを処理し、エージェント インスタンスのライフ サイクルを管理します。
    -   `api/endpoints/`: API ルート定義。
        -   `chat.py`: 同期およびストリーミング チャット インターフェイス (OpenAI のような応答形式を使用)、ディープ エージェント モジュールと統合されています。
            -   `POST /api/chat`: チャットの応答を同期します。
            -   `POST /api/chat/stream`: SSE ストリーミング応答。
            -   `POST /api/chat/stream/event`: イベント ストリームの応答。
        -   `health.py`: ヘルスチェックインターフェイス。
        -   `urls.py`：統一配線実装。
    -   `middleware/`：カスタムミドルウェア（処理時間、統一応答形式）。
    -   `settings.py`: API モジュールのデフォルト設定。
-   `tests/`: テストディレクトリ、構造、および`src`保持一致。
-   `docs/`: 多言語ドキュメント。
-   `pyproject.toml`: プロジェクトのメタデータ、依存関係、およびツール構成。
-   `langgraph.json`:`langgraph-cli`グラフと環境構成。
-   `uv.lock`: 依存関係のバージョンをロックします。
-   `LICENSE`: Apache ライセンス 2.0。

## 🧪 テスト

プロジェクト利用`pytest`テストを実行して質問する**100%**テスト範囲。

### テストの実行

-   **明日のテストを実行する**:
    ```bash
    PYTHONPATH=src TOMORROW_APP=tomorrow uv run pytest tests/tomorrow
    ```

-   **Rainy テストを実行する**:
    ```bash
    PYTHONPATH=src RAINY_APP=rainy uv run pytest tests/rainy
    ```

### カバレッジテストを実行する

テストカバレッジが以下に達する必要があります**100%**。

```bash
PYTHONPATH=src \
TOMORROW_APP=tomorrow \
RAINY_APP=rainy \
uv run coverage run --rcfile=pyproject.toml -m pytest && uv run coverage report --rcfile=pyproject.toml
```

## 📄ライセンス

このプロジェクトでは、**Apache ライセンス 2.0**ライセンス。詳しくはこちらをご覧ください[ライセンス](LICENSE)書類。
