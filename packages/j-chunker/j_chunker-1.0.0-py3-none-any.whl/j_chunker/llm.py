# SPDX-License-Identifier: Apache-2.0

# Standard
import os
from functools import lru_cache

# Third Party
from dotenv import load_dotenv
from langchain_ibm import WatsonxLLM
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams

load_dotenv()

@lru_cache(maxsize=1)
def initialize_model(decoding_method="greedy", max_new_tokens=1024, min_new_tokens=10, temperature=0, top_k=25, top_p=1, stop_words=["\n\n\n"]):
    """
    Initialize and return a WatsonxLLM model with specified parameters.

    Args:
        decoding_method (str, optional): Method used for decoding. Defaults to "greedy".
        max_new_tokens (int, optional): Maximum number of new tokens to generate. Defaults to 1024.
        min_new_tokens (int, optional): Minimum number of new tokens to generate. Defaults to 10.
        temperature (float, optional): Sampling temperature. Defaults to 0.
        top_k (int, optional): Number of top tokens to consider for sampling. Defaults to 25.
        top_p (float, optional): Cumulative probability threshold for top-p sampling. Defaults to 1.
        stop_words (list, optional): List of stop words to end generation. Defaults to ["\n\n\n"].

    Returns:
        WatsonxLLM: Initialized WatsonxLLM model.
    """
    model_id = os.getenv("MODEL_NAME")
    url = os.getenv("IBM_CLOUD_URL")
    api_key = os.getenv("IBM_CLOUD_API_KEY")
    project_id = os.getenv("PROJECT_ID")

    params = {
        GenParams.DECODING_METHOD: decoding_method,
        GenParams.MIN_NEW_TOKENS: min_new_tokens,
        GenParams.MAX_NEW_TOKENS: max_new_tokens,
        GenParams.TEMPERATURE: temperature,
        GenParams.TOP_K: top_k,
        GenParams.TOP_P: top_p,
        GenParams.STOP_SEQUENCES: stop_words
    }

    llm = WatsonxLLM(
        model_id=model_id,
        url=url,
        apikey=api_key,
        project_id=project_id,
        params=params,
    )

    return llm

def verify_translation(translated_text, llm):
    prompt = f"""
    <|begin_of_text|>
    <|start_header_id|>system<|end_header_id|>
    As a professional Japanese proofreader and editor, your task is to verify and clean up the following translated text. Please adhere to these guidelines:

    1. Remove any translator's Notes, Comments, or Explanations present in the text.
    2. Ensure the text is properly formatted and punctuated. Make sure to convert any other language if present into japanese.
    3. Do not add any new information or explanatory notes.
    4. Return only the verified and cleaned-up Japanese text without any comments and explainatory notes.
    5. Stop generating once the cleaned-up text is complete. Do not add any explanations or notes after the Japanese text.
    6. The cleaned-up text will be used in production environment so make sure to be accurate to the point. Else you will be penalized heavily.

    Here are some examples:

    Example 1:
    Input:
    プロジェクトマネージャーの重要なスキルには以下があります：
    1. コミュニケーション能力
    2. リーダーシップ
    3. 問題解決能力
    4. 時間管理
    （注：「時間管理」は「タイムマネジメント」とも呼ばれます）

    Output:
    プロジェクトマネージャーの重要なスキルには以下があります：
    1. コミュニケーション能力
    2. リーダーシップ
    3. 問題解決能力
    4. 時間管理

    Example 2:
    Input:
    日本の四季：
    1. 春（3月～5月）：桜の季節 (Note: Cherry blossoms are called "sakura" in Japanese)
    2. 夏（6月～8月）：暑く湿度が高い
    3. 秋（9月～11月）：紅葉が美しい (Translator's note: "Koyo" means autumn foliage)
    4. 冬（12月～2月）：寒く、一部地域では雪が降る

    Output:
    日本の四季：
    1. 春（3月～5月）：桜の季節
    2. 夏（6月～8月）：暑く湿度が高い
    3. 秋（9月～11月）：紅葉が美しい
    4. 冬（12月～2月）：寒く、一部地域では雪が降る

    Example 3 (Handling repetitive content and hallucinations):
    Input:
    日本の主要な都市には以下があります：
    1. 東京：日本の首都東京、東京、東京、東京、東京、東京、東京、東京、東京、東京
    2. 大阪：関西地方の中心都市大阪、大阪、大阪、大阪、大阪、大阪、大阪、大阪、大阪
    3. 名古屋：中部地方の主要都市名古屋、名古屋、名古屋、名古屋、名古屋、名古屋、名古屋
    4. 福岡：九州地方の中心都市福岡、福岡、福岡、福岡、福岡、福岡、福岡、福岡、福岡
    5. 札幌：北海道の中心都市札幌、札幌、札幌、札幌、札幌、札幌、札幌、札幌、札幌
    6. 神戸：兵庫県の代表的な都市神戸、神戸、神戸、神戸、神戸、神戸、神戸、神戸、神戸
    7. 京都：古都として有名な京都、京都、京都、京都、京都、京都、京都、京都、京都、京都

    Output:
    日本の主要な都市には以下があります：
    1. 東京：日本の首都
    2. 大阪：関西地方の中心都市
    3. 名古屋：中部地方の主要都市
    4. 福岡：九州地方の中心都市
    5. 札幌：北海道の中心都市
    6. 神戸：兵庫県の代表的な都市
    7. 京都：古都として有名
    <|eom_id|>

    <|start_header_id|>user<|end_header_id|>
    Here's the text to verify and clean up:

    {translated_text}
    <|eom_id|>

    <|start_header_id|>assistant<|end_header_id|>
    """
    result = str(llm.invoke(prompt)).strip()
    return result

def process_chunk_with_llm(chunk, llm, max_words):
    """
    Process a single chunk of text using the LLM for proofreading and cleaning.

    Args:
        chunk (dict): Dictionary containing chunk information.
        llm (WatsonxLLM): Initialized WatsonxLLM model.
        max_words (int): Maximum number of words for the summary.

    Returns:
        dict: Processed and cleaned chunk information.
    """
    prompt = f"""
    <|begin_of_text|>
    <|start_header_id|>system<|end_header_id|>
    You are a Japanese document processing expert with exceptional skills in understanding and organizing text chunks extracted from PDFs. Your task is to process the following text chunk and extract meaningful and contextual information from it.

    Instructions:
    1. Carefully analyze the information in the chunk and grasp the main content and concepts.
    2. Ignore unnecessary symbols, page numbers, headers, footers, or other non-essential elements.
    3. Create meaningful and complete sentences while maintaining context.
    4. Appropriately complete abbreviated information or incomplete sentences based on context.
    5. Retain technical terms and abbreviations when possible.
    6. Convert bullet points or numbered lists into sentence form, unless the list structure is essential.
    7. Summarize and include any explanations of tables or graphs if present.
    8. Appropriately translate any English parts into Japanese, considering the context.
    9. Please summarize the following text chunk into approximately {max_words} words or less, providing the most important and contextual information in Japanese.
    10. Strive to retain all important information from the original chunk.
    11. If multiple topics are present in the chunk, organize them logically.
    12. Recognize the type of document (e.g., legal document, technical manual, academic paper) and use appropriate style and terminology.
    13. Observe that in the chunk if there are numbers or explanations of calculations, you should retain all the data and if possible give more detailed explanations of the calculations.

    Please process the following text chunk and provide organized, meaningful, and contextual information in Japanese, following the above instructions:

    Examples of correct and incorrect outputs:

    Example 1:
    Input chunk:
    ```
    3. 個人情報保護法の概要
    ・個人情報の定義
    ・個人情報取扱事業者の義務
    ・本人の権利　　etc...

    4. マイナンバー法の概要
    ```

    Correct output:
    ```
    個人情報保護法の概要について説明します。この法律では、個人情報の定義が明確にされており、個人情報取扱事業者の義務が規定されています。また、本人の権利についても定められています。これらの要点に加え、その他の重要な側面も含まれています。

    続いて、マイナンバー法の概要について述べられています。
    ```

    Incorrect output:
    ```
    3. 個人情報保護法の概要
    ・個人情報の定義
    ・個人情報取扱事業者の義務
    ・本人の権利　　etc...

    4. マイナンバー法の概要

    個人情報保護法とマイナンバー法について書かれています。
    ```

    Explanation: The correct output converts the bullet points into a coherent paragraph, maintains all the important information, and indicates the transition to the next topic. The incorrect output merely repeats the input and adds a vague summary without providing any meaningful organization or context.

    Example 2:
    Input chunk:
    ```
    2.3 Data Analysis Results
    The t-test revealed a significant difference (p < 0.05) between Group A (M = 3.45, SD = 0.67) and Group B (M = 2.98, SD = 0.72).

    Fig. 1: Distribution of scores for Group A and Group B
    [A graph showing two bell curves with slight overlap]
    ```

    Correct output:
    ```
    データ分析の結果について説明します。t検定の結果、グループAとグループBの間に有意な差が見られました（p < 0.05）。グループAの平均値は3.45（標準偏差0.67）であり、グループBの平均値は2.98（標準偏差0.72）でした。

    また、図1にはグループAとグループBのスコア分布が示されています。この図からは、二つのグループの分布が若干重なっているものの、明確な差異が観察できることが分かります。
    ```

    Incorrect output:
    ```
    2.3 データ分析結果
    t検定で有意差あり（p < 0.05）。
    グループA（M = 3.45, SD = 0.67）
    グループB（M = 2.98, SD = 0.72）

    図1：グループAとグループBのスコア分布
    ```

    Explanation: The correct output translates the English terms, explains the statistical results in a complete sentence, and describes the graph's content. The incorrect output merely translates the headings and keeps the data in a list format without providing context or explanation.

    Example 3 (Demonstrating handling of numerical data and calculations):
    Input chunk:
    ```
    5.2 収益予測
    2023年度の予測売上高: 10億5000万円
    売上原価率: 65%
    営業利益率目標: 15%

    計算例:
    売上原価 = 10億5000万円 * 0.65 = 6億8250万円
    目標営業利益 = 10億5000万円 * 0.15 = 1億5750万円
    ```

    Correct output:
    ```
    2023年度の収益予測について説明します。予測売上高は10億5000万円と設定されており、売上原価率は65%、営業利益率の目標は15%と定められています。

    これらの数値を基に具体的な計算を行うと、以下のようになります：

    1. 売上原価の計算:
    売上高の65%が売上原価となるため、
    10億5000万円 × 0.65 = 6億8250万円
    したがって、予測される売上原価は6億8250万円です。

    2. 目標営業利益の計算:
    売上高の15%を営業利益とすることが目標とされているため、
    10億5000万円 × 0.15 = 1億5750万円
    つまり、目標とする営業利益は1億5750万円となります。

    これらの計算結果から、売上高から売上原価と目標営業利益を差し引いた残りの約2億1000万円が、販売費及び一般管理費に充てられることが推測されます。
    ```

    Incorrect output:
    ```
    2023年の売上予測は10億5000万円です。
    売上原価は6億8250万円で、営業利益目標は1億5750万円です。
    ```

    Explanation: The correct output retains all the numerical data from the original chunk and provides a detailed explanation of the calculations. It also adds context by explaining what the remaining amount might represent. The incorrect output, while technically accurate, fails to show the calculation process and doesn't provide enough context or explanation for the figures presented.

    Please use these examples as a guide to process the given text chunk and provide a well-organized, contextual output in Japanese, paying special attention to the handling of numerical data and calculations.
    <|eom_id|>

    <|start_header_id|>user<|end_header_id|>
    Here's the text chunk to process:

    {chunk['content']}
    <|eom_id|>

    <|start_header_id|>assistant<|end_header_id|>
    """
    result = str(llm.invoke(prompt)).strip()
    verified_result = verify_translation(result, llm)

    return {
        'content': verified_result,
        "cluster": int(chunk['cluster']),
        'pages': chunk['pages']
    }