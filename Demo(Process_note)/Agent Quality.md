---
title: (重要) Agent Quality

---

:::info
怎麼做黑箱/玻璃箱評估、LLM judge、HITL、觀測三支柱（log/trace/metric）

[Agent Quality](https://www.youtube.com/watch?v=LFQRy-Ci-lk)
:::

## Agent Quality：從「評估」到「可觀測性」的完整落地框架（整合逐字稿＋白皮書）
### [00:00-00:51] 問題定義：為什麼「AI Agent 品質」是架構層級，而不是最後測試
- 核心痛點：AI Agent 具備非決定性（non-determinism），你無法像傳統軟體一樣用「固定規格＋固定測試」完全預測行為，因此「信任」變成工程問題而不是口號。[AQ-1]
- 白皮書把重點講得很硬：Agent quality 必須是 architectural pillar（架構支柱），不是 release 前的 QA 流程。[AQ-1]
#### (Concept: Non-determinism / 非決定性)
- 白話比喻：同一個問題丟給同一個 Agent，就像同一個人每天心情不同，會選不同路徑做事；你不能只驗收「最後交付物」，還要看「過程」有沒有亂撞、作弊、或差點出事。
#### 💡 深度補充：
- 「品質」在 AI 系統工程裡常被拆成 reliability / safety / robustness 等子目標；NIST 的 AI RMF 把「可信賴（trustworthy）」視為風險管理與治理的系統工程問題，而不是單點模型分數。[W7]

### [00:51-02:06] 三個核心訊息：Trajectory、Observability、Flywheel
- 訊息 1：The Trajectory is the Truth（軌跡才是真相）＝評估不能只看 final output，要看整段決策過程（包含推理、工具呼叫、回應解讀）。[AQ-1]
- 訊息 2：Observability is the Foundation（可觀測性是地基）＝你看不到過程，就不可能評估或除錯；白皮書把可觀測性拆成 Logs/Traces/Metrics 三支柱。[AQ-1]
- 訊息 3：Evaluation is a Continuous Loop（評估是持續迴圈）＝用 Agent Quality Flywheel 把「真實世界失敗」變成「回饋＋回歸測試」，一直滾動變強。[AQ-1]
#### (Concept: Trajectory / 軌跡)
- 白話比喻：你不能只看學生考卷最後答案對不對，還要看草稿推導過程；因為「猜對」可能代表風險很高（下次就爆）。
#### (Concept: Observability / 可觀測性)
- 白話比喻：監控（monitoring）像看「餐點有沒有準時出菜」；可觀測性像把廚房透明化，能追問「為什麼這一步這樣做」。[AQ-4]
#### 💡 深度補充：
- 在分散式系統裡，OpenTelemetry 把 signals（traces/metrics/logs）標準化，讓你能用 Trace ID/Span ID 把事件串成一條「因果故事線」。[W1][W2][W3]

### [02:06-04:23] 為什麼傳統測試壞掉：delivery truck vs F1 car + 失敗是「悄悄腐蝕信任」
- 類比：傳統軟體像 delivery truck（固定路線、固定檢查、crash 就是 fail）；Agent 像 F1（要在動態環境做細緻判斷），評估不能是 checklist，而要靠持續 telemetry（遙測資料）。[AQ-3]
- Agent 的失敗常是「表面成功」：API 回 200 OK、輸出看起來合理，但其實錯得很深，會慢慢侵蝕使用者信任（insidious failures）。[AQ-3]
- 白皮書列出典型 failure modes（比傳統 bug 更難抓）：[AQ-2]
  - Algorithmic Bias：把資料裡的系統性偏見「自動化＋放大」。
  - Factual Hallucination：很自信地編造不存在的事實/來源。
  - Performance & Concept Drift：世界變了、定義變了，Agent 還活在舊假設。
  - Emergent Unintended Behaviors：為了達成目標鑽規則漏洞、長出奇怪「迷信」策略。
#### (Concept: Hallucination / 幻覺)
- 白話比喻：像小朋友背書背一半，剩下自己編，還講得很肯定；最危險的是「聽起來像真的」。
#### 💡 深度補充：
- 「概念漂移（concept drift）」在風控/詐欺等領域很致命，因為攻擊手法會演化；所以你要有持續監測與回訓練/回饋機制，而不是一次性驗收。[AQ-2]
- TruthfulQA 是一個專門量測「模型是否傾向模仿人類錯誤迷思」的基準，提醒你：模型越大不一定越誠實，單靠 scaling 不保證 truthfulness。[W4]

### [04:23-06:15] 評估目標改變：Verification → Validation + 四大品質支柱（Four Pillars）
- 觀念翻轉：傳統 verification 問「有沒有照規格做對？」；Agent evaluation 要問 validation「有沒有做出對使用者有價值且可信的東西？」[AQ-3]
- 四大支柱（品質的座標系）：[AQ-5]
  - Effectiveness（有效性）：有沒有達成使用者真正意圖（連到 business KPI）。
  - Efficiency（效率）：資源消耗是否合理（tokens/cost、latency、步數、失敗 tool call 次數）。
  - Robustness（魯棒性）：遇到 API error、缺資料、模糊指令時，能否優雅處理（重試、澄清、誠實回報）。
  - Safety & Alignment（安全與對齊）：不可談判門檻（拒絕危險要求、抵抗 prompt injection、避免資料外洩）。
#### (Concept: Effectiveness vs Efficiency)
- 白話比喻：有效性＝你有沒有把作業做對；效率＝你是不是寫 25 頁廢話才得到 1 行正確答案（而且還很貴）。
#### (Concept: Robustness / 魯棒性)
- 白話比喻：遇到題目不清楚時，好的助教會先問清楚；爛的助教會硬猜，猜錯還裝懂。
#### 💡 深度補充：
- 安全層面不要只靠「最後輸出檢查」：prompt injection 是把惡意指令偽裝成正常輸入，誘導模型洩漏敏感資訊或做不該做的事。[W5][W6]
- OWASP GenAI Top 10 把 Prompt Injection 當成高風險類別，因為 LLM 天生把「資料」和「指令」混在同一條序列裡，很容易被混淆。[W6]

### [06:23-08:07] Outside-In 評估層級：先黑盒 End-to-End，再玻璃盒 Trajectory
- 策略：Outside-In hierarchy＝先看整體任務是否成功（Black Box），再打開看為什麼失敗（Glass Box）。[AQ-6]
- 黑盒（End-to-End）常用指標：Task success rate、User satisfaction（如 thumbs up/down、CSAT）、Overall quality/完整度。[AQ-6]
- 玻璃盒（Trajectory evaluation）要找 breakpoints：規劃（planning）錯？工具選錯/參數錯？工具回應解讀錯？RAG 抓到爛文件？步數過多/延遲過高？多 Agent 溝通打架？[AQ-7]
#### (Concept: Black Box vs Glass Box)
- 白話比喻：黑盒像只看考試分數；玻璃盒像看你的解題過程、哪一步開始歪掉。
#### 💡 深度補充：
- RAG（Retrieval-Augmented Generation）把「外部可更新知識庫」接到生成模型上，失敗來源因此變成兩段：retrieval 爛或 generation 爛；所以你必須評估 chunking/embedding/retriever/引用一致性，而不是只看最後字串像不像。[W8]
- RAG 原始論文強調結合 parametric memory（模型參數）與 non-parametric memory（檢索到的文件）來提升知識密集任務表現與可更新性。[W8]

### [07:35-08:07] ADK 實作技巧：把「成功軌跡」存成回歸測試（Eval Case）
- 實務 tip：在 ADK web UI 互動到一次「你很滿意的結果」，把該 session 存成 Eval Case（.test.json），鎖住 ground truth final_response，未來用 adk eval 或 pytest 做 regression test，防止品質倒退。[AQ-6]
- 重點：存的不只是最後答案，還包含工具呼叫序列（trajectory），所以能抓到「答案看似還行，但路徑變爛/變危險」的退化。[AQ-6]
#### (Concept: Regression test / 回歸測試)
- 白話比喻：把「這次做對的食譜＋步驟」存起來，下次改菜刀或改火候，立刻知道哪裡變差。

### [08:08-10:48] 誰來評？三層評估者：自動指標 → LLM Judge → 人類（HITL）
- 自動化 metrics：ROUGE/BLEU（字串相似）、BERTScore/embedding cosine（語意相似）適合做 CI/CD 裡的「趨勢警報」，但很淺，不能代表真正有用/安全。[AQ-8]
- LLM-as-a-Judge：用更強的 LLM 依 rubric 評分或比較另一個 Agent 的輸出/中間步驟，能大規模產出較細緻的質化判斷。[AQ-9]
- 重要技巧：pairwise comparison（兩兩比較）優於單次打分（1~5 分容易大家都打 3，central tendency bias）；用 win/loss/tie 讓訊號更乾淨。[AQ-9]
- Agent-as-a-Judge：更進一步，評「整段 trace」而非只評 final text，特別適合抓規劃/工具選擇/上下文處理的過程品質。[AQ-10]
- 人類（HITL）不可取代：domain nuance、價值判斷、golden set 建立、以及高風險動作的安全把關。[AQ-11]
#### (Concept: ROUGE / BLEU / BERTScore)
- 白話比喻：ROUGE/BLEU 像在比「兩段文字有多少字一樣」；BERTScore 像在比「意思像不像」。它們都不等於「真的有幫助」或「不會害人」。
#### 💡 深度補充：
- ROUGE 是摘要評估常用的 n-gram 重疊指標家族，偏 recall 導向（抓到多少參考摘要的片段）。[W9]
- BLEU 是機器翻譯經典 n-gram precision＋brevity penalty 指標，但同樣偏「表面相似」，不保證任務有效性。[W10]
- BERTScore 用 contextual embeddings 做 token 對 token 的相似度匹配，通常比單純 n-gram 更貼近語意一致性。[W11]
- LLM-as-a-judge 近年被系統化整理成一個研究領域（定義、分類、挑戰與 benchmark）。[W12]
- Agent-as-a-judge 研究指出：用「具備 agentic 能力的評審」可對整段任務過程給中間回饋，降低人工成本，並在某些設定下接近人類評估一致性。[W13]

### [09:55-11:33] HITL、Reviewer UI、RAI：把「人類判斷」做成可操作的系統
- Reviewer UI 最佳實務：雙欄（左：對話上下文；右：Agent reasoning/trace），讓 reviewer 能快速標註問題類型（bad plan、tool misuse 等）。[AQ-12]
- 高風險動作必做 interruption workflow：例如 execute_payment、發敏感 email、刪資料庫等，Agent 執行前停下來讓人類 approve/reject。[AQ-12]
- RAI & safety evaluation 是 non-negotiable gate：要做 systematic red teaming（主動找攻擊/越獄/偏見/洩漏），搭配 automated filters＋human review。[AQ-12]
- Guardrails 建議做成 plugin 架構（before/after callbacks）：輸入端掃 prompt injection、輸出端掃 PII 外洩，讓安全機制可重用、可測試、可分層。[AQ-12]
#### (Concept: Red teaming / 紅隊測試)
- 白話比喻：你自己先扮演壞人來攻擊你的系統，把洞先挖出來補好。
#### (Concept: PII / 個資)
- 白話比喻：像身分證號、地址、信用卡；你把 log 存下來就等於把敏感資料複製一份，沒 scrub 就很危險。
#### 💡 深度補充：
- prompt injection 的本質是「把模型當成可被操控的代理人」，攻擊者用精心包裝的輸入讓模型偏離原本 policy 或洩漏資訊；這類風險需要系統層緩解（權限、隔離、審批、最小化工具能力），而不是只靠提示詞。[W5][W6]

### [11:33-14:16] Observability 三支柱：Logs（事實）/ Traces（因果）/ Metrics（總覽）
- 監控 vs 可觀測性（廚房比喻）：line cook 有固定食譜→監控像 checklist；gourmet chef 面對 mystery box→必須看過程決策，才能評「思考是否有效」。[AQ-4]
- Logs：原子事件的時間戳日記，最好是 structured JSON；要包含 prompt/response、中間推理、tool input/output/error、內部狀態變化。[AQ-4][AQ-14]
- Traces：把 logs 用 spans 串成端到端故事線，揭露因果「為什麼會錯」；尤其對 multi-step agent 的除錯不可或缺。[AQ-13]
- Metrics：不是新資料，而是由 logs/traces 聚合出來的總體健康分數；分成 System metrics 與 Quality metrics。[AQ-13][AQ-15]
  - System metrics（給 SRE/ops）：Latency（$P50,P99$）、Error rate、Tokens per task、API cost、Task completion rate、Tool usage frequency。[AQ-15]
  - Quality metrics（給 DS/PM/AgentOps）：Correctness、Trajectory adherence、Safety、Helpfulness/Relevance（通常需要 golden set 或 LLM judge 來算）。[AQ-15]
- 成本權衡：高粒度記錄很貴且會增加延遲；所以用 dynamic sampling：例如成功請求只 trace 10%，失敗請求 trace 100%。[AQ-1][AQ-16]
#### (Concept: Span / Trace)
- 白話比喻：trace 是「一個任務的完整故事」；span 是故事裡的「一個章節」（一次 LLM call、一次 tool call）。
#### (Concept: Percentile latency)
- 白話比喻：$P50$ 像「一般人排隊等多久」；$P99$ 像「最倒楣那群人等多久」，通常更能反映尖峰壓力與壞體驗。
#### 💡 深度補充：
- OpenTelemetry 明確定義 traces 與 span context（含 Trace ID/Span ID）以及 context propagation，讓你跨元件追蹤同一條請求的因果路徑。[W1][W2][W3]
- Chain-of-thought prompting 研究顯示「讓模型外顯中間推理步驟」可提升複雜推理表現；工程上即使不存 raw CoT，也會用「可稽核的中間狀態/工具證據」來支撐除錯與評估。[W14]

### [14:17-16:24] Agent Quality Flywheel：把失敗變成燃料，讓系統越用越可靠
- Flywheel 四步驟（把框架變成操作手冊）：[AQ-17]
  - Step 1 Define Quality：先用四大支柱定義目標（你要什麼叫「好」）。
  - Step 2 Instrument for Visibility：先把 logs/traces 做好，才有證據。
  - Step 3 Evaluate the Process：用 outside-in（黑盒→玻璃盒）＋混合評審（metrics/LLM judge/HITL）。
  - Step 4 Architect the Feedback Loop：把 production failure 轉成「永久回歸測試」加入 golden eval set，越失敗越強。[AQ-17]
- 三大原則收斂（逐字稿總結對齊白皮書）：[AQ-17]
  - 評估是架構支柱，不是最後 QA。
  - 軌跡才是真相：看旅程不只看終點。
  - 人類是最終裁判：自動化負責規模，人類負責定義「什麼是好」與高風險邊界。
#### (Concept: Evaluatable-by-design / 可評估性內建)
- 白話比喻：不要先做完車才裝感測器；一開始就把「可量測、可追蹤、可回放」當成系統需求。
#### 💡 深度補充：
- 這種「持續評估＋回饋」的精神，本質上是把 AgentOps 變成類似 DevOps 的工程閉環；安全面則可用 NIST AI RMF 的風險治理語言來對齊（治理、量測、監控、回應）。[W7]
