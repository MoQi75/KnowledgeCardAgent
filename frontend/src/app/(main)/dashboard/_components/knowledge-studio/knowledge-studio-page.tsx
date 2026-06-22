"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import {
  AlertCircle,
  BookOpen,
  Brain,
  CheckCircle2,
  ClipboardCheck,
  Database,
  FileText,
  Layers3,
  Loader2,
  RotateCcw,
  Route,
  Sparkles,
  UploadCloud,
} from "lucide-react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Textarea } from "@/components/ui/textarea";
import { APP_CONFIG } from "@/config/app-config";
import {
  type AgentAnalyzeResponse,
  type AnswerCheckResult,
  cardSystemApi,
  type DocumentRecord,
  type KnowledgeCard,
  type QuizQuestion,
  type ReviewPlan,
  type StudySummary,
  type WrongQuestion,
} from "@/lib/card-system-api";

type StudioView =
  | "dashboard"
  | "documents"
  | "cards"
  | "quiz"
  | "wrong-questions"
  | "review-plan"
  | "stats"
  | "settings";

interface KnowledgeStudioPageProps {
  view: StudioView;
}

const emptySummary: StudySummary = {
  document_count: 0,
  card_count: 0,
  quiz_count: 0,
  answer_count: 0,
  wrong_count: 0,
  accuracy: 0,
};

export function KnowledgeStudioPage({ view }: KnowledgeStudioPageProps) {
  const [summary, setSummary] = useState<StudySummary>(emptySummary);
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [cards, setCards] = useState<KnowledgeCard[]>([]);
  const [quiz, setQuiz] = useState<QuizQuestion[]>([]);
  const [wrongQuestions, setWrongQuestions] = useState<WrongQuestion[]>([]);
  const [reviewPlan, setReviewPlan] = useState<ReviewPlan | null>(null);
  const [selectedDocumentId, setSelectedDocumentId] = useState("");
  const [loading, setLoading] = useState(false);

  const loadAll = useCallback(async () => {
    setLoading(true);
    try {
      const [nextSummary, nextDocuments, nextCards, nextQuiz, nextWrongQuestions] = await Promise.all([
        cardSystemApi.getStudySummary().catch(() => emptySummary),
        cardSystemApi.listDocuments().catch(() => []),
        cardSystemApi.listCards().catch(() => []),
        cardSystemApi.listQuiz().catch(() => []),
        cardSystemApi.listWrongQuestions().catch(() => []),
      ]);
      setSummary(nextSummary);
      setDocuments(nextDocuments);
      setCards(nextCards);
      setQuiz(nextQuiz);
      setWrongQuestions(nextWrongQuestions);
      if (!selectedDocumentId && nextDocuments[0]) {
        setSelectedDocumentId(nextDocuments[0].id);
      }
    } finally {
      setLoading(false);
    }
  }, [selectedDocumentId]);

  useEffect(() => {
    loadAll().catch((error) => showError("加载数据失败", error));
  }, [loadAll]);

  const pageTitle = useMemo(() => {
    const titles: Record<StudioView, string> = {
      dashboard: "仪表盘",
      documents: "资料库",
      cards: "知识卡片",
      quiz: "自测练习",
      "wrong-questions": "错题本",
      "review-plan": "复习计划",
      stats: "学习统计",
      settings: "系统设置",
    };
    return titles[view];
  }, [view]);

  return (
    <div className="@container/main flex flex-col gap-4 rounded-3xl border border-[#eadffd] bg-[radial-gradient(circle_at_12%_8%,rgba(255,255,255,0.78),transparent_28%),radial-gradient(circle_at_86%_20%,rgba(197,174,241,0.36),transparent_30%),linear-gradient(135deg,#f7f2ff_0%,#eee5ff_52%,#f9eef3_100%)] p-4 shadow-[0_24px_70px_rgba(109,81,184,0.12)] md:gap-6 md:p-6 [&_[data-slot=badge]]:border-[#d8cff6] [&_[data-slot=badge]]:bg-[#f0e9ff] [&_[data-slot=badge]]:text-[#6d51b8] [&_[data-slot=button][data-variant=outline]]:border-[#d8cff6] [&_[data-slot=button][data-variant=outline]]:bg-white/70 [&_[data-slot=button][data-variant=outline]]:text-[#6d51b8] [&_[data-slot=button][data-variant=outline]]:hover:bg-[#f7d5df]/70 [&_[data-slot=button][data-variant=outline]]:hover:text-[#7f123c] [&_[data-slot=button][data-variant=secondary]]:bg-[#f0e9ff] [&_[data-slot=button][data-variant=secondary]]:text-[#6d51b8] [&_[data-slot=card-description]]:text-[#6f6680] [&_[data-slot=card-title]]:text-[#19162b] [&_[data-slot=card]]:border [&_[data-slot=card]]:border-[#e7dffd] [&_[data-slot=card]]:bg-[#fffafe]/92 [&_[data-slot=card]]:shadow-[0_16px_42px_rgba(109,81,184,0.1)] [&_[data-slot=input]]:border-[#e7dffd] [&_[data-slot=input]]:bg-white/80 [&_[data-slot=table-head]]:text-[#4f4564] [&_[data-slot=textarea]]:border-[#e7dffd] [&_[data-slot=textarea]]:bg-white/80">
      <div className="flex flex-col gap-2">
        <Badge variant="outline" className="w-fit">
          CardReviewAgent
        </Badge>
        <div className="flex flex-col justify-between gap-3 md:flex-row md:items-end">
          <div>
            <h1 className="font-heading font-semibold text-2xl text-[#19162b] tracking-normal">{APP_CONFIG.name}</h1>
            <p className="text-[#5d5472] text-sm">
              对接 FastAPI + LangGraph + RAG 后端，完成资料导入、知识卡片、自测和复习规划。
            </p>
          </div>
          <Button variant="outline" onClick={() => loadAll()} disabled={loading}>
            {loading ? <Loader2 className="animate-spin" /> : <RotateCcw />}
            刷新数据
          </Button>
        </div>
      </div>

      <div className="flex items-center gap-2 text-[#7b7190] text-sm">
        <span>{pageTitle}</span>
      </div>

      {view === "dashboard" && <DashboardView summary={summary} cards={cards} reviewPlan={reviewPlan} />}
      {view === "documents" && (
        <DocumentsView
          documents={documents}
          selectedDocumentId={selectedDocumentId}
          setSelectedDocumentId={setSelectedDocumentId}
          onChanged={loadAll}
          setCards={setCards}
          setQuiz={setQuiz}
          setReviewPlan={setReviewPlan}
        />
      )}
      {view === "cards" && <CardsView cards={cards} onChanged={loadAll} />}
      {view === "quiz" && <QuizView quiz={quiz} onChanged={loadAll} />}
      {view === "wrong-questions" && <WrongQuestionsView wrongQuestions={wrongQuestions} />}
      {view === "review-plan" && (
        <ReviewPlanView wrongQuestions={wrongQuestions} reviewPlan={reviewPlan} setReviewPlan={setReviewPlan} />
      )}
      {view === "stats" && <StatsView summary={summary} />}
      {view === "settings" && <SettingsView />}
    </div>
  );
}

function DashboardView({
  summary,
  cards,
  reviewPlan,
}: {
  summary: StudySummary;
  cards: KnowledgeCard[];
  reviewPlan: ReviewPlan | null;
}) {
  return (
    <>
      <SummaryCards summary={summary} />
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>今日复习任务</CardTitle>
            <CardDescription>来自最近生成的复习计划</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {reviewPlan?.tasks?.[0] ? (
              <TaskCard task={reviewPlan.tasks[0]} />
            ) : (
              <EmptyHint text="暂无复习任务，请先在复习计划页面生成计划。" />
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>最近生成的知识卡片</CardTitle>
            <CardDescription>展示最新的学习卡片摘要</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {cards.slice(0, 3).map((card) => (
              <div key={card.id} className="rounded-lg border border-[#eadffd] bg-white/70 p-3">
                <div className="font-medium text-[#19162b]">{card.title}</div>
                <p className="mt-1 line-clamp-2 text-[#6f6680] text-sm">{card.summary}</p>
              </div>
            ))}
            {cards.length === 0 && <EmptyHint text="暂无知识卡片，请先导入资料并生成卡片。" />}
          </CardContent>
        </Card>
      </div>
    </>
  );
}

function DocumentsView({
  documents,
  selectedDocumentId,
  setSelectedDocumentId,
  onChanged,
  setCards,
  setQuiz,
  setReviewPlan,
}: {
  documents: DocumentRecord[];
  selectedDocumentId: string;
  setSelectedDocumentId: (id: string) => void;
  onChanged: () => Promise<void>;
  setCards: (cards: KnowledgeCard[]) => void;
  setQuiz: (quiz: QuizQuestion[]) => void;
  setReviewPlan: (plan: ReviewPlan) => void;
}) {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [busy, setBusy] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [learningGoal, setLearningGoal] = useState("");
  const [cardCount, setCardCount] = useState(8);
  const [quizCount, setQuizCount] = useState(5);
  const [reviewDays, setReviewDays] = useState(7);
  const [analysisResult, setAnalysisResult] = useState<AgentAnalyzeResponse | null>(null);
  const [analyzing, setAnalyzing] = useState(false);

  async function createDocument() {
    if (!content.trim()) {
      toast.warning("请先粘贴学习资料内容。");
      return;
    }
    setBusy(true);
    try {
      const document = await cardSystemApi.createDocument({
        title: title || "未命名资料",
        content,
      });
      setSelectedDocumentId(document.id);
      toast.success("资料已创建");
      await onChanged();
    } catch (error) {
      showError("创建资料失败", error);
    } finally {
      setBusy(false);
    }
  }

  async function generateCards() {
    setBusy(true);
    try {
      const payload = selectedDocumentId
        ? { document_id: selectedDocumentId }
        : { text: content, title: title || "未命名资料" };
      if (!payload.document_id && !content.trim()) {
        toast.warning("请选择资料或输入资料内容。");
        return;
      }
      const result = await cardSystemApi.generateCards(payload);
      setCards(result.cards.cards);
      setSelectedDocumentId(result.document.id);
      toast.success("知识卡片已生成");
      await onChanged();
    } catch (error) {
      showError("生成知识卡片失败", error);
    } finally {
      setBusy(false);
    }
  }

  async function analyzeFile() {
    if (!selectedFile) {
      toast.warning("请先上传学习资料文件。");
      return;
    }

    setAnalyzing(true);
    try {
      const formData = new FormData();
      formData.append("file", selectedFile);
      formData.append("user_id", "default_user");
      if (learningGoal.trim()) {
        formData.append("learning_goal", learningGoal.trim());
      }
      formData.append("card_count", String(cardCount));
      formData.append("quiz_count", String(quizCount));
      formData.append("review_days", String(reviewDays));

      const response = await cardSystemApi.analyzeStudyFile(formData);
      await onChanged();
      setAnalysisResult(response);
      setCards(response.cards);
      setQuiz(response.quizzes);
      setReviewPlan(toReviewPlan(response));
      setSelectedDocumentId(response.document_id);
      toast.success("CardReviewAgent 智能分析已完成");
    } catch (error) {
      showError("CardReviewAgent 智能分析失败", error);
    } finally {
      setAnalyzing(false);
    }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="size-5 text-[#b70f46]" />
                资料智能分析
              </CardTitle>
              <CardDescription>
                上传学习资料，CardReviewAgent 将自动解析内容并生成知识卡片、自测题和复习计划。
              </CardDescription>
            </div>
            <Badge variant="secondary">工具调用 · RAG 检索 · 学习记忆</Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 xl:grid-cols-[minmax(0,1.2fr)_minmax(280px,0.8fr)]">
            <div className="space-y-4 rounded-xl border border-[#eadffd] bg-white/64 p-4">
              <div className="grid gap-2">
                <Label htmlFor="study-file">上传学习资料文件</Label>
                <Input
                  id="study-file"
                  type="file"
                  accept=".pdf,.docx,.txt,.md,.markdown,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain,text/markdown"
                  onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
                />
                <p className="text-[#7b7190] text-xs">支持 PDF、DOCX、TXT、Markdown。</p>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="learning-goal">学习目标</Label>
                <Input
                  id="learning-goal"
                  value={learningGoal}
                  onChange={(event) => setLearningGoal(event.target.value)}
                  placeholder="例如：帮我复习编译原理 FIRST/FOLLOW 集"
                />
              </div>
            </div>

            <div className="space-y-4 rounded-xl border border-[#eadffd] bg-white/64 p-4">
              <div className="grid gap-3 sm:grid-cols-3 xl:grid-cols-1">
                <NumberSetting
                  id="card-count"
                  label="知识卡片数量"
                  value={cardCount}
                  onChange={setCardCount}
                />
                <NumberSetting
                  id="quiz-count"
                  label="自测题数量"
                  value={quizCount}
                  onChange={setQuizCount}
                />
                <NumberSetting
                  id="review-days"
                  label="复习计划天数"
                  value={reviewDays}
                  onChange={setReviewDays}
                />
              </div>
              <Button className="w-full" onClick={analyzeFile} disabled={analyzing}>
                {analyzing ? <Loader2 className="animate-spin" /> : <UploadCloud />}
                启动 CardReviewAgent 智能分析
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {analysisResult && <AgentTracePanel result={analysisResult} />}
      {analysisResult && <AgentResultSections result={analysisResult} />}

      <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_360px]">
        <Card>
          <CardHeader>
            <CardTitle>资料输入</CardTitle>
            <CardDescription>粘贴课程笔记、论文摘要、教材片段或复习资料。</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-2">
              <Label htmlFor="document-title">资料标题</Label>
              <Input
                id="document-title"
                value={title}
                onChange={(event) => setTitle(event.target.value)}
                placeholder="例如：LangGraph 工作流基础"
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="document-content">学习资料内容</Label>
              <Textarea
                id="document-content"
                value={content}
                onChange={(event) => setContent(event.target.value)}
                placeholder="在这里粘贴学习资料文本..."
                className="min-h-72"
              />
            </div>
            <div className="flex flex-wrap gap-2">
              <Button onClick={createDocument} disabled={busy}>
                <FileText />
                创建资料
              </Button>
              <Button variant="secondary" onClick={generateCards} disabled={busy}>
                <BookOpen />
                生成知识卡片
              </Button>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>资料列表</CardTitle>
            <CardDescription>选择资料后可直接生成知识卡片。</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {documents.map((document) => (
              <button
                type="button"
                key={document.id}
                onClick={() => setSelectedDocumentId(document.id)}
                className={`w-full rounded-lg border border-[#eadffd] bg-white/70 p-3 text-left transition-colors hover:bg-[#f7f2ff] ${
                  selectedDocumentId === document.id
                    ? "border-[#b70f46] bg-[#f7d5df]/45 shadow-[0_10px_24px_rgba(183,15,70,0.12)]"
                    : ""
                }`}
              >
                <div className="font-medium text-[#19162b]">{document.title}</div>
                <p className="mt-1 line-clamp-2 text-[#6f6680] text-xs">{document.content}</p>
              </button>
            ))}
            {documents.length === 0 && <EmptyHint text="暂无资料，请先创建一条学习资料。" />}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function NumberSetting({
  id,
  label,
  value,
  onChange,
}: {
  id: string;
  label: string;
  value: number;
  onChange: (value: number) => void;
}) {
  return (
    <div className="grid gap-2">
      <Label htmlFor={id}>{label}</Label>
      <Input
        id={id}
        type="number"
        min={1}
        max={30}
        value={value}
        onChange={(event) => onChange(Math.max(1, Number(event.target.value) || 1))}
      />
    </div>
  );
}

function AgentTracePanel({ result }: { result: AgentAnalyzeResponse }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>CardReviewAgent 执行过程</CardTitle>
        <CardDescription>
          展示文件解析、意图识别、任务规划、工具调用、RAG 检索、结果校验和学习记忆更新。
        </CardDescription>
      </CardHeader>
      <CardContent className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {result.agent_trace.map((item) => (
          <div key={`${item.step}-${item.name}`} className="rounded-xl border border-[#eadffd] bg-white/70 p-4">
            <div className="flex items-start gap-3">
              <div className="flex size-9 shrink-0 items-center justify-center rounded-full bg-[#f0e9ff] text-[#6d51b8]">
                {traceIcon(item.name)}
              </div>
              <div className="min-w-0 space-y-1">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-medium text-[#19162b]">
                    {item.step}. {item.name}
                  </span>
                  <Badge variant="outline">{item.status}</Badge>
                </div>
                <p className="text-[#6f6680] text-sm">{item.detail}</p>
              </div>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

function AgentResultSections({ result }: { result: AgentAnalyzeResponse }) {
  return (
    <div className="grid gap-4 xl:grid-cols-3">
      <Card>
        <CardHeader>
          <CardTitle>知识卡片</CardTitle>
          <CardDescription>
            已生成 {result.cards.length} 张卡片，来源于 {result.summary.rag_chunk_count} 个 RAG 检索切片。
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {result.cards.map((card) => {
            const relatedPoints = card.related_points ?? card.related_concepts ?? [];
            return (
              <div key={card.id} className="space-y-2 rounded-xl border border-[#eadffd] bg-white/70 p-3">
                <div className="font-medium text-[#19162b]">{card.title}</div>
                <p className="line-clamp-3 text-[#6f6680] text-sm">{card.explanation}</p>
                <TagList label="关联知识点" items={relatedPoints} />
              </div>
            );
          })}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>自测题</CardTitle>
          <CardDescription>QuizGeneratorTool 已生成 {result.quizzes.length} 道练习题。</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {result.quizzes.map((question, index) => (
            <div key={question.id} className="space-y-2 rounded-xl border border-[#eadffd] bg-white/70 p-3">
              <div className="font-medium text-[#19162b]">
                {index + 1}. {question.question}
              </div>
              <p className="text-[#6f6680] text-sm">答案：{question.answer}</p>
              <p className="line-clamp-2 text-[#7b7190] text-xs">解析：{question.explanation}</p>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>复习计划</CardTitle>
          <CardDescription>
            {result.review_plan.plan_title}，共 {result.review_plan.review_days} 天。
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <TagList label="薄弱点" items={result.review_plan.weak_points} />
          {result.review_plan.daily_tasks.map((task) => (
            <div key={`${task.day}-${task.task_title}`} className="rounded-xl border border-[#eadffd] bg-white/70 p-3">
              <div className="font-medium text-[#19162b]">{task.task_title}</div>
              <p className="mt-1 text-[#6f6680] text-sm">{task.task_content}</p>
              <p className="mt-1 text-[#7b7190] text-xs">原因：{task.reason}</p>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}

function traceIcon(name: string) {
  if (name.includes("文件")) {
    return <FileText className="size-4" />;
  }
  if (name.includes("规划")) {
    return <Route className="size-4" />;
  }
  if (name.includes("RAG")) {
    return <Layers3 className="size-4" />;
  }
  if (name.includes("记忆")) {
    return <Database className="size-4" />;
  }
  return <Brain className="size-4" />;
}

function toReviewPlan(result: AgentAnalyzeResponse): ReviewPlan {
  return {
    id: result.review_plan.id ?? result.document_id,
    weak_points: result.review_plan.weak_points,
    tasks: result.review_plan.daily_tasks.map((task) => ({
      day: task.day,
      topic: task.task_title,
      task: task.task_content,
      reason: task.reason,
      is_completed: false,
    })),
  };
}

function CardsView({ cards, onChanged }: { cards: KnowledgeCard[]; onChanged: () => Promise<void> }) {
  async function generateQuiz(cardId: string) {
    try {
      await cardSystemApi.generateQuiz({ card_id: cardId });
      toast.success("题目已生成，请到自测练习查看。");
      await onChanged();
    } catch (error) {
      showError("生成题目失败", error);
    }
  }

  if (cards.length === 0) {
    return <EmptyHint text="暂无知识卡片，请先在资料库生成卡片。" />;
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      {cards.map((card) => (
        <Card key={card.id}>
          <CardHeader>
            <CardTitle>{card.title}</CardTitle>
            <CardDescription>{card.summary}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <TagList label="关键词" items={card.keywords} />
            <TagList label="易错点" items={card.common_mistakes} />
            <TagList label="关联知识点" items={card.related_concepts ?? card.related_points ?? []} />
            <Button variant="outline" onClick={() => generateQuiz(card.id)}>
              <ClipboardCheck />
              生成题目
            </Button>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

function QuizView({ quiz, onChanged }: { quiz: QuizQuestion[]; onChanged: () => Promise<void> }) {
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [results, setResults] = useState<Record<string, AnswerCheckResult>>({});

  async function submit(question: QuizQuestion) {
    const answer = answers[question.id]?.trim();
    if (!answer) {
      toast.warning("请先填写答案。");
      return;
    }
    try {
      const response = await cardSystemApi.submitQuiz({
        question_id: question.id,
        user_answer: answer,
      });
      setResults((current) => ({ ...current, [question.id]: response.result }));
      toast.success(response.result.is_correct ? "回答正确" : "已记录到错题本");
      await onChanged();
    } catch (error) {
      showError("提交答案失败", error);
    }
  }

  if (quiz.length === 0) {
    return <EmptyHint text="暂无题目，请先在知识卡片页面生成题目。" />;
  }

  return (
    <div className="space-y-4">
      {quiz.map((question, index) => {
        const result = results[question.id];
        return (
          <Card key={question.id}>
            <CardHeader>
              <CardTitle>
                {index + 1}. {question.question}
              </CardTitle>
              <CardDescription>
                {question.question_type} · {question.difficulty} · {question.related_card_title}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {question.options.length > 0 ? (
                <RadioGroup
                  value={answers[question.id] ?? ""}
                  onValueChange={(value) => setAnswers((current) => ({ ...current, [question.id]: value }))}
                >
                  {question.options.map((option) => (
                    <div key={option} className="flex items-center gap-2 rounded-lg border border-[#eadffd] bg-white/70 p-3">
                      <RadioGroupItem value={option} id={`${question.id}-${option}`} />
                      <Label htmlFor={`${question.id}-${option}`}>{option}</Label>
                    </div>
                  ))}
                </RadioGroup>
              ) : (
                <Textarea
                  placeholder="输入你的答案..."
                  value={answers[question.id] ?? ""}
                  onChange={(event) => setAnswers((current) => ({ ...current, [question.id]: event.target.value }))}
                />
              )}
              <Button onClick={() => submit(question)}>提交答案</Button>
              {result && (
                <div className="space-y-2 rounded-lg border border-[#eadffd] bg-[#f7f2ff]/75 p-3">
                  <div className="flex items-center gap-2 font-medium">
                    {result.is_correct ? (
                      <CheckCircle2 className="size-4 text-green-600" />
                    ) : (
                      <AlertCircle className="size-4 text-destructive" />
                    )}
                    {result.is_correct ? "回答正确" : "回答不正确"}
                  </div>
                  <p className="text-sm">正确答案：{result.correct_answer}</p>
                  <p className="text-sm">解析：{result.explanation}</p>
                  <p className="text-sm">反馈：{result.feedback}</p>
                </div>
              )}
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}

function WrongQuestionsView({ wrongQuestions }: { wrongQuestions: WrongQuestion[] }) {
  if (wrongQuestions.length === 0) {
    return <EmptyHint text="暂无错题。完成自测并答错后会在这里显示。" />;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>错题本</CardTitle>
        <CardDescription>集中复盘薄弱知识点和高频错误。</CardDescription>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>题目</TableHead>
              <TableHead>关联知识点</TableHead>
              <TableHead>错误次数</TableHead>
              <TableHead>解析</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {wrongQuestions.map((item) => (
              <TableRow key={item.id}>
                <TableCell className="max-w-xs">{item.question}</TableCell>
                <TableCell>{item.related_knowledge || "暂无"}</TableCell>
                <TableCell>{item.error_count}</TableCell>
                <TableCell className="max-w-sm text-[#6f6680]">{item.explanation}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}

function ReviewPlanView({
  wrongQuestions,
  reviewPlan,
  setReviewPlan,
}: {
  wrongQuestions: WrongQuestion[];
  reviewPlan: ReviewPlan | null;
  setReviewPlan: (plan: ReviewPlan) => void;
}) {
  async function generatePlan(days: number) {
    try {
      const weakPoints = wrongQuestions.map((item) => item.related_knowledge || item.question).filter(Boolean);
      const response = await cardSystemApi.generateReviewPlan({
        weak_points: weakPoints.length > 0 ? weakPoints : undefined,
        title: `${days} 天复习计划`,
      });
      setReviewPlan({ ...response.plan, tasks: response.plan.tasks.slice(0, days) });
      toast.success("复习计划已生成");
    } catch (error) {
      showError("生成复习计划失败", error);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <Button onClick={() => generatePlan(3)}>生成 3 天复习计划</Button>
        <Button variant="outline" onClick={() => generatePlan(7)}>
          生成 7 天复习计划
        </Button>
      </div>
      {!reviewPlan && <EmptyHint text="暂无复习计划，请根据错题或薄弱点生成计划。" />}
      {reviewPlan?.tasks.map((task) => (
        <TaskCard key={`${task.day}-${task.topic}`} task={task} />
      ))}
    </div>
  );
}

function StatsView({ summary }: { summary: StudySummary }) {
  return (
    <div className="space-y-4">
      <SummaryCards summary={summary} />
      <Card>
        <CardHeader>
          <CardTitle>正确率</CardTitle>
          <CardDescription>基于已提交答案统计</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center justify-between text-sm">
            <span>当前正确率</span>
            <span>{formatPercent(summary.accuracy)}</span>
          </div>
          <Progress value={summary.accuracy * 100} />
          <p className="text-[#6f6680] text-sm">
            已累计 {summary.answer_count} 次答题，其中错题 {summary.wrong_count} 道。
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

function SettingsView() {
  const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8080";

  return (
    <Card>
      <CardHeader>
        <CardTitle>系统设置</CardTitle>
        <CardDescription>前端通过环境变量连接后端 FastAPI 服务。</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="grid gap-2">
          <Label>后端接口地址</Label>
          <Input value={apiBase} readOnly />
        </div>
        <p className="text-[#6f6680] text-sm">
          如需修改，请在环境变量中设置 NEXT_PUBLIC_API_BASE_URL，默认 http://localhost:8080。
        </p>
      </CardContent>
    </Card>
  );
}

function SummaryCards({ summary }: { summary: StudySummary }) {
  const items = [
    ["资料数量", summary.document_count],
    ["知识卡片数量", summary.card_count],
    ["题目数量", summary.quiz_count],
    ["答题数量", summary.answer_count],
    ["错题数量", summary.wrong_count],
    ["正确率", formatPercent(summary.accuracy)],
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-6">
      {items.map(([label, value]) => (
        <Card key={label}>
          <CardHeader>
            <CardDescription>{label}</CardDescription>
            <CardTitle className="text-2xl">{value}</CardTitle>
          </CardHeader>
        </Card>
      ))}
    </div>
  );
}

function TaskCard({
  task,
}: {
  task: { day: number; topic: string; task: string; reason: string; is_completed: boolean };
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>
          Day {task.day}: {task.topic}
        </CardTitle>
        <CardDescription>{task.is_completed ? "已完成" : "待完成"}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-2">
        <p className="text-sm">{task.task}</p>
        <p className="text-[#6f6680] text-sm">原因：{task.reason}</p>
      </CardContent>
    </Card>
  );
}

function TagList({ label, items }: { label: string; items: string[] }) {
  return (
    <div className="space-y-2">
      <div className="text-[#7b7190] text-xs">{label}</div>
      <div className="flex flex-wrap gap-1.5">
        {items.length > 0 ? (
          items.map((item) => (
            <Badge key={item} variant="secondary">
              {item}
            </Badge>
          ))
        ) : (
          <span className="text-[#8b7f98] text-sm">暂无</span>
        )}
      </div>
    </div>
  );
}

function EmptyHint({ text }: { text: string }) {
  return (
    <div className="rounded-lg border border-[#d8cff6] border-dashed bg-white/62 p-6 text-center text-[#7b7190] text-sm">
      {text}
    </div>
  );
}

function showError(title: string, error: unknown) {
  const message = error instanceof Error ? error.message : "请检查后端服务是否已启动。";
  toast.error(title, { description: message });
}

function formatPercent(value: number) {
  return `${Math.round(value * 100)}%`;
}
