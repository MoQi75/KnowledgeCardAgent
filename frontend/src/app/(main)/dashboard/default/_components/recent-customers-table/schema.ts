import z from "zod";

export const recentAgentTaskSchema = z.object({
  id: z.string(),
  taskName: z.string(),
  intent: z.string(),
  tools: z.array(z.string()),
  status: z.string(),
  completedAt: z.string(),
  order: z.number(),
});

export type RecentAgentTaskRow = z.infer<typeof recentAgentTaskSchema>;
