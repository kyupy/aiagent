# aiagent (minimal rewrite scaffold)

`HANDOVER.md` の設計方針に沿って、以下の最小実装を追加しました。

- `runner`: スレッドIDをキーにしたセッション保持 + `/chat` HTTP API
- `bot`: runner `/chat` を呼ぶ最小クライアント
- `db`: SQLite スキーマと初期化スクリプト

## Run runner

```bash
PYTHONPATH=runner/src python -m runner.http_api
```

## Call from bot CLI

```bash
PYTHONPATH=bot/src python -m bot.cli --thread-id t1 --user-id u1 --text "hello"
```

## Init DB

```bash
python -m db.init_db --db data/db.sqlite3 --schema db/schema.sql
```
