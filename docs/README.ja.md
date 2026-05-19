# nhm-deepagents

[簡体字中国語](/docs/README.zh.md)\|[英語](/docs/README.en.md)\|[日本語](/docs/README.ja.md)\|[繁体中文](/docs/README.zh-TW.md)

ディープエージェント用の Python プロジェクト。

## 概要

`nhm-deepagents`は、ディープ エージェントに焦点を当てた Python プロジェクトです。最新の Python 機能とツールを使用して、堅牢な開発エクスペリエンスを提供します。

## 環境要件

-   **パイソン**: >= 3.14
-   **包管理器**:[紫外線](https://github.com/astral-sh/uv)

## インストールとセットアップ

開発を開始するには、次の手順に従ってください。

1.  **インストール`uv`**:
    まだインストールしていない場合`uv`、あなたはそれをフォローすることができます[公的倉庫](https://github.com/astral-sh/uv)の指示に従ってください。

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

## 開発スクリプト

このプロジェクトでは、`black`そして`isort`フォーマットして使用してください`pre-commit`品質チェックを実施します。

-   **フォーマットコード**:
    ```bash
    uv run black .
    uv run isort .
    ```

-   **コミット前フックを手動で実行する**:
    ```bash
    uv run pre-commit run --all-files
    ```

## プロジェクトの構造

-   `src/tomorrow/`: コアパッケージディレクトリ。
-   `pyproject.toml`: プロジェクトの構成と依存関係の管理。
-   `.pre-commit-config.yaml`: コミット前のフック構成。
-   `LICENSE`: Apache ライセンス 2.0。

## 環境変数

-   TODO: 必要な環境変数をここに記録します。

## テスト

-   TODO: テストを追加し、その実行方法を文書化します (例:`uv run pytest`）。

## ライセンス

このプロジェクトでは、**Apache ライセンス 2.0**ライセンス。詳細については、を参照してください。[ライセンス](../LICENSE)書類。
