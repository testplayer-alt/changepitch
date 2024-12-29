"use client";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
} from "@/components/ui/form";
import { useState } from "react";

// Zodスキーマ定義
const formSchema = z.object({
  URL: z.string().min(1, {
    message: "URLを入力してください",
  }),
  pitch: z.string().min(1, {
    message: "ピッチを入力してください",
  }),
});

export default function Home() {
  // ローディング状態の管理
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState(""); // エラーメッセージを追加

  // useFormの初期化
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      URL: "",
      pitch: "",
    },
  });

  // フォーム送信処理
  const onSubmit = async (data: z.infer<typeof formSchema>) => {
    setIsLoading(true);
    setErrorMessage(""); // エラーメッセージをリセット
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/process`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const error = await response.json();
        setErrorMessage(`エラー: ${error.error}`);
        return;
      }

      // ファイル名の取得とデコード
      const contentDisposition = response.headers.get("Content-Disposition");
      let fileName = "processed_audio.mp3"; // デフォルト名
      console.log("タイトル:" + contentDisposition);
      if (contentDisposition) {
        const match = contentDisposition.match(/filename\*=UTF-8''(.+)/);
        if (match) {
          fileName = decodeURIComponent(match[1]); // デコードされた日本語名を取得
        }
      }

      const blob = await response.blob();
      const link = document.createElement("a");
      link.href = window.URL.createObjectURL(blob);
      link.download = fileName;
      link.click();
    } catch (error: unknown) {
      alert(`APIリクエストに失敗しました: ${error}`);
    } finally {
      setIsLoading(false);
    }
  };


  return (
    <div>
      {!isLoading && (
        <div className="row grid grid-cols-6 grid-rows-10 gap-4">
          <div className="col-span-1 row-span-4" />
          <div className="col-span-4 row-span-4 content-end">
            <h3 className="text-center pt- place-content-end m-auto font-bold text-[2rem]">
              Youtube動画のピッチを変更する
            </h3>
          </div>
          <div className="col-span-1 row-span-4" />
          <div className="col-span-2 row-span-6" />
          {/* フォーム */}
          <Form {...form}>
            <form
              onSubmit={form.handleSubmit(onSubmit)}
              className="col-span-2 row-span-6 m-auto w-full"
            >
              <FormField
                control={form.control}
                name="URL"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>YouTube URL:</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="URL"
                        {...field}
                        disabled={isLoading} // ローディング中は入力を無効化
                      />
                    </FormControl>
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="pitch"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>ピッチ (半音単位):</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        placeholder=""
                        {...field}
                        disabled={isLoading} // ローディング中は入力を無効化
                      />
                    </FormControl>
                  </FormItem>
                )}
              />
              <div className="text-center mt-2">
                <Button type="submit" className="w-6/12" disabled={isLoading}>
                  {isLoading ? "処理中..." : "確定"}
                </Button>
              </div>
            </form>
          </Form>
          {errorMessage && (
            <p className="text-center text-red-500">{errorMessage}</p>
          )}
        </div>
      )}

      {/* ローディングインジケーター */}
      {isLoading && (
        <div className="loading-overlay">
          <div className="spinner"></div>
          <div className="grid grid-cols-6 grid-rows-4 gap-3">
            <div className="col-span-6 row-span-3" />
            <div className="col-span-2" />
            <p className="text-center col-span-2 text-[1.5rem] font-bold">
              音声処理中です...
              <br />
              この処理には数分かかる場合があります
            </p>
          </div>

          <div className="w-full">
            <div className="spinner-box m-auto">
              <div className="pulse-container">
                <div className="pulse-bubble pulse-bubble-1"></div>
                <div className="pulse-bubble pulse-bubble-2"></div>
                <div className="pulse-bubble pulse-bubble-3"></div>
                <div className="pulse-bubble pulse-bubble-4"></div>
                <div className="pulse-bubble pulse-bubble-5"></div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
