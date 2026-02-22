# 引き継ぎ書：サークル運営AIエージェント

## プロジェクト概要

北海道大学のサークル「未来開拓倶楽部」の心理ゼミ運営を支援するAIエージェントシステム。
Discordを起点にタスク管理・議事録作成・情報整理を行う。

## 設計思想（最重要）

**必要十分なシンプルさを最優先にすること。**
保守性よりバイブコーディングで直せる明快さを選ぶ。コードも思想も使い方も一貫させること。

### データの原則

- **データの正はNotion一箇所**
- ローカルファイルは読み取りキャッシュ専用
- 外部データ取得時はシステムがファイルに落として**メタデータのみAIに渡す**（プロンプトを汚さない）
- AIが中身を必要とするときは明示的にリクエストして取得する

### コンテナ構成（3つだけ）

```text
mcp      → Notion等への接続口（notion-mcp-server、HTTPトランスポート）
bot      → Discord Botのみ。薄い窓口に徹する
runner   → エージェントロジック全体 + ファイル置き場
```

### ファイルシステム（runnerのボリューム /data）

```text
/data/
  agent.md              ← システムプロンプト（AIが読む）
  skills/               ← frontmatter付きmarkdown。スキル・ナレッジ置き場
    knowledge.md        ← 組織情報（AIが書き換える）
    notion_schema.md    ← NotionDB構造（初回起動時にAIが自動生成）
  cache/                ← MCPで取得したデータのキャッシュ
  users/{user_id}/      ← ユーザーごとの作業ディレクトリ（スクリプト実行等）
```

### スキルの構造

frontmatterがメタデータ、本文がコンテンツ。
システムプロンプトにはYAMLのメタデータ一覧のみ注入し、AIは必要なスキルをread_fileで取得する。
NotionのYAMLプロパティ構造に合わせることで変換ロジックを薄くする。

```markdown
---
name: knowledge
description: サークルのナレッジ・組織情報
writable: true
---
本文...
```

### agent.mdの思想

- `<この組織>`と書いた箇所はknowledge.mdのnameフィールドで動的置換
- ツール一覧は起動時にMCPから動的取得して末尾に自動注入
- 最小限の記述のみ。AIが知らないと判断できないことだけ書く

## Discordの設計

### チャンネル構成

```text
[カテゴリ: AIエージェント]
  ├── {username}-chat    ← テキストチャンネル（コンテキストなし・単発）
  └── {username}-thread  ← フォーラムチャンネル（コンテキストあり）
        └── スレッド = セッション。作成時にモデル選択
```

カテゴリ単位でミュート・非表示にできるので購読管理はDiscord側に任せる。

### モデル選択

スレッド作成時にセレクトメニューで選択。現在はGemini Flash / Gemini Proのみ。

### 権限モデル

- フォーラムチャンネルごとに「読み込みON/OFF」「書き込みON/OFF」の2ボタン
- デフォルト：読み込みON・書き込みOFF
- 権限がない操作はシステムがDiscord上で確認UIを出し、許可されたら続行

## セッション管理（未解決の核心問題）

**現状の設計の歪み：**
「Discordのスレッド = セッション」という思想と、runnerがステートレスなHTTPで動いていることが矛盾している。

権限リトライ時にrunnerへ再POSTすると、Geminiのツールループ途中のcontentsが消えてループが最初から走り直す。Geminiが同じツールを再度呼ぶ保証はない。

**解決の方向性（未実装）：**
runnerがループ途中のcontentsをセッションID（スレッドID）で保持しておき、リトライ時に途中から再開できるようにする。
あるいは、会話のセッション管理をrunnerに寄せてDiscordのスレッドIDをキーに状態を持つ。

## データベース（SQLite：/data/db.sqlite3）

```sql
users (
  id TEXT PRIMARY KEY,      -- 内部の統一UUID
  discord_id TEXT UNIQUE,
  notion_id TEXT,
  line_id TEXT,             -- 将来のLINE統合用
  created_at TEXT
)

channels (
  user_id TEXT PRIMARY KEY,
  category_id TEXT,
  text_channel_id TEXT,
  forum_channel_id TEXT
)

threads (
  thread_id TEXT PRIMARY KEY,
  user_id TEXT,
  model TEXT DEFAULT 'gemini-flash',
  read_ok INTEGER DEFAULT 1,
  write_ok INTEGER DEFAULT 0
)
```

## MCPサーバー

- `@notionhq/notion-mcp-server` を使用
- `--transport http --port 3000` で起動（Streamable HTTP対応）
- エンドポイント：`http://mcp:3000/mcp`
- 認証：AuthorizationヘッダーにBearerトークン + mcp-session-idヘッダー
- MCPの全ツール結果はキャッシュして、AIにはメタデータのみ返す

## 環境変数

```text
NOTION_TOKEN=
MCP_AUTH_TOKEN=    # openssl rand -hex 32 で生成
DISCORD_BOT_TOKEN=
GEMINI_API_KEY=
```

## 現状のコードの問題点

以下の問題があり、**スクラッチで書き直すことを推奨する。**

1. **runnerの責務が広すぎる**：FastAPIサーバー・Geminiエージェント・ツール実行・MCPクライアント・キャッシュ・セッション管理を全部持っている
2. **セッション問題**：上記の通り未解決
3. **context.py**：bot/src/に原因不明で存在するファイルがある
4. **permit_callback_id**：botからrunnerに送られているが、runner側で未使用
5. **agent.mdの初期配置問題**：runner/dataはボリュームで初回空のため、Dockerfileでseedするかimageに焼き込む必要がある
6. **runner/data/notion/**：cache/に統合されたはずの古いディレクトリが残っている

## 書き直しの指針

- botはDiscordのI/Oだけ。runnerの/chatを叩いて返すだけ
- runnerはセッション（スレッドID）をキーに状態を持ち、Geminiループを管理する
- MCPはrunnerからのみ叩く。botはMCPを知らない
- 権限確認はrunnerがneed_permissionを返してbotが判断する（この流れは正しい）
- ファイルシステムの構造とスキルの設計はそのまま使える
- DBスキーマはそのまま使える
- agent.mdの内容と思想はそのまま使える
