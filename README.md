# math-symbol-ime-dict

数学記号を ASCII Math / Typst 風の名前で入力するためのユーザー辞書です。
`data/math_symbols.csv` を唯一のソースにして、Microsoft IME、Google 日本語入力 / Mozc、azooKey for macOS 用のファイルを生成します。

例:

```text
land      -> ∧
lor       -> ∨
forall    -> ∀
exists    -> ∃
subseteq  -> ⊆
RR        -> ℝ
alpha     -> α
Gamma     -> Γ
```

## 同梱されている生成済みファイル

| パス                                                     | 用途                            | 形式                                                |
| -------------------------------------------------------- | ------------------------------- | --------------------------------------------------- |
| `dist/msime/math_symbols_msime_utf16le.txt`              | Microsoft IME                   | UTF-16 LE BOM / TSV / `読み<TAB>語句<TAB>品詞`      |
| `dist/google/math_symbols_google_utf8.tsv`               | Google 日本語入力 / Mozc        | UTF-8 / TSV / `よみ<TAB>単語<TAB>品詞`              |
| `dist/google/math_symbols_google_utf8_with_comments.tsv` | Google 日本語入力 / Mozc 確認用 | UTF-8 / TSV / `よみ<TAB>単語<TAB>品詞<TAB>コメント` |
| `dist/azookey/math_symbols_azookeymac.plist`             | azooKey for macOS               | `defaults import` 用 plist                          |
| `dist/azookey/math_symbols_azookey_items.json`           | azooKey 確認用                  | plist 内に格納する JSON payload                     |

現在の登録数は 783 件です。

## 使い方

### Microsoft IME

Microsoft IME の「ユーザー辞書ツール」を開き、「ツール」→「テキスト ファイルからの登録」で `dist/msime/math_symbols_msime_utf16le.txt` を選択します。

### Google 日本語入力 / Mozc

辞書ツールで対象の辞書を選び、「この辞書にインポート」または「新規辞書にインポート」から `dist/google/math_symbols_google_utf8.tsv` を選択します。

Google 日本語入力では、辞書ツールの列は「よみ」「単語」「品詞」「コメント」です。通常は 3 列版を使い、コメントも保持したい場合だけ 4 列版を試してください。

### azooKey for macOS

`dist/azookey/math_symbols_azookeymac.plist` は azooKey for macOS の設定 plist として生成しています。既存の azooKeyMac ユーザー辞書を置き換える可能性があるため、先にバックアップしてから取り込んでください。

```sh
defaults export dev.ensan.inputmethod.azooKeyMac ~/Desktop/azooKeyMac-backup.plist
defaults import dev.ensan.inputmethod.azooKeyMac dist/azookey/math_symbols_azookeymac.plist
```

その後、azooKey for macOS を再起動してください。

注意: azooKey iOS 版の一括インポート形式は、このリポジトリ作成時点で公式に安定した公開仕様としては扱っていません。このターゲットは azooKey for macOS 向けです。

## ソース CSV

`data/math_symbols.csv` が唯一の編集対象です。

| カラム         | 意味                                                 |
| -------------- | ---------------------------------------------------- |
| `reading`      | 入力する ASCII 名。例: `land`, `arrow.r`, `RR`       |
| `symbol`       | 変換候補として出す記号                               |
| `msime_pos`    | Microsoft IME 用の品詞。既定は `短縮よみ`            |
| `google_pos`   | Google 日本語入力 / Mozc 用の品詞。既定は `短縮よみ` |
| `azookey_hint` | azooKey payload の `hint`                            |
| `comment`      | 確認用コメント。主に Unicode 名                      |

## 生成方法

Python 3.12 以上と `uv` を使います。ランタイム依存は標準ライブラリのみです。

```sh
uv run python scripts/generate.py
```

CLI としても実行できます。

```sh
uv run python scripts/generate.py build
uv run python scripts/generate.py validate
uv run python scripts/generate.py build --targets google azookey
```

## 開発用コマンド

`ruff` と `ty` は `uv` の dependency group として定義しています。

```sh
uv sync --group dev
uv run ruff format .
uv run ruff check .
uv run ty check
PYTHONPATH=src uv run python -m unittest discover -s tests
```

## リポジトリ構成

```text
math-symbol-ime-dict/
├── data/
│   └── math_symbols.csv
├── dist/
│   ├── azookey/
│   ├── google/
│   └── msime/
├── scripts/
│   └── generate.py
├── src/
│   └── math_symbol_ime_dict/
├── tests/
├── pyproject.toml
└── README.md
```

## 設計メモ

- 生成結果を再現しやすいよう、azooKey の `id` はランダム UUID ではなく `reading + symbol` から生成した UUIDv5 にしています。
- Google 日本語入力 / Mozc は UTF-8 TSV、Microsoft IME は UTF-16 LE BOM 付き TSV を生成します。
- 記号名は AsciiMath でよく使われる `land`, `lor`, `sqrt`, `subseteq` 系と、Typst 風の `arrow.r`, `gt.eq`, `RR` 系の alias を併用しています。
