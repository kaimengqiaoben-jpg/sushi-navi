@echo off
REM タスクスケジューラーに毎日自動投稿を登録するスクリプト
REM 管理者権限で実行してください

echo 寿司職人ナビ 毎日自動投稿タスクを登録します...

REM 毎日 午前9:00 に実行
schtasks /create /tn "SushiNaviDailyPost" ^
  /tr "C:\Users\81909\sushi-blog\daily_post.bat" ^
  /sc daily ^
  /st 09:00 ^
  /f

if %ERRORLEVEL% == 0 (
    echo タスク登録成功！毎日09:00に自動投稿されます。
    echo タスク確認: schtasks /query /tn "SushiNaviDailyPost"
    echo タスク停止: schtasks /delete /tn "SushiNaviDailyPost" /f
) else (
    echo エラー: 管理者権限で実行してください
    echo 右クリック → 管理者として実行
)

pause
