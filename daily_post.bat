@echo off
REM 寿司職人ナビ 毎日自動投稿バッチ
REM Windows タスクスケジューラーに登録して毎日実行

REM APIキーを設定（初回のみ変更が必要）
set ANTHROPIC_API_KEY=ここにAPIキーを入力

REM ログファイル
set LOGFILE=C:\Users\81909\sushi-blog\auto_post_log.txt

echo [%DATE% %TIME%] 自動投稿開始 >> %LOGFILE%

cd /d C:\Users\81909\sushi-blog
python auto_post.py >> %LOGFILE% 2>&1

echo [%DATE% %TIME%] 自動投稿完了 >> %LOGFILE%
echo. >> %LOGFILE%
