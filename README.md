# aiagent

`HANDOVER.md` の設計方針に沿って、runner をスレッドIDベースで再開可能にする最小実装です。

## What is included

- `runner`
  - `/chat` : チャット処理
  - `/permissions` : read/write 権限更新
  - `/health` : ヘルスチェック
  - `thread_id` ごとのセッションをメモリ保持しつつ、SQLiteにスナップショット/履歴を保存
- `bot`
  - runner のHTTP APIを呼び出す最小クライアント
  - CLIから chat / permissions を送信可能
- `db`
  - `users/channels/threads/session_events` スキーマ
  - 初期化スクリプト

## Run runner

```bash
python -m db.init_db --db data/db.sqlite3 --schema db/schema.sql
RUNNER_DB_PATH=data/db.sqlite3 PYTHONPATH=runner/src python -m runner.http_api
```

## Bot CLI examples

```bash
PYTHONPATH=bot/src python -m bot.cli chat --thread-id t1 --user-id u1 --text "hello"
PYTHONPATH=bot/src python -m bot.cli permissions --thread-id t1 --user-id u1 --write-ok true
PYTHONPATH=bot/src python -m bot.cli chat --thread-id t1 --user-id u1 --text "[WRITE] update"
```
