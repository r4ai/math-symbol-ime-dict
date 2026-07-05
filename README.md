# math-symbol-ime-dict

数学記号を日本語IMEのユーザー辞書で入力するための辞書です。
`data/math_symbols.csv` をソースにして、Microsoft IME、Google 日本語入力 / Mozc、azooKey for macOS 向けのインポートファイルを生成します。

生成済み辞書の登録数は 1846 件です。

## 入力方法

日本語IMEのひらがな/全角入力中は、全項目に付く `M` prefix 付きの読みを使うのが基本です。
`M` の後ろは元の読みをそのまま付けるため、大文字小文字の区別も保てます。

```text
Mland      -> ∧
Mlor       -> ∨
Mforall    -> ∀
Mexists    -> ∃
Msubseteq  -> ⊆
MRR        -> ℝ
Malpha     -> α
MGamma     -> Γ
MAlpha     -> Α
```

よく使う一部の読みには、prefix なしの先頭大文字 alias もあります。

```text
Land    -> ∧
Forall  -> ∀
Exists  -> ∃
Sqrt    -> √
```

記号を含む読みには、全角記号で入力したときの読みも追加されます。

```text
M->      -> →
M－＞    -> →
Mー＞    -> →
M1/2     -> ½
M１／２  -> ½
```

`land` や `alpha` のような prefix なしの小文字読みも登録されています。
これは英数入力時や、ASCII の読みを直接扱えるIME設定向けの互換経路です。
ひらがなローマ字入力中は `land` が `ぁんd` のようになりやすいため、`Mland` か `Land` を使ってください。

```text
land      -> ∧
alpha     -> α
rightarrow -> →
```

`Alpha` や `Rightarrow` のように既存の大文字読みとして意味があるものは、衝突を避けるため prefix なし alias を増やしていません。
その場合は `Malpha` / `MAlpha` や `Mrightarrow` / `MRightarrow` を使います。

## 取り込み

| IME                         | 使うファイル                                             | 形式                                                |
| --------------------------- | -------------------------------------------------------- | --------------------------------------------------- |
| Microsoft IME               | `dist/msime/math_symbols_msime_utf16le.txt`              | UTF-16 LE BOM / TSV / `読み<TAB>語句<TAB>品詞`      |
| Google 日本語入力 / Mozc    | `dist/google/math_symbols_google_utf8.tsv`               | UTF-8 / TSV / `よみ<TAB>単語<TAB>品詞`              |
| Google 日本語入力 / Mozc 確認用 | `dist/google/math_symbols_google_utf8_with_comments.tsv` | UTF-8 / TSV / `よみ<TAB>単語<TAB>品詞<TAB>コメント` |
| azooKey for macOS           | `dist/azookey/math_symbols_azookeymac.plist`             | `defaults import` 用 plist                          |

### Microsoft IME

Microsoft IME の「ユーザー辞書ツール」を開き、「ツール」→「テキスト ファイルからの登録」で `dist/msime/math_symbols_msime_utf16le.txt` を選択します。

### Google 日本語入力 / Mozc

辞書ツールで対象の辞書を選び、「この辞書にインポート」または「新規辞書にインポート」から `dist/google/math_symbols_google_utf8.tsv` を選択します。

コメントも確認したい場合だけ、4列版の `dist/google/math_symbols_google_utf8_with_comments.tsv` を使ってください。

### azooKey for macOS

`dist/azookey/math_symbols_azookeymac.plist` は azooKey for macOS の設定 plist です。
既存のユーザー辞書を置き換える可能性があるため、先にバックアップしてから取り込んでください。

```sh
defaults export dev.ensan.inputmethod.azooKeyMac ~/Desktop/azooKeyMac-backup.plist
defaults import dev.ensan.inputmethod.azooKeyMac dist/azookey/math_symbols_azookeymac.plist
```

取り込み後、azooKey for macOS を再起動してください。

## 編集と生成

編集対象は `data/math_symbols.csv` です。

| カラム         | 意味                                                 |
| -------------- | ---------------------------------------------------- |
| `reading`      | 入力する基本読み。例: `land`, `arrow.r`, `RR`, `^^`  |
| `symbol`       | 変換候補として出す記号                               |
| `msime_pos`    | Microsoft IME 用の品詞。既定は `短縮よみ`            |
| `google_pos`   | Google 日本語入力 / Mozc 用の品詞。既定は `短縮よみ` |
| `azookey_hint` | azooKey payload の `hint`                            |
| `comment`      | 確認用コメント。主に Unicode 名                      |

生成には Python 3.12 以上と `uv` を使います。
ランタイム依存は標準ライブラリのみです。

```sh
uv run python scripts/generate.py
uv run python scripts/generate.py validate
uv run python scripts/generate.py build --targets google google-comments
```

## 開発

```sh
uv sync --group dev
uv run ruff format .
uv run ruff check .
uv run ty check
PYTHONPATH=src uv run python -m unittest discover -s tests
```

## 設計方針

- 基本読みは `data/math_symbols.csv` にだけ書き、IME向け alias は生成時に追加します。
- 全項目に `M` prefix 付き alias を作り、日本語IME中でも衝突せず入力できる経路を確保します。
- prefix なしの先頭大文字 alias は、使用頻度が高く、既存の読みと衝突しないものだけに限定します。
- 同じ読みが複数の記号に向かう場合は生成時にエラーにします。
- azooKey の `id` は `reading + symbol` から生成した UUIDv5 にして、生成結果が毎回安定するようにしています。
