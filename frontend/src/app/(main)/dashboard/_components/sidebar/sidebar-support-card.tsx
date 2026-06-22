import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export function SidebarSupportCard() {
  return (
    <Card
      size="sm"
      className="overflow-hidden border-[#d8cff6] bg-[linear-gradient(135deg,#fffafe_0%,#f0e9ff_58%,#f9eef3_100%)] shadow-[0_12px_28px_rgba(109,81,184,0.12)] group-data-[collapsible=icon]:hidden"
    >
      <CardHeader className="min-w-0 px-4">
        <CardTitle className="truncate text-[#19162b] text-sm">学习助手</CardTitle>
        <CardDescription className="line-clamp-2 text-[#6f6680]">
          使用资料库、知识卡片、自测练习和复习计划完成闭环学习。
        </CardDescription>
      </CardHeader>
    </Card>
  );
}
