"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Controller, useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Field, FieldContent, FieldError, FieldGroup, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";

const formSchema = z.object({
  email: z.string().email({ message: "请输入有效的账号邮箱。" }),
  password: z.string().min(6, { message: "密码至少需要 6 个字符。" }),
  remember: z.boolean().optional(),
});

export function LoginForm() {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      email: "",
      password: "",
      remember: false,
    },
  });

  const onSubmit = (data: z.infer<typeof formSchema>) => {
    toast("You submitted the following values", {
      description: (
        <pre className="mt-2 w-[320px] rounded-md bg-neutral-950 p-4">
          <code className="text-white">{JSON.stringify(data, null, 2)}</code>
        </pre>
      ),
    });
  };

  return (
    <form noValidate onSubmit={form.handleSubmit(onSubmit)} className="flex flex-col gap-5">
      <FieldGroup className="gap-5">
        <Controller
          control={form.control}
          name="email"
          render={({ field, fieldState }) => (
            <Field className="gap-2" data-invalid={fieldState.invalid}>
              <FieldLabel htmlFor="login-email" className="text-cyan-50">
                账号
              </FieldLabel>
              <Input
                {...field}
                id="login-email"
                type="email"
                placeholder="请输入账号邮箱"
                autoComplete="email"
                aria-invalid={fieldState.invalid}
                className="h-12 border-white/12 bg-white/[0.08] px-4 text-white placeholder:text-slate-400 focus-visible:border-cyan-300 focus-visible:ring-cyan-300/30"
              />
              {fieldState.invalid && <FieldError errors={[fieldState.error]} className="text-rose-200" />}
            </Field>
          )}
        />
        <Controller
          control={form.control}
          name="password"
          render={({ field, fieldState }) => (
            <Field className="gap-2" data-invalid={fieldState.invalid}>
              <FieldLabel htmlFor="login-password" className="text-cyan-50">
                密码
              </FieldLabel>
              <Input
                {...field}
                id="login-password"
                type="password"
                placeholder="请输入密码"
                autoComplete="current-password"
                aria-invalid={fieldState.invalid}
                className="h-12 border-white/12 bg-white/[0.08] px-4 text-white placeholder:text-slate-400 focus-visible:border-fuchsia-300 focus-visible:ring-fuchsia-300/30"
              />
              {fieldState.invalid && <FieldError errors={[fieldState.error]} className="text-rose-200" />}
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
                className="border-cyan-200/40 data-[state=checked]:border-cyan-300 data-[state=checked]:bg-cyan-300 data-[state=checked]:text-slate-950"
              />
              <FieldContent>
                <FieldLabel htmlFor="login-remember" className="font-normal text-slate-300">
                  记住我
                </FieldLabel>
                {fieldState.invalid && <FieldError errors={[fieldState.error]} className="text-rose-200" />}
              </FieldContent>
            </Field>
          )}
        />
      </FieldGroup>
      <Button
        className="h-12 w-full bg-gradient-to-r from-cyan-400 via-blue-500 to-fuchsia-500 font-semibold text-white shadow-[0_0_28px_rgba(59,130,246,0.35)] transition hover:shadow-[0_0_40px_rgba(168,85,247,0.5)]"
        type="submit"
      >
        进入系统
      </Button>
    </form>
  );
}
