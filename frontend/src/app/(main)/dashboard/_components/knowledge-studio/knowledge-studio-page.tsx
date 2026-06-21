"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { AlertCircle, BookOpen, CheckCircle2, ClipboardCheck, FileText, Loader2, RotateCcw } from "lucide-react";
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
    <div className="@container/main flex flex-col gap-4 md:gap-6">
      <div className="flex flex-col gap-2">
        <Badge variant="outline" className="w-fit">
          {APP_CONFIG.shortName}
        </Badge>
        <div className="flex flex-col justify-between gap-3 md:flex-row md:items-end">
          <div>
            <h1 className="font-heading font-semibold text-2xl tracking-normal">{APP_CONFIG.name}</h1>
            <p className="text-muted-foreground text-sm">
              对接 FastAPI + LangGraph + RAG 后端，完成资料导入、知识卡片、自测和复习规划。
            </p>
          </div>
          <Button variant="outline" onClick={() => loadAll()} disabled={loading}>
            {loading ? <Loader2 className="animate-spin" /> : <RotateCcw />}
            刷新数据
          </Button>
        </div>
      </div>

      <div className="flex items-center gap-2 text-muted-foreground text-sm">
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
              <div key={card.id} className="rounded-lg border p-3">
                <div className="font-medium">{card.title}</div>
                <p className="mt-1 line-clamp-2 text-muted-foreground text-sm">{card.summary}</p>
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
}: {
  documents: DocumentRecord[];
  selectedDocumentId: string;
  setSelectedDocumentId: (id: string) => void;
  onChanged: () => Promise<void>;
  setCards: (cards: KnowledgeCard[]) => void;
}) {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [busy, setBusy] = useState(false);

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

  return (
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
              className={`w-full rounded-lg border p-3 text-left transition-colors hover:bg-muted ${
                selectedDocumentId === document.id ? "border-primary bg-muted" : ""
              }`}
            >
              <div className="font-medium">{document.title}</div>
              <p className="mt-1 line-clamp-2 text-muted-foreground text-xs">{document.content}</p>
            </button>
          ))}
          {documents.length === 0 && <EmptyHint text="暂无资料，请先创建一条学习资料。" />}
        </CardContent>
      </Card>
    </div>
  );
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
            <TagList label="关联知识点" items={card.related_concepts} />
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
                    <div key={option} className="flex items-center gap-2 rounded-lg border p-3">
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
                <div className="space-y-2 rounded-lg border bg-muted/40 p-3">
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
                <TableCell className="max-w-sm text-muted-foreground">{item.explanation}</TableCell>
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
          <p className="text-muted-foreground text-sm">
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
        <p className="text-muted-foreground text-sm">
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
        <p className="text-muted-foreground text-sm">原因：{task.reason}</p>
      </CardContent>
    </Card>
  );
}

function TagList({ label, items }: { label: string; items: string[] }) {
  return (
    <div className="space-y-2">
      <div className="text-muted-foreground text-xs">{label}</div>
      <div className="flex flex-wrap gap-1.5">
        {items.length > 0 ? (
          items.map((item) => (
            <Badge key={item} variant="secondary">
              {item}
            </Badge>
          ))
        ) : (
          <span className="text-muted-foreground text-sm">暂无</span>
        )}
      </div>
    </div>
  );
}

function EmptyHint({ text }: { text: string }) {
  return <div className="rounded-lg border border-dashed p-6 text-center text-muted-foreground text-sm">{text}</div>;
}

function showError(title: string, error: unknown) {
  const message = error instanceof Error ? error.message : "请检查后端服务是否已启动。";
  toast.error(title, { description: message });
}

function formatPercent(value: number) {
  return `${Math.round(value * 100)}%`;
}
