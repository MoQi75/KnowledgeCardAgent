"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { WandSparkles } from "lucide-react";
import { useRouter } from "next/navigation";
import { Controller, useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Field, FieldContent, FieldError, FieldGroup, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";

const demoAccount = {
  email: "admin@example.com",
  password: "123456",
};

const formSchema = z.object({
  email: z.string().email({ message: "请输入有效的账号邮箱。" }),
  password: z.string().min(6, { message: "密码至少需要 6 个字符。" }),
  remember: z.boolean().optional(),
});

export function LoginForm() {
  const router = useRouter();
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      email: "",
      password: "",
      remember: false,
    },
  });

  const fillDemoAccount = () => {
    form.setValue("email", demoAccount.email, { shouldDirty: true, shouldValidate: true });
    form.setValue("password", demoAccount.password, { shouldDirty: true, shouldValidate: true });
    form.setValue("remember", true, { shouldDirty: true });
    toast.success("已填充演示账号");
  };

  const onSubmit = (data: z.infer<typeof formSchema>) => {
    window.localStorage.setItem(
      "knowledge-card-demo-session",
      JSON.stringify({
        email: data.email,
        remember: Boolean(data.remember),
        loginAt: new Date().toISOString(),
      }),
    );
    toast.success("登录成功，正在进入系统");
    router.push("/dashboard");
  };

  return (
    <form noValidate onSubmit={form.handleSubmit(onSubmit)} className="flex flex-col gap-5">
      <Button
        className="h-11 w-full rounded-2xl border-[#e2d6fb] bg-[#f7f2ff] text-[#6d51b8] shadow-sm transition hover:-translate-y-0.5 hover:bg-[#efe6ff] hover:shadow-md"
        type="button"
        variant="outline"
        onClick={fillDemoAccount}
      >
        <WandSparkles className="size-4" />
        自动填充演示账号 admin@example.com / 123456
      </Button>

      <FieldGroup className="gap-5">
        <Controller
          control={form.control}
          name="email"
          render={({ field, fieldState }) => (
            <Field className="gap-2" data-invalid={fieldState.invalid}>
              <FieldLabel htmlFor="login-email" className="font-medium text-[#4f4564]">
                账号
              </FieldLabel>
              <Input
                {...field}
                id="login-email"
                type="email"
                placeholder="请输入账号邮箱"
                autoComplete="email"
                aria-invalid={fieldState.invalid}
                className="h-12 rounded-2xl border-[#e7dffd] bg-[#fcfaff] px-4 text-[#151426] shadow-inner transition placeholder:text-[#aaa1bb] focus-visible:border-[#ae99f1] focus-visible:ring-[#c5aef1]/45"
              />
              {fieldState.invalid && <FieldError errors={[fieldState.error]} className="text-[#c91944]" />}
            </Field>
          )}
        />
        <Controller
          control={form.control}
          name="password"
          render={({ field, fieldState }) => (
            <Field className="gap-2" data-invalid={fieldState.invalid}>
              <FieldLabel htmlFor="login-password" className="font-medium text-[#4f4564]">
                密码
              </FieldLabel>
              <Input
                {...field}
                id="login-password"
                type="password"
                placeholder="请输入密码"
                autoComplete="current-password"
                aria-invalid={fieldState.invalid}
                className="h-12 rounded-2xl border-[#e7dffd] bg-[#fcfaff] px-4 text-[#151426] shadow-inner transition placeholder:text-[#aaa1bb] focus-visible:border-[#ae99f1] focus-visible:ring-[#c5aef1]/45"
              />
              {fieldState.invalid && <FieldError errors={[fieldState.error]} className="text-[#c91944]" />}
            </Field>
          )}
        />
        <Controller
          control={form.control}
          name="remember"
          render={({ field, fieldState }) => (
            <Field className="items-center" orientation="horizontal" data-invalid={fieldState.invalid}>
              <Checkbox
                id="login-remember"
                name={field.name}
                checked={field.value}
                onCheckedChange={(checked) => field.onChange(Boolean(checked))}
                aria-invalid={fieldState.invalid}
                className="border-[#c5aef1] data-[state=checked]:border-[#b70f46] data-[state=checked]:bg-[#b70f46] data-[state=checked]:text-white"
              />
              <FieldContent>
                <FieldLabel htmlFor="login-remember" className="font-normal text-[#6f6680]">
                  记住我
                </FieldLabel>
                {fieldState.invalid && <FieldError errors={[fieldState.error]} className="text-[#c91944]" />}
              </FieldContent>
            </Field>
          )}
        />
      </FieldGroup>
      <Button
        className="h-12 w-full rounded-2xl bg-gradient-to-r from-[#b70f46] to-[#d9366f] font-semibold text-white shadow-[0_15px_28px_rgba(183,15,70,0.22)] transition hover:-translate-y-0.5 hover:shadow-[0_20px_36px_rgba(183,15,70,0.32)]"
        type="submit"
      >
        进入系统
      </Button>
    </form>
  );
}
