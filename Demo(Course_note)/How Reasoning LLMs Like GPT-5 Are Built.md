---
title: "How Reasoning LLMs Like GPT-5 Are Built 課程筆記"
date: 2026-04-18
transcript: "How Reasoning LLMs Like GPT-5 Are Built.md"
pdf: "無"
---

### [00:00:00-00:02:11] 什麼是 Reasoning LLM 與近期發展背景
- **主題介紹**：<font color="#4A86E8">Reasoning LLM (推理型大型語言模型)</font> 驅動了現代最先進的聊天機器人 (如 GPT-5)，本次將探討何謂 Reasoning LLM、建立模型的推論期與訓練期技術，以及 GPT-5 統一系統的可能架構。
- **歷史發展背景**：在 2022 到 2024 年間，標準的非推理 LLM (如 GPT-3、GPT-4、Llama 家族、Gemini) 取得了巨大的成功。
- **重大突破點 (2024年9月)**：OpenAI 發布了 <font color="#4A86E8">o1 model</font>，並將其定位為**一個懂得思考的模型**。
    - **核心特性**：這是一個新的 AI 模型系列，其設計目的是在給出回應前，會**花費更多時間進行思考**。
    - **基準測試表現 (Eval)**：在 AIME (美國數學奧林匹亞)、Codeforces (競技程式設計)、以及 PhD 級別的科學問題測試上，**o1 的準確率大幅超越了當時的非推理模型 GPT-4o**。
- **2025 年的推理模型浪潮**：繼 o1 之後，各家科技巨頭與團隊相繼釋出強大的推理模型，知名範例包含：Claude、Gemini 2.5 Pro、GPT-5 以及 DeepSeek R1。
    - 講者引用網路迷因總結：2024 年是**非推理模型**的天下，而到了 2025 年則湧現了大量在各項基準測試上表現優異的**強大推理模型**。
- #### 💡 深度補充：OpenAI o1 模型的影響
    - OpenAI o1 的推出標誌著 AI 發展從「系統一」(直覺、快速反應) 轉向「系統二」(緩慢、深度邏輯思考) 的重大典範轉移。o1 模型在內部使用了強化學習 (RL) 來自我探索思考路徑，這也是為何它在 AIME 這類需要深層邏輯推演的數學競賽中能取得驚人成績的原因。

### [00:02:11-00:04:13] 推理 (Reasoning) 的定義與在 LLM 中的應用
- **認知心理學的定義**：推理是**基於現有資訊得出結論的過程**。
- **推理的多種形式**：
    - <font color="#4A86E8">常識推理 (Common Sense Reasoning)</font>：例如回答「人會戴太陽眼鏡嗎？」這類生活常識。
    - <font color="#4A86E8">數學推理 (Mathematical Reasoning)</font>：面對數學題目時，需要進行**多步驟 (Multi-step)** 的推導來解題。
    - 其他形式還包含：多跳推理 (Multi-hop)、邏輯推理 (Logical)、以及溯因推理 (Abductive) 等。
- **LLM 是否具備推理能力的爭議**：產業界對於 LLM 是否具備「真正的推理」存在許多爭論，因此**如何在 AI 領域中給予推理一個精確的定義**變得至關重要。
- **Google DeepMind Denny Zhou 的權威定義**：
    - 在 LLM 領域中，推理被定義為：**在「問題」與「最終答案」之間，存在著 <font color="#4A86E8">中間標記 (Intermediate Tokens)</font>**。
    - #### (Concept: 中間標記 Intermediate Tokens)
        - 白話文解釋：就像人類解數學題時寫在計算紙上的草稿。模型不會立刻給出答案，而是先輸出一段用來自我推導的隱藏文字，這段文字就是中間標記。
- **兩種模型的運作流程比較**：
    - **非推理 LLM (Non-reasoning LLM)**：問題輸入後，經過**快速的單次傳遞 (Quick single pass)**，直接產出最終答案。
    - **推理 LLM (Reasoning LLM)**：問題輸入後，模型會**先生成一系列的中間標記 (中間步驟)**，推導完成後才產出最終答案。
- #### 💡 深度補充：Denny Zhou 與中間標記的數學理論
    - Denny Zhou (Google DeepMind 推理團隊負責人) 在 ICLR 2024 的研究中從理論上證明了：只要允許 Transformer 生成足夠數量的「中間標記」，即使是固定深度的模型，也能解決任何複雜的邏輯問題。這說明了「中間標記」能將複雜計算分攤到序列步驟中，實現了**「以時間換取深度」**的計算力飛躍。

### [00:04:13-00:07:14] Reasoning LLM 的實際操作範例與模型透明度
- **實驗平台與設定**：講者使用 Hyperbolic 平台 (可運行並測試各種開源模型) 進行推理與非推理模型的實際比較。
- **非推理模型範例 (使用開源 Llama 模型)**：
    - **測試提示詞**：「我剛學 AI 覺得很有趣，如何能在一年內贏得圖靈獎 (Turing Award)？」
    - **模型反應**：接收問題後**立刻開始生成回答**，給出了一個包含第 1 到 12 個月的極度不切實際的學習計畫。
    - **解析**：模型雖然把任務拆解成小塊，但它**並沒有進行思考 (Not really thinking)**，也沒有產生中間標記來評估這個目標的荒謬性。
- **推理模型範例 (使用開源的 <font color="#4A86E8">DeepSeek R1</font>)**：
    - **測試條件**：使用完全相同的提示詞與最大標記數限制。
    - **模型反應**：畫面上出現了可點擊的**推理追蹤 (Reasoning traces)** 區塊。
    - **內部思考過程 (Thinking)**：模型生成的思考標記顯示：「用戶聽起來對發現 AI 感到興奮，深入來看，他們可能根本不在乎獎項本身...」。模型試圖理解用戶真實意圖，而非盲目給出一年計畫。
    - **最終輸出**：直到模型完成內部思考並**感到有信心回答 (Feels confident to answer)** 時，才開始產出最終答案。
- **模型思維透明度的差異**：
    - **完全可見**：如 DeepSeek R1 這種開源模型，會向使用者展示**確切的思考過程**。
    - **部分隱藏**：如 OpenAI 的推理模型 (o1 系列)，出於安全或商業考量，並不展示原始推理軌跡，而是提供一個**思考過程的重寫或摘要 (Rewrite/Summary)**。
- #### 💡 深度補充：DeepSeek R1 與思維鏈透明化
    - DeepSeek R1 是 2025 年初極具代表性的開源推理模型，其最大的貢獻在於證明了透過純強化學習 (RL) 也能激發出強大的自我反思與長思維鏈 (Long CoT) 能力，且對外完全公開思維軌跡，這對 AI 領域研究模型的可解釋性 (Interpretability) 提供了極大的幫助。

### [00:07:14-00:09:43] 推理模型的效能霸權與兩大建構技術分類
- **效能表現與盲測排行榜**：
    - 講者展示了來自 LMSYS Chatbot Arena (影片中語音辨識誤植為 El Marina) 平台的排行榜截圖。該平台透過使用者進行配對比較 (Pairwise comparisons) 來評估 LLM。
    - <font color="#E06666">關鍵數據</font>：目前排行榜的**前段班已完全被推理模型統治**。
    - **頂尖模型陣容**：並列第一梯隊的模型包含 Gemini 2.5、GPT-5 High 以及 Claude Opus 4.1。
    - 第一個**非推理模型甚至只能排到第四名或第五名**，這充分展現了推理模型在當今 AI 發展中的重要性與主導力量。
    - #### (Concept: LMSYS Chatbot Arena)
        - 白話文解釋：這就像是 AI 界的「蒙眼試吃大會」。使用者發送同一個問題給兩個匿名的 AI 模型，然後投票選出哪個回答更好，藉此計算出各個模型的真實 Elo 積分排名。
- **建立 Reasoning LLM 的兩大技術分類**：
    - 要讓 LLM 學會推理，現行技術可歸納為兩個主要的大方向：
    - <font color="#6AA84F">推論期技術 (Inference-time Techniques)</font>：
        - **核心概念**：**保持原始非推理 LLM 的參數不變 (Frozen LLM)**。
        - **運作方式**：在模型外部加入額外的模組或演算法，引導這個未經修改的模型去生成中間標記。
        - **效果**：透過外部機制的輔助，讓整個系統在接收輸入到輸出答案的過程中，**表現得像是一個推理過程**。
    - <font color="#6AA84F">訓練期技術 (Training-time Techniques)</font>：
        - **核心概念**：使用訓練演算法與專門的「推理資料 (Reasoning data)」，對非推理 LLM 進行**持續微調 (Continue fine-tuning)**。
        - **運作方式**：經過訓練後，產出的將是一個**真正內化推理能力**的 Reasoning LLM。
        - **效果**：在使用模型時，不再需要依賴外部的額外模組，模型本身接收提示詞後，就能自主輸出**「中間標記 $\rightarrow$ 最終答案」**的結構。
- #### 💡 深度補充：推論期計算 (Test-Time Compute) 的崛起
    - 推論期技術的興起代表了 AI 縮放定律 (Scaling Laws) 的轉變。過去我們專注於投入大量算力在「預訓練」階段；現在業界發現，如果在模型生成答案時 (即推論階段) 給予它更多的計算資源 (Test-Time Compute) 讓它搜尋、反思與驗證，模型便能夠解開原先無法解決的極度複雜難題，這也是當今各家 AI 巨頭大力投資的核心技術路線。

---

### [00:09:44-00:17:13] 推論期技術 (Inference-time Techniques)

- **推論期技術的核心基礎**：
  - 核心特徵在於保持原始模型的參數**完全不變**，也就是維持一個<font color="#4A86E8">凍結的非推論模型 (Frozen Non-reasoning LLM)</font>。
  - 透過外掛不同的模組與演算法，強制或引導模型生成**中間預測標記 (Intermediate Tokens)**，使得整體的輸出流程「表現得像」是一個推論過程。
  - 講者在此段落詳細介紹了四種主流的推論期技術。
- **技術一：提示工程 (Prompting)**
  - 運作機制：在輸入端增加一個<font color="#4A86E8">提示工程模組</font>，利用精心設計的提示詞迫使模型思考。
  - 實務作法 1：**少樣本思維鏈提示 (Few-shot Chain of Thought, Few-shot CoT)**
    - 做法：在提示詞中提供包含**完整推論軌跡 (Reasoning Traces)** 的範例給模型參考。
    - 具體案例：給定一個數學題目（例如：3個紅袋子，每個裝5顆蘋果...），在提示詞中先寫出範例解法，明確包含中間計算過程（如 `Answer 2 * 3 = 6. So final answer is 6`）。
    - 預期效果：非推論模型會嘗試**精準模仿**範例的樣板結構。當遇到新問題時，模型會先產出中間推論步驟，並使用與範例完全一致的格式（例如：`So, final answer is 29`）來總結答案。
  - 實務作法 2：**零樣本思維鏈提示 (Zero-shot CoT)**
    - 做法：不需要提供完整範例，僅在使用者原本的提示詞末尾加上一句極簡的咒語：「**讓我們一步一步來思考 (Let's think step by step)**」。
    - 預期效果：單憑這句話就能有效推動模型將複雜任務拆解成數個較小的中間步驟來逐步求解。
  - #### (Concept: Chain of Thought, CoT)
    思維鏈 (CoT) 就像是規定學生在數學考試時「必須寫下完整計算過程」。如果只要求答案，學生（模型）可能會憑直覺瞎猜；但一旦被要求寫出步驟，大腦（神經網路）就會被迫一步步推導，從而大幅降低最終結論的錯誤率。
  - #### 💡 深度補充：
    - **Zero-shot CoT 的學術震撼**：此概念源於 Kojima 等人發表的《Large Language Models are Zero-Shot Reasoners》。這項發現震驚了學界，因為它證明了大型語言模型內部其實早就具備了潛在的推論能力，只需要一句簡單的提示就能將其「喚醒」，大幅省去了人工標註 Few-shot 範例的昂貴成本。
- **技術二：循序修正 (Sequential Revision)**
  - 運作機制：反覆利用**同一個 LLM** 對其自身的輸出進行**多次精煉與修改**。
  - 執行流程：
    - 步驟 1：將初始提示詞丟給 LLM 產生第一版的初步回答。
    - 步驟 2：將這個初步回答，連同新的輔助指令（例如：「**評估此回答並加以改善 (evaluate this response and improve it)**」）再次回傳給原模型。
    - 步驟 3：將上述修正過程重複執行一個**固定的迭代次數 (fixed number of iterations)**。
    - 步驟 4：迭代終止後，挑選出品質最高的回應作為最終輸出。
  - <font color="#6AA84F">正面效益</font>：建立自我反思的迴圈，讓模型能循序漸進地思考並糾正早期的邏輯謬誤。
- **技術三：N 中選優 (Best of $N$)**
  - 運作機制：針對同一個提示詞，讓 LLM 平行地進行 $N$ 次抽樣 (Sample $N$ times in parallel)，產生 $N$ 個獨立的解答路線，最後從中篩選出最優解。
  - 關鍵元件：必須外掛一個 <font color="#4A86E8">選擇器 (Selector)</font> 來檢視並裁決所有生成的候選回答。
  - 選擇器的實作方式：
    - **獨立機器學習模型**：例如訓練一個專職評分的<font color="#4A86E8">獎勵模型 (Reward Model)</font>。
    - **簡單啟發式規則 (Heuristics)**：最經典的應用為**多數決 (Majority Voting)**，特別適用於有標準答案的學科。
  - 實際運作案例（數學題）：
    - 在提示詞加入 `let's think step by step`。
    - 從模型中平行抽樣出 3 個不同的推論解法，假設得到的最終數字分別為：29, 28, 29。
    - 選擇器 (採用多數決) 統計後發現有 <font color="#E06666">大多數 (Majority)</font> 的回答指向 29，因此判定 29 為最終正確答案。
- **技術四：針對驗證器進行搜尋 (Search Against a Verifier)**
  - 運作機制：超越單純的隨機抽樣，結合了**搜尋演算法 (Search Algorithm)**、**LLM** 與**驗證器 (Verifier)**，在龐大的解空間中進行系統化探索。
  - 關鍵元件 1：**驗證器 (Verifier)**
    - 定義：一個獨立訓練的輔助型機器學習模型。
    - 任務：專門針對 LLM 生成的**完整解答**或**部分解答 (Partial solutions / Sequence of thoughts)** 給予評分，分數代表該推論步驟的品質或正確機率。
  - 關鍵元件 2：**搜尋演算法 (Search Algorithm)**
    - 依賴驗證器的評分回饋來決定下一步的探索方向，講者列舉了以下幾種演算法：
      - 前述的 **Best of $N$**：生成 $N$ 個解答 $\rightarrow$ 驗證器全部評分 $\rightarrow$ 挑最高分。
      - **波束搜尋 (Beam Search)**：將解題過程視為動態建構的樹狀圖，在推論的每一個中間步驟就將「部分解答」交給驗證器評分。根據分數，演算法會果斷**修剪 (Prune)** 掉低分的錯誤分支，並集中資源**探索 (Explore)** 高分潛力分支。
      - **前瞻搜尋 (Look-ahead Search)**。
      - **蒙地卡羅樹搜尋 (Monte Carlo Search)**。
  - #### (Concept: Verifier & Tree Search)
    可以把 LLM 想像成在巨大迷宮中找出口的人，而 Verifier 是他手上的「危險探測器」。每走到一個岔路（生成部分解答），探測器會評估這條路的存活率（給出分數）。波束搜尋 (Beam Search) 就是同時派出一小隊人馬，根據探測器的分數，立刻放棄死胡同（修剪分支），把人力集中在看似正確的道路上（探索分支），極大地提高了找到正確出口的效率。
  - #### 💡 深度補充：
    - **AlphaGo 的核心靈魂**：此段落提到的 Monte Carlo Search 與 Verifier 的結合，正是當年 DeepMind 擊敗李世乭的 AlphaGo 的核心架構。在當代頂尖的 Reasoning LLM（例如 OpenAI o1 或 DeepSeek R1）中，模型將文字推理過程視為下棋，並利用強化學習訓練出的 Verifier (類似 AlphaGo 的 Value Network) 來動態評估當下「文字盤面」的正確率，這是目前 AI 展現出驚人邏輯能力的關鍵底層技術。
- **段落總結：推論期技術的架構演進**
  - **非推論模式**：輸入 $\rightarrow$ 瞬間給出最終輸出。
  - **提示工程 (Prompting)**：輸入 $\rightarrow$ 強制生成一連串思考軌跡 $\rightarrow$ 給出最終輸出。
  - **Best of $N$**：輸入 $\rightarrow$ 平行產出多條解題路線 $\rightarrow$ 透過選擇器決定勝負 $\rightarrow$ 給出最終輸出。
  - **驗證器搜尋 (Search + Verifier)**：輸入 $\rightarrow$ 建構動態解答樹 $\rightarrow$ 透過驗證器即時探索與修剪 $\rightarrow$ 直到抵達具備高信心的解答分支作為最終輸出。

---

## [00:17:14-00:22:19] 訓練期技術 (Training-time Techniques)
- **核心概念**：透過**持續訓練**（Continue Training）原有的基礎模型（Base LLM），將其直接轉化為內建推理能力的 <font color="#4A86E8">Reasoning LLM</font>。
- 講者將訓練期技術主要歸納為四大流派：
  ### [00:17:31-00:18:37] 技術一：監督式微調 (Supervised Fine-Tuning, SFT)
  - **運作機制**：將不具備推理能力的模型，使用包含思考過程的資料集進行微調。
  - **資料格式**：使用 <font color="#4A86E8">Chain of Thought (CoT) Data</font>，其結構為嚴格對應的「**問題 (Problem) -> 思考序列 (Sequence of Thoughts / Rationale) -> 最終答案 (Final Answer)**」。
  - **經典案例與文獻**：<font color="#4A86E8">STaR (Self-Taught Reasoner)</font> 模型。
    - 該研究展示如何利用基礎模型自身來收集 CoT 資料，透過將格式設定為 Question -> Rationale -> Answer 進行自我迭代。
    - **訓練策略**：採用 <font color="#6AA84F">Iterative Bootstrapping (迭代拔靴法)</font>，讓模型不斷自我生成更好的 CoT 資料並反覆訓練，進而逐步且穩健地提升推理能力。
  #### (Concept: Supervised Fine-Tuning 與 Bootstrapping)
  SFT 就像是給學生大量的「標準詳解」，讓學生模仿解題步驟；而 Bootstrapping 則是讓學生先試著寫詳解，挑出寫得對的再拿來當作下一輪的教材，實現**左腳踩右腳**的自我提升。
  #### 💡 深度補充：
  STaR (Self-Taught Reasoner) 是由 Stanford 與 Google 研究人員提出的框架。其核心精神在於打破「需要大量人類標註的思考過程」這個瓶頸。當模型給出錯誤答案時，STaR 會給予正確提示（Hint）促使模型重新生成正確的推導過程，這樣能極大化利用失敗的嘗試，是建構高品質推理資料集的基準技術。
  ### [00:18:38-00:20:09] 技術二：結合驗證器的強化學習 (Reinforcement Learning with a Verifier)
  - **運作機制**：在 SFT 階段之後，讓模型進入「**實戰演練 (Practice)**」階段，要求模型針對同一提示詞生成多種不同的思考路徑。
  - **驗證器 (Verifier) 介入**：透過一個獨立訓練的 <font color="#4A86E8">Verifier</font> 來評估這些中間回覆並給予嚴格分數。
  - **權重更新**：使用 <font color="#4A86E8">強化學習 (RL) 演算法</font> 依據分數更新模型參數，**強烈鼓勵**生成高分答案，並對 <font color="#E06666">Verifier 判定為劣質的回覆進行懲罰與勸退 (Discouraged)</font>。
  - **兩種主流驗證器架構**：
    - <font color="#4A86E8">結果監督獎勵模型 (Outcome-supervised Reward Model, ORM)</font>：僅針對**整套解決方案**（包含所有中間思考與最終答案）給予一次性的總體評分。
    - <font color="#4A86E8">過程監督獎勵模型 (Process-supervised Reward Model, PRM)</font>：會針對推導過程中的**每一個獨立思考步驟**分別進行細密評分。
  - **經典案例與文獻**：OpenAI 發表的指標性論文 <font color="#6AA84F">《Let's Verify Step by Step》</font>。
  #### (Concept: ORM vs PRM)
  ORM 就像是「只看期末考最終答案給分的老師」，對錯一翻兩瞪眼；PRM 則是「會看計算過程給部分給分的老師」，即使最後粗心算錯，前面的正確邏輯依然會得到肯定。這能有效避免模型「用錯誤的邏輯瞎猜對答案」。
  #### 💡 深度補充：
  OpenAI 的《Let's Verify Step by Step》論文中強烈證明了 PRM 的優越性。PRM 不僅能提供更密集的獎勵訊號（Dense Reward Signal），還能顯著減少模型產生 <font color="#E06666">幻覺 (Hallucination)</font> 與 <font color="#E06666">Reward Hacking (作弊刷分)</font> 的現象，這正是目前訓練頂尖推理模型（如 OpenAI o1 系列）的核心基石。
  ### [00:20:10-00:21:11] 技術三：自我修正 (Self-Correction)
  - **運作機制**：專門訓練模型學會發現自身錯誤並**主動自我修正**的能力。訓練後的模型在給出初步輸出後，能自主進行二次甚至多次的檢視與修正。
  - **資料準備**：蒐集大量的 <font color="#4A86E8">修訂資料 (Revision Data)</font>，這是一系列由「<font color="#E06666">錯誤答案序列 -> 最終正確答案</font>」所組成的完整歷程記錄。
  - **訓練方式**：
    - 可直接使用上述修訂資料進行基礎的 SFT。
    - 也可以進階結合**強化學習 (RL)** 來專門且針對性地強化此修正能力。
  - **經典案例與文獻**：Google DeepMind 提出的 <font color="#4A86E8">SCoRe (Self-Correction via Reinforcement Learning)</font> 演算法。
  #### (Concept: Revision Data 與 Self-Correction)
  這好比訓練學生不要只寫出第一直覺的答案，而是要具備「考後檢查考卷」的能力。修訂資料就是讓模型看懂「從寫錯、發現錯誤、到擦掉重寫出正確答案」的心路歷程。
  #### 💡 深度補充：
  過去的研究表明，未經特殊訓練的 LLM 其實**非常不擅長自我修正**，往往會在修正過程中把原本對的改成錯的（能力退化現象）。DeepMind 的 SCoRe 論文透過多回合的 RL 訓練，強制模型在第一階段生成嘗試性答案，第二階段進行嚴格自我批判，成功克服了傳統模型遇到修正提示時容易產生的 Mode Collapse（模式崩潰）問題。
  ### [00:21:12-00:22:19] 技術四：內化搜尋 (Internalize Search)
  - **運作機制**：這是目前**最進階且複雜**的技術。目標是將推論期的外部搜尋過程（例如：探索不同分支、回溯）直接**固化並內化**到模型的參數中。
  - **資料生成過程**：
    - 首先，利用上一節提到的**推論期技術 (Inference-time Techniques)** 讓模型進行大量採樣，探索出各種解決方案的分支。
    - 完整記錄下模型**探索方向、反思 (Reflect)、回溯 (Backtrack) 到重新生成**的整個搜尋樹軌跡（Search Tree Trajectory）。
  - **訓練方式**：一旦蒐集到這些包含「搜尋軌跡」的豐沛資料，後續的訓練過程就與標準的 SFT 或 CoT 訓練完全相同。
  - **最終效果**：經過此訓練的模型能自主展現出動態探索與回溯的行為，完全無需依賴外部龐雜的搜尋演算法介入。
  - **經典案例與文獻**：學界的 <font color="#4A86E8">MetaCoT</font> 以及 <font color="#4A86E8">Journey Learning</font> 論文。
  #### (Concept: Internalize Search)
  如果「推論期搜尋」是考試時拿計算紙瘋狂試錯（極度依賴外部工具與運算時間）；「內化搜尋」就是把計算紙上的試錯過程全部背進腦海裡，變成直覺反應。模型真正學會了「此路不通，退回上一步」的思維模式。
  #### 💡 深度補充：
  這種技術將立體的 Search Tree 降維轉換為 Sequence Data 餵給模型。以 Journey Learning 為例，它不僅教模型最終的 Shortest Path（最佳捷徑），更把「探索死胡同後走出來的完整旅程 (Journey)」全部教給模型。這能大幅降低推論期使用 MCTS（蒙地卡羅樹搜尋）等外部演算法所帶來的巨大延遲，是打造如 DeepSeek-R1 或 OpenAI o1 這種能「深思熟慮」模型的終極聖杯。

---

### [00:22:20-00:27:31] GPT-5 統一系統架構與實務解析
- **GPT-5 系統架構揭密**
  - OpenAI 釋出長達 <font color="#E06666">50 頁</font> 的 `GPT-5 System Card`，內容多著墨於**評估 (Evaluation)** 與**安全機制 (Safety Mechanisms)**，並未具體公開參數數量或底層架構細節。
  - **核心組成**：GPT-5 統一系統由**兩個主要模型**與**一個路由元件**構成：
    - <font color="#4A86E8">GPT-5 Main</font>：**運算效率高**且**成本較低**的主模型，但屬於非推論 (Non-reasoning) 模型，無法進行深度思考。
    - <font color="#4A86E8">GPT-5 Thinking</font>：具備完整推理能力的**思考模型**。講者推測其訓練極可能採用了監督式微調 (SFT)、結合驗證器的強化學習 (RL with verifier)，以及內部化搜尋 (Internalizing Search) 等訓練期技術。
    - <font color="#4A86E8">Fast Router</font> (快速路由器)：運行速度極快且成本極低的元件，部署於雙模型之前。當接收到 Prompt 時，由其**動態決定**將任務分配給哪個模型。
      - **應用範例**：若詢問「某國家的首都在哪？」，由於問題單純，Router 會將其指派給 <font color="#6AA84F">GPT-5 Main</font> 以節省資源。
  - #### (Concept: 路由器 Router)
    路由器就像是一間大公司的「總機」，會初步判斷客戶(使用者)的問題難度。如果是簡單的常見問題，就轉接給基層客服 (Main) 快速解決；如果是牽涉複雜邏輯或運算的專案，就轉交給資深工程師 (Thinking) 慢慢處理，以此達到**效能與成本的最佳化**。
  - #### 💡 深度補充：大語言模型的路由機制 (LLM Routing)
    在業界實務中，Routing 機制已成為降低推論成本 (Inference Cost) 的標準做法。通常路由器本身是一個極小的分類模型 (例如 BERT 級別或更小的分類器)，它只需計算輸入句子的語義特徵，預測解決該問題所需的「算力閾值」。這使得系統能在大規模併發情況下，將大部分的日常對話交由小模型處理，僅在關鍵時刻自動調用昂貴的推理模型。
- **安全機制的典範轉移：從「拒絕」到「安全補全」**
  - **傳統做法 (GPT-5 之前)**：採用<font color="#4A86E8">意圖分類 (Intent Classification)</font>，在輸入階段進行二元分類。若判定使用者意圖不安全，模型會直接觸發 <font color="#E06666">硬拒絕 (Hard Refusal)</font>。
  - **GPT-5 的創新**：將重心轉移至 <font color="#6AA84F">Safe Completions (安全補全)</font>。
  - **運作差異**：不再執著於過濾輸入的安全性，而是**專注優化輸出結果**。即使使用者的意圖存在模糊空間，模型也會盡力產出**安全且具備幫助性**的回答，大幅降低了傳統模型過度拒絕的問題。
  - #### (Concept: Safe Completions 安全補全)
    過去的安全機制像是一個「嚴格的門衛」，看到可疑的提示詞就直接擋在門外；而「安全補全」則像是一位「有經驗的公關」，不管你問的問題多敏感，他都能用專業、不踩紅線的安全方式回答你，確保對話不中斷。
  - #### 💡 深度補充：Safe Completions 的獎勵函數設計
    根據 OpenAI 的研究，Safe Completions 在強化學習階段透過全新的獎勵函數 $r = h \times s$ 來實現，其中 $h$ 代表幫助性 (Helpfulness)，$s$ 代表安全性 (Safety)。這種乘法機制鼓勵模型在絕對安全的範圍內，盡可能最大化任務完成度，有效解決了處理「雙重用途 (Dual-use)」問題時常見的系統死板反應（例如詢問化學反應被誤判為製造炸彈而遭拒絕）。
- **ChatGPT 介面模式與底層對應**
  - GPT-5 在 ChatGPT 的介面上提供了四種不同的操作模式，各自對應上述的底層系統架構：
    - `Instant`：強制僅使用 **GPT-5 Main**，不進行推論，適合日常快速對答。
    - `Thinking`：強制僅使用 **GPT-5 Thinking**，無視問題簡單與否，皆進行深度思考。
    - `Auto`：啟用 **Fast Router**，完全交由系統自動判斷最適合的模型。
    - `Pro (Thinking Pro Mode)`：啟用 <font color="#4A86E8">Test-time Compute (推論期算力)</font>。
      - **運作機制**：底層並未增加新的模型，而是讓思考模型套用推論期技術（如：自我一致性、循序修正、蒙地卡羅樹搜尋等）。
      - **核心優勢**：針對同一個 Prompt 同時**探索多種解決方案與方向**，透過內部評估後，最終只向使用者展示 <font color="#6AA84F">最佳解答</font>，專門用以解決極度複雜的難題。
  - #### (Concept: Test-time Compute 推論期算力)
    一般模式下，AI 看到題目就馬上寫下答案（一氣呵成）；開啟 Test-time Compute 後，就像 AI 獲准在考卷發下來後，先在計算紙上嘗試多種不同的解法，自己驗證哪一種是對的，最後才把最完美的那一種抄到答案卷上遞交給使用者。
  - #### 💡 深度補充：Test-time Compute (推論期算力) 的 Scaling Law
    近年 AI 領域發現，除了擴展模型訓練期的參數與資料量能讓模型變強之外，**給予模型更多思考時間 (Test-time compute)** 也能顯著提升能力。GPT-5 Pro 模式正是運用強化學習配合搜尋演算法，讓模型在產生最終輸出前，在潛藏空間中進行大量的模擬、修剪與回溯，從而在數學和程式競賽中達到遠超原始模型的卓越表現。
