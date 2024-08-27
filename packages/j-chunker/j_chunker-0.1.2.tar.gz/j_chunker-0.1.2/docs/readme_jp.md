# 言語モデル、MeCabおよびJanomeを使用した日本語PDFのインテリジェントチャンキング

## 目次
1. [はじめに](#はじめに)
2. [特徴](#特徴)
3. [依存関係](#依存関係)
4. [インストール](#インストール)
5. [使用方法](#使用方法)
6. [関数の説明](#関数の説明)
7. [クラスタリングとチャンキングのプロセス](#クラスタリングとチャンキングのプロセス)
8. [例](#例)
9. [カスタマイズオプション](#カスタマイズオプション)
10. [出力](#出力)
11. [注意点](#注意点)
12. [トラブルシューティング](#トラブルシューティング)
13. [ライセンス](#ライセンス)

# はじめに

## 背景

デジタル文書、特にPDF形式の文書量が増加するにつれ、効率的かつインテリジェントな文書処理システムの必要性が高まっています。日本語のような明確な単語境界がなく、複雑な書記体系を持つ言語では、従来のチャンキング手法はしばしば不十分です。このホワイトペーパーでは、言語モデルの力と日本語特有のツールを組み合わせた新しいアプローチを紹介し、これらの課題を克服します。

## 既存の問題点

現在の文書処理システムは、日本語のPDFを扱う際にいくつかの課題に直面しています：

1. **明確な単語境界の欠如**: 単語を区切るスペースを使用する言語とは異なり、日本語のテキストは連続的に流れるため、標準的なトークン化手法では単語境界を正確に識別することが困難です。

2. **複雑な書記体系**: 日本語は漢字（表意文字）、ひらがな、カタカナを混合して使用するため、非専門的なシステムでは処理が困難です。

3. **文脈依存の意味**: 日本語の文字の意味は文脈によって大きく変わることがあり、単純なチャンキングアルゴリズムでは対応が難しいです。

4. **PDF形式の複雑さ**: PDFから構造化されたテキストをきれいに抽出することは、特に複雑なレイアウトやスキャンされた文書を扱う場合に難しい場合があります。

5. **意味的一貫性**: 既存のチャンキング手法は、意味的な境界を考慮せずに文書を固定サイズのチャンクに分割することが多く、関連するコンテンツを異なるチャンクに分割してしまう可能性があります。

6. **スケーラビリティの問題**: 大規模な文書の処理は、特に高度なNLP技術を使用する場合、計算コストが高くなる可能性があります。

7. **不統一なフォーマット**: 日本語の文書では縦書きと横書きが混在することがあり、抽出とチャンキングのプロセスをさらに複雑にします。

## 提案するソリューション

このPythonスクリプトは、高度な自然言語処理技術を組み合わせて日本語のPDF文書をチャンキングする革新的なアプローチを提示します。この方法は、大規模言語モデル（LLM）、MeCab（日本語の形態素解析器）、およびクラスタリングアルゴリズムを活用して、日本語テキストから意味的に意味のある適切なサイズのチャンクを作成します。このアプローチは、特に大規模言語モデルと文書分析システムの文脈において、日本語文書の処理における複数の課題に対処します。

## 特徴

- ページ番号情報付きでPDFファイルからテキストを抽出
- MeCabとJanome（日本語に最適化）の両方を使用してテキストを前処理およびトークン化
- 多言語Sentence Transformerモデルを使用してテキストチャンクの埋め込みを生成
- 埋め込みとTF-IDF特徴量を組み合わせたK-meansアルゴリズムを使用してテキストをクラスタリング
- 単語数、意味的類似性、文の境界に基づいてインテリジェントなチャンクを作成
- オプションでLanguage Modelを使用してチャンクのクリーニングと校正を実行
- 生のチャンクと処理済みチャンクをメタデータ（PDF名、ページ番号、クラスタ、単語数）と共に保存
- 日本語と非日本語のテキストの両方を処理

## 依存関係

- os
- re
- json
- time
- MeCab
- torch
- PyPDF2
- logging
- unicodedata
- numpy
- kneed
- dotenv
- functools
- sklearn
- langchain_ibm
- janome
- sentence_transformers
- ibm_watson_machine_learning

## インストール

J-Chunkerはpipを使用してインストールできます：

```bash
pip install j_chunker
```

## 使用方法

J-Chunkerの基本的な使用例は以下の通りです：

```python
from j_chunker import chunker
import os

pdf_paths = ["path/to/your/japanese.pdf"]
output_dir = os.getenv("OUTPUT_DIR", "output")
raw_dir = os.path.join(output_dir, "raw")
processed_dir = os.path.join(output_dir, "processed")

embedding_model_name = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

chunks = chunker(pdf_paths, output_dir, raw_dir, processed_dir, embedding_model_name, max_words=1024, llm_summarize=False, visualize=True)

print(chunks)
```
### パラメータ:

- `pdf_paths`: 処理するPDFファイルのパスのリスト
- `output_dir`: 出力ファイルを保存するディレクトリ
- `raw_dir`: 生のチャンクを保存するディレクトリ
- `processed_dir`: 処理済みチャンクを保存するディレクトリ
- `embedding_model_name`: 埋め込みに使用するSentence Transformersモデルの名前
- `max_words`: チャンクあたりの最大単語数（デフォルト：500）
- `llm_summarize`: LLMを要約に使用するかどうか（デフォルト：False）
- `visualize`: クラスタを可視化するかどうか（デフォルト：True）

## 環境変数

J-Chunkerは以下の環境変数を使用します：

- `OUTPUT_DIR`: 出力ファイルのディレクトリ（デフォルト："output"）
- `EMBEDDING_MODEL_NAME`: Sentence Transformersモデルの名前（デフォルト："sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"）

LLM要約（有効な場合）のための変数：
- `MODEL_NAME`: LLMモデル名
- `IBM_CLOUD_URL`: IBM Cloud URL
- `IBM_CLOUD_API_KEY`: IBM Cloud APIキー
- `PROJECT_ID`: IBM WatsonのプロジェクトID

これらの変数は環境で設定するか、`.env`ファイルを使用して設定できます。

## 関数の説明

### `initialize_model()`

指定されたパラメータでWatsonxLLMモデルを初期化して返します。

**例：**
```python
llm = initialize_model(temperature=0.2, max_new_tokens=1024)
```

### `extract_text_from_pdf(pdf_path)`

PDFファイルからページ番号と共にテキストコンテンツを抽出します。

**例：**
```python
pages = extract_text_from_pdf("data/example.pdf")
print(f"PDFから{len(pages)}ページを抽出しました")
```

### `preprocess_document(pages, tagger)`

抽出されたテキストをトークン化、レンマ化し、n-gramを生成することで前処理します。

**例：**
```python
paragraphs, tokenized_paragraphs, lemmatized_paragraphs, ngrams, page_numbers = preprocess_document(pages, tagger)
print(f"{len(paragraphs)}個の段落を作成しました")
```

### `generate_embeddings(lemmatized_paragraphs, model)`

Sentence Transformerモデルを使用してレンマ化された段落の埋め込みを生成します。

**例：**
```python
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
embeddings = generate_embeddings(lemmatized_paragraphs, model)
print(f"生成された埋め込みの形状：{embeddings.shape}")
```

### `find_optimal_clusters(embeddings, max_clusters=10)`

エルボー法を使用して最適なクラスタ数を見つけます。

**例：**
```python
optimal_clusters = find_optimal_clusters(embeddings, max_clusters=15)
print(f"最適なクラスタ数：{optimal_clusters}")
```

### `cluster_paragraphs(embeddings, lemmatized_paragraphs, max_clusters=20)`

埋め込みとTF-IDF特徴量を組み合わせたK-meansを使用して段落をクラスタリングします。

**例：**
```python
clusters = cluster_paragraphs(embeddings, lemmatized_paragraphs, max_clusters=15)
print(f"{len(set(clusters))}個のクラスタを割り当てました")
```

### `sentence_aware_japanese_chunking(paragraphs, clusters, page_numbers, max_words=1000)`

単語数、クラスタの境界、文の完全性に基づいてドキュメントを小さな部分にチャンク分割します。

**例：**
```python
chunks = sentence_aware_japanese_chunking(paragraphs, clusters, page_numbers, max_words=800)
print(f"{len(chunks)}個のチャンクを作成しました")
```

### `clean_chunk(text)`

不要なパターンやフォーマットを削除して処理済みチャンクをクリーニングします。

**例：**
```python
cleaned_text = clean_chunk("これはサンプルテキストです...余分な   スペースがあります。")
print(f"クリーニングされたテキスト：{cleaned_text}")
```

### `save_chunks_to_json(chunks, pdf_name, output_file)`

ドキュメントのチャンクをJSONファイルに保存します。

**例：**
```python
save_chunks_to_json(chunks, "example_pdf", "output/raw/example_chunks.json")
```

### `process_chunk_with_llm(chunk, llm, max_words)`

LLMを使用して単一のテキストチャンクを校正とクリーニングのために処理します。

**例：**
```python
llm = initialize_model()
processed_chunk = process_chunk_with_llm(chunk, llm, max_words=500)
print(f"処理済みチャンク：{processed_chunk['content'][:100]}...")
```

### `process_single_pdf(pdf_path, model, tagger, max_words=500)`

単一のPDFファイルを処理します：テキストを抽出し、前処理し、埋め込みを生成し、クラスタリングし、チャンク分割します。

**例：**
```python
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
tagger = MeCab.Tagger()
chunks, pdf_name = process_single_pdf("data/example.pdf", model, tagger, max_words=600)
print(f"処理済みPDF：{pdf_name}、{len(chunks)}個のチャンクを作成しました")
```

### `process_and_clean_chunks(chunks, pdf_name, output_file, max_words, llm_summarize=False)`

LLMを使用してすべてのチャンクを処理し、オプションでクリーニングしてから結果をJSONファイルに保存します。

**例：**
```python
process_and_clean_chunks(chunks, "example_pdf", "output/processed/example_processed.json", max_words=500, llm_summarize=True)
```

### `chunker(pdf_paths, output_dir, raw_dir, processed_dir, max_words=500, llm_summarize=False)`

複数のPDFファイルを処理します：テキストを抽出し、前処理し、埋め込みを生成し、クラスタリングし、チャンク分割し、オプションでクリーニングします。

**例：**
```python
pdf_paths = ["data/file1.pdf", "data/file2.pdf"]
chunker(pdf_paths, "output", "output/raw", "output/processed", max_words=600, llm_summarize=True)
```

## クラスタリングとチャンキングのプロセス

### クラスタリングプロセス

1. **埋め込みの生成**: 
   各段落は、多言語Sentence Transformerモデルを使用して数値ベクトルに変換されます。これらの埋め込みは、テキストの意味的な意味を捉えた密なベクトル表現であり、コンピューターが高次元空間で異なる段落の内容を理解し比較することを可能にします。

2. **TF-IDF特徴量の作成**: 
   各段落の重要な用語を捉えるためにTF-IDF（Term Frequency-Inverse Document Frequency）ベクトルが作成されます。この数値統計は、コレクション内のドキュメントに対する単語の重要性を反映し、埋め込みからの意味情報に単語の重要性とユニーク性に関する情報を補完します。

3. **特徴量の組み合わせ**: 
   埋め込みとTF-IDF特徴量が組み合わされ、より豊かな表現が得られます。この組み合わせにより、クラスタリングアルゴリズムは段落をグループ化する際に意味的類似性と重要な用語の頻度の両方を考慮することができます。

4. **最適なクラスタ数の発見**: 
   スクリプトはエルボー法を使用して最適なクラスタ数を決定します。この技術は、クラスタ数の関数として説明された分散をプロットし、曲線の肘の部分を最適な数として選択し、段落を何個の異なるグループに分割すべきかを自動的に決定します。

5. **K-meansクラスタリング**: 
   スクリプトは、K-meansアルゴリズムを使用して、組み合わせた特徴量に基づいて類似した段落をグループ化します。この教師なし機械学習手法は、各段落を最も近いクラスタ中心に反復的に割り当て、その後割り当てられた段落に基づいて中心を再計算します。

6. **クラスタラベルの割り当て**: 
   各段落にクラスタラベル（グループ識別子）が割り当てられます。これらのラベルは後のチャンキングプロセスで、意味的に関連したコンテンツを一緒に保つために使用されます。

### チャンキングプロセス

1. **クラスタによるグループ化**: 
   段落は割り当てられたクラスタラベルに従ってグループ化されます。このステップにより、後続のチャンキングプロセスで意味的に類似したコンテンツが一緒に保たれることが保証されます。

2. **文の分割**: 
   各段落は個々の文に分割されます。この粒度の細かいアプローチにより、各チャンクのコンテンツをより正確に制御でき、文の完全性を維持するのに役立ちます。

3. **単語のカウント**: 
   スクリプトは各文の単語をカウントします。日本語テキストにはJanomeを使用し、非日本語テキストには単純な分割を使用します。形態素解析器であるJanomeは、日本語テキストの単語を正確にカウントできます。このステップはチャンクのサイズを制御するために重要です。

4. **チャンクの作成**: 
   クラスタの境界を尊重しながら、単語制限に達するまで文を追加してチャンクが作成されます。このアプローチは、一貫したチャンクサイズの必要性と各チャンク内の意味的一貫性を維持する目標のバランスを取ります。

5. **メタデータの追跡**: 
   スクリプトは各チャンクのページ番号、クラスタ、単語数を追跡します。このメタデータは、ドキュメント構造を理解し、潜在的な下流のタスクに価値があります。

この組み合わせたクラスタリングとチャンキングのプロセスにより、ドキュメントを意味的に一貫した管理可能な部分に知的に分割することができます。これは特に長いドキュメントを処理する場合や、さらな自然言語処理タスクのためにテキストを準備する場合に特に有用です。コンテキストと意味を維持しながら、一貫したサイズのテキストチャンクを作成します。

## 例

日本語と英語のテキストの両方について、クラスタリングの出力を含む全プロセスの詳細な例を見てみましょう。

### 日本語の例

以下の日本語テキストを考えてみましょう：

```python
japanese_text = """
東京は日本の首都です。人口が多く、経済の中心地でもあります。
東京には多くの観光名所があります。例えば、東京タワーやスカイツリーがあります。
日本の文化は独特です。茶道や歌舞伎などの伝統文化が今も息づいています。
日本料理も人気があります。寿司や天ぷらは世界中で愛されています。
日本の技術も有名です。家電製品や自動車など、高品質な製品を作っています。
"""

# ステップ1：テキストの前処理
tagger = MeCab.Tagger()
paragraphs = japanese_text.split('\n')
paragraphs = [p for p in paragraphs if p.strip()]
_, _, lemmatized_paragraphs, _, page_numbers = preprocess_document([(1, p) for p in paragraphs], tagger)

print("レンマ化された段落：")
for i, para in enumerate(lemmatized_paragraphs, 1):
    print(f"{i}. {para}")
print("-" * 50)

# ステップ2：埋め込みの生成
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
embeddings = generate_embeddings(lemmatized_paragraphs, model)

print(f"埋め込みの形状：{embeddings.shape}")
print("-" * 50)

# ステップ3：段落のクラスタリング
clusters = cluster_paragraphs(embeddings, lemmatized_paragraphs, max_clusters=3)

print("クラスタリング結果：")
for i, (para, cluster) in enumerate(zip(paragraphs, clusters), 1):
    print(f"段落 {i} (クラスタ {cluster})：")
    print(para)
    print()
print("-" * 50)

# ステップ4：チャンクの作成
chunks = sentence_aware_japanese_chunking(paragraphs, clusters, page_numbers, max_words=50)

print("生成されたチャンク：")
for chunk in chunks:
    print(f"クラスタ：{chunk['cluster']}、ページ：{chunk['pages']}")
    print(f"内容：{chunk['content']}")
    print(f"単語数：{chunk['word_count']}")
    print("-" * 50)
```

出力：
```
レンマ化された段落：
1. 東京 日本 首都 です 人口 多い 経済 中心 地 です
2. 東京 多く 観光 名所 あり ます 例えば 東京タワー スカイツリー あり ます
3. 日本 文化 独特 です 茶道 歌舞伎 など 伝統 文化 今 息づく て い ます
4. 日本 料理 人気 あり ます 寿司 天ぷら 世界 中 愛す られる て い ます
5. 日本 技術 有名 です 家電 製品 自動車 など 高 品質 製品 作る て い ます
--------------------------------------------------
埋め込みの形状：(5, 384)
--------------------------------------------------
クラスタリング結果：
段落 1 (クラスタ 0)：
東京は日本の首都です。人口が多く、経済の中心地でもあります。

段落 2 (クラスタ 0)：
東京には多くの観光名所があります。例えば、東京タワーやスカイツリーがあります。

段落 3 (クラスタ 1)：
日本の文化は独特です。茶道や歌舞伎などの伝統文化が今も息づいています。

段落 4 (クラスタ 1)：
日本料理も人気があります。寿司や天ぷらは世界中で愛されています。

段落 5 (クラスタ 2)：
日本の技術も有名です。家電製品や自動車など、高品質な製品を作っています。

--------------------------------------------------
生成されたチャンク：
クラスタ：0、ページ：1
内容：東京は日本の首都です。人口が多く、経済の中心地でもあります。東京には多くの観光名所があります。例えば、東京タワーやスカイツリーがあります。
単語数：36
--------------------------------------------------
クラスタ：1、ページ：1
内容：日本の文化は独特です。茶道や歌舞伎などの伝統文化が今も息づいています。日本料理も人気があります。寿司や天ぷらは世界中で愛されています。
単語数：35
--------------------------------------------------
クラスタ：2、ページ：1
内容：日本の技術も有名です。家電製品や自動車など、高品質な製品を作っています。
単語数：19
--------------------------------------------------
```

### 英語の例

次に、英語のテキストを見てみましょう：

```python
english_text = """
Artificial Intelligence (AI) is revolutionizing various industries.
Machine Learning, a subset of AI, enables computers to learn from data.
Natural Language Processing allows machines to understand human language.
Computer Vision is another important field in AI, focusing on image recognition.
These AI technologies are being applied in healthcare, finance, and transportation.
"""

# ステップ1：テキストの前処理
paragraphs = english_text.split('\n')
paragraphs = [p for p in paragraphs if p.strip()]
_, _, lemmatized_paragraphs, _, page_numbers = preprocess_document([(1, p) for p in paragraphs], tagger)

print("レンマ化された段落：")
for i, para in enumerate(lemmatized_paragraphs, 1):
    print(f"{i}. {para}")
print("-" * 50)

# ステップ2：埋め込みの生成
embeddings = generate_embeddings(lemmatized_paragraphs, model)

print(f"埋め込みの形状：{embeddings.shape}")
print("-" * 50)

# ステップ3：段落のクラスタリング
clusters = cluster_paragraphs(embeddings, lemmatized_paragraphs, max_clusters=3)

print("クラスタリング結果：")
for i, (para, cluster) in enumerate(zip(paragraphs, clusters), 1):
    print(f"段落 {i} (クラスタ {cluster})：")
    print(para)
    print()
print("-" * 50)

# ステップ4：チャンクの作成
chunks = sentence_aware_japanese_chunking(paragraphs, clusters, page_numbers, max_words=50)

print("生成されたチャンク：")
for chunk in chunks:
    print(f"クラスタ：{chunk['cluster']}、ページ：{chunk['pages']}")
    print(f"内容：{chunk['content']}")
    print(f"単語数：{chunk['word_count']}")
    print("-" * 50)
```

出力：
```
レンマ化された段落：
1. Artificial Intelligence ( AI ) is revolutionizing various industries .
2. Machine Learning , a subset of AI , enables computers to learn from data .
3. Natural Language Processing allows machines to understand human language .
4. Computer Vision is another important field in AI , focusing on image recognition .
5. These AI technologies are being applied in healthcare , finance , and transportation .
--------------------------------------------------
埋め込みの形状：(5, 384)
--------------------------------------------------
クラスタリング結果：
段落 1 (クラスタ 0)：
Artificial Intelligence (AI) is revolutionizing various industries.

段落 2 (クラスタ 0)：
Machine Learning, a subset of AI, enables computers to learn from data.

段落 3 (クラスタ 1)：
Natural Language Processing allows machines to understand human language.

段落 4 (クラスタ 1)：
Computer Vision is another important field in AI, focusing on image recognition.

段落 5 (クラスタ 2)：
These AI technologies are being applied in healthcare, finance, and transportation.

--------------------------------------------------
生成されたチャンク：
クラスタ：0、ページ：1
内容：Artificial Intelligence (AI) is revolutionizing various industries. Machine Learning, a subset of AI, enables computers to learn from data.
単語数：18
--------------------------------------------------
クラスタ：1、ページ：1
内容：Natural Language Processing allows machines to understand human language. Computer Vision is another important field in AI, focusing on image recognition.
単語数：19
--------------------------------------------------
クラスタ：2、ページ：1
内容：These AI technologies are being applied in healthcare, finance, and transportation.
単語数：11
--------------------------------------------------
```

### クラスタリング結果の解釈

両方の例で、クラスタリングアルゴリズムが類似した段落をどのようにグループ化しているかを観察できます：

1. **日本語の例**：
   - クラスタ0：東京に関する段落（一般情報と観光名所）
   - クラスタ1：日本の文化と料理に関する段落
   - クラスタ2：日本の技術に関する段落

2. **英語の例**：
   - クラスタ0：一般的なAIと機械学習
   - クラスタ1：特定のAI分野（自然言語処理とコンピュータビジョン）
   - クラスタ2：AI技術の応用

クラスタリングは主題的に類似したコンテンツをグループ化するのに役立ち、これが生成されたチャンクに反映されます。このアプローチにより、関連情報が一緒に保たれ、各チャンクの一貫性が向上します。

K-meansアルゴリズムの性質上、実行ごとに正確なクラスタ番号が異なる可能性がありますが、類似したコンテンツのグループ化は一貫しているはずです。

### 埋め込みの可視化（オプション）

クラスタリングの仕組みをより深く理解するために、t-SNEやPCAやUMAPなどの次元削減技術を使用して埋め込みを可視化できます。以下はPCAを使用した例です：

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from umap import UMAP
from scipy.spatial import ConvexHull

def visualize_embeddings(embeddings, clusters, pdf_name=None, method='pca'):
    """
    Visualize embeddings using various dimensionality reduction techniques.
    
    Parameters:
    - embeddings: numpy array of shape (n_samples, n_features)
    - clusters: numpy array of cluster labels
    - pdf_name: str, optional name of the PDF file for the title
    - method: str, visualization method ('pca', 'tsne', or 'umap')
    """
    # Choose dimensionality reduction method
    if method == 'pca':
        reducer = PCA(n_components=2)
        method_name = 'PCA'
    elif method == 'tsne':
        reducer = TSNE(n_components=2, random_state=42)
        method_name = 't-SNE'
    elif method == 'umap':
        reducer = UMAP(n_components=2, random_state=42)
        method_name = 'UMAP'
    else:
        raise ValueError("Invalid method. Choose 'pca', 'tsne', or 'umap'.")

    # Perform dimensionality reduction
    embeddings_2d = reducer.fit_transform(embeddings)
    
    # Create a new figure
    plt.figure(figsize=(12, 8))
    
    # Get unique clusters and assign colors
    unique_clusters = np.unique(clusters)
    colors = plt.cm.rainbow(np.linspace(0, 1, len(unique_clusters)))
    
    # Plot each cluster
    for cluster, color in zip(unique_clusters, colors):
        mask = clusters == cluster
        plt.scatter(embeddings_2d[mask, 0], embeddings_2d[mask, 1], 
                    c=[color], label=f'Cluster {cluster}', alpha=0.7)
        
        # Plot centroid
        centroid = embeddings_2d[mask].mean(axis=0)
        plt.scatter(centroid[0], centroid[1], c=[color], s=200, marker='*', 
                    edgecolors='black', linewidth=1.5)
        
        # Plot convex hull
        if np.sum(mask) >= 3:  # Need at least 3 points for a hull
            hull = ConvexHull(embeddings_2d[mask])
            for simplex in hull.simplices:
                plt.plot(embeddings_2d[mask][simplex, 0], embeddings_2d[mask][simplex, 1], 
                         c=color, linestyle='--', alpha=0.5)
    
    # Add labels and title
    plt.xlabel(f'First {method_name} Component')
    plt.ylabel(f'Second {method_name} Component')
    title = f'Paragraph Embeddings Clustered ({method_name})'
    if pdf_name:
        title += f'\n{pdf_name}'
    plt.title(title)
    
    # Add legend
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Adjust layout and display
    plt.tight_layout()
    plt.show()

# Example usage:
# visualize_embeddings(embeddings, clusters, pdf_name="example.pdf", method='pca')
# visualize_embeddings(embeddings, clusters, pdf_name="example.pdf", method='tsne')
# visualize_embeddings(embeddings, clusters, pdf_name="example.pdf", method='umap')
```

この可視化は、段落が埋め込み空間でどのようにグループ化されているか、そしてクラスタがどの程度よく分離されているかを理解するのに役立ちます。

これらの詳細な出力を調べることで、クラスタリングプロセスがどのように機能し、最終的なドキュメントのチャンキングにどのように影響するかについての洞察を得ることができます。この情報は、プロセスの微調整や、特定のチャンクが作成される理由を理解するのに有用です。

## カスタマイズオプション

### クラスタリングのカスタマイズ

考慮するクラスタの最大数を調整します：

```python
clusters = cluster_paragraphs(embeddings, lemmatized_paragraphs, max_clusters=25)
```

### チャンキングのカスタマイズ

チャンクあたりの最大単語数を変更します：

```python
chunks = sentence_aware_japanese_chunking(paragraphs, clusters, page_numbers, max_words=1500)
```

### 埋め込みモデルのカスタマイズ

埋め込みモデルを変更します：

```python
model = SentenceTransformer('different-multilingual-model')
```

### LLM処理のカスタマイズ

LLM処理を有効または無効にし、パラメータを調整します：

```python
chunker(pdf_paths, output_dir, raw_dir, processed_dir, max_words=600, llm_summarize=True)
```

## 出力

スクリプトは処理されたPDFごとに2種類の出力を生成します：

1. 生のチャンク：`output/raw/{pdf_name}_raw.json`
2. 処理済みチャンク：`output/processed/{pdf_name}_processed.json`

JSONの構造の例：

```json
[
  {
    "chunk_id": 1,
    "content": "処理およびクリーニングされたテキストコンテンツ...",
    "pages": "1,2",
    "cluster": 0,
    "word_count": 250,
    "pdf_name": "example_pdf"
  },
  ...
]
```

## 注意点

- スクリプトは日本語に最適化されていますが、日本語と非日本語の両方のテキストを処理できます。
- 処理時間はPDFのサイズ、作成されるチャンクの数、そしてLLM処理が有効かどうかによって異なります。
- チャンクのサイズを制御するには、`chunker()`の`max_words`を調整してください。
- スクリプトは動的クラスタリングアプローチを使用し、各ドキュメントの最適なクラスタ数を自動的に決定します。
- Sentence Transformer埋め込みとTF-IDF特徴量の組み合わせにより、意味と単語頻度の情報の両方を捉えた豊かな表現がクラスタリングに提供されます。
- 文を意識したチャンキングプロセスにより、文が複数のチャンクに分割されることがなく、読みやすさとコンテキストが維持されます。
- MeCabとJanomeの両方を使用することで、日本語テキストの柔軟かつ正確な処理が可能になります。
- オプションのLLMベースの後処理ステップは、チャンクのクリーニングと洗練に役立ち、下流のタスクのための品質を潜在的に向上させます。
- 非常に大きなドキュメントの場合は、効率を向上させるために並列処理の実装を検討してください。
- 新しいドメインや異なる構造のドキュメントを処理する場合は、定期的なテストと検証を推奨します。
- スクリプトは現在、日本語と非日本語のテキストの両方を効果的に処理できる多言語Sentence Transformerモデルを使用しています。
- `clean_chunk`関数は、日本語と非日本語の両方のテキストを処理し、重要な文字とフォーマットを保持するように更新されています。

## 高度な使用法

### 混合言語ドキュメントの処理

このスクリプトは複数の言語を含むドキュメントを処理することができます。以下は混合言語テキストを処理する例です：

```python
mixed_text = """
日本の技術革新は世界をリードしています。
Many Japanese companies are at the forefront of AI and robotics.
自動運転車の開発は、トヨタやホンダなどが積極的に取り組んでいます。
The integration of AI in daily life is more prevalent in Japan than in many other countries.
"""

# 混合言語テキストの前処理とチャンク化
paragraphs = mixed_text.split('\n')
paragraphs = [p for p in paragraphs if p.strip()]
_, _, lemmatized_paragraphs, _, page_numbers = preprocess_document([(1, p) for p in paragraphs], tagger)
embeddings = generate_embeddings(lemmatized_paragraphs, model)
clusters = cluster_paragraphs(embeddings, lemmatized_paragraphs, max_clusters=2)
chunks = sentence_aware_japanese_chunking(paragraphs, clusters, page_numbers, max_words=100)

for chunk in chunks:
    print(f"クラスタ：{chunk['cluster']}、内容：{chunk['content']}")
```

### 特定のドメインのための微調整

特定のドメイン（例：法律、医療、技術）のドキュメントを扱う場合、以下のようにプロセスを微調整することができます：

1. 利用可能な場合は、ドメイン固有の埋め込みモデルを使用します。
2. ドメイン固有の用語を保持するように`clean_chunk`関数を調整します。
3. ドメイン固有の指示を含むようにLLMプロンプトを変更します。

法律文書のための`clean_chunk`関数の変更例：

```python
def clean_chunk_legal(text):
    # 法律固有のクリーニングルールを追加
    legal_terms = ['原告', '被告', '判決', 'plaintiff', 'defendant', 'verdict']
    for term in legal_terms:
        text = text.replace(f" {term} ", f" {term}")  # 法律用語が分割されないようにする
    # ... (残りのクリーニングプロセス)
    return text
```

### LLM要約

LLMベースの要約を使用するには、必要な環境変数を設定し、`llm_summarize=True`を設定する必要があります：

```python
import os
from dotenv import load_dotenv

load_dotenv()

# これらの環境変数が.envファイルに設定されていることを確認してください：
# MODEL_NAME
# IBM_CLOUD_URL
# IBM_CLOUD_API_KEY
# PROJECT_ID

chunks = chunker(pdf_paths, output_dir, raw_dir, processed_dir, embedding_model_name, max_words=1024, llm_summarize=True)
```

## トラブルシューティング

問題が発生した場合は、以下を試してみてください：

1. **埋め込みエラー**：`sentence-transformers`ライブラリの最新バージョンがインストールされていることを確認してください。
2. **MeCabエラー**：MeCabとその辞書が正しくインストールされ、アクセス可能であることを確認してください。
3. **メモリの問題**：大きなドキュメントの場合は、より小さなバッチで処理するか、システムのメモリを増やしてみてください。
4. **LLM処理エラー**：IBMクラウドの認証情報とネットワーク接続を確認してください。

## ライセンス

このプロジェクトはApache 2.0ライセンスの下で提供されています - 詳細はLICENSEファイルをご覧ください。

## 謝辞

- MeCab、Janome、Sentence Transformersライブラリの開発者の皆様に感謝いたします。
- LLM機能を提供していただいたIBM Watsonxチームに特別な感謝を申し上げます。