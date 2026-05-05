# 詭鎮奇談（Arkham Horror）線上版 — 中文 fork

> 本專案是 [halogenandtoast/ArkhamHorror](https://github.com/halogenandtoast/ArkhamHorror) 的個人 fork，加入了一些在地化修正與 Windows 部署支援。  
> 原專案是一款在瀏覽器中運行的《詭鎮奇談：卡牌版》（Arkham Horror: The Card Game）開源實作，支援多人連線、牌組匯入、完整戰役流程。

---

## 這個 fork 做了什麼

### 1. 修復 Bug：40 張卡的技能檢定 race condition（2026-05-05）

跟原作者版本相比，這個 fork 修正了一批會讓玩家覺得「卡牌效果好像沒生效」的 bug，根因是同一個訊息佇列 race condition。

**戰鬥傷害沒正確結算：**
- fight 通過後，武器上「依檢定結果造成額外傷害」的效果常常不生效，敵人只吃到 1 點基礎傷害
- fight 失敗時，武器/事件「對自己造成傷害」的反噬效果也沒觸發
- 受影響卡牌（fight 通過加傷）：Beretta M1918、Bonesaw、Brand of Cthugha、Butterfly Swords (5)、Cosmic Flame、Cyclopean Hammer (5)、.41 Derringer、Hand Hook、Ice Pick (3)、Katana、Kukri、Machete、Sledgehammer (3)、Switchblade、Trusty Bullwhip、Enchanted Blade Guardian (3) 等
- 受影響卡牌（fight 失敗反噬）：Old Shotgun (2)、Sawed-Off Shotgun (5)、Shotgun (4)、Winchester Model 1912 (5)
- 特殊事件 / 技能：Custom Modifications、Glassing、Marksmanship (1)、Brute Force (1)、Vicious Blow (2)、Broken Bottle、Baseball Bat (2)

**調查時少拿線索：**
- investigate 通過後，「依檢定結果或條件多拿 1 個線索」的效果有時候沒生效，只拿到地點原本提供的數量
- 受影響卡牌：Chemistry Set、Mariner's Compass / (2)、Nautical Charts、Old Keyring (3)、Second Sight、Damning Testimony、Deduction (2)、Sharp Vision (1)

**修正內容：** 把 result handler（`PassedSkillTest` / `FailedSkillTest` 等）裡的 `skillTestModifier` 用 `priority` 包起來，確保 `DamageDealt` / `DamageDealtToInvestigator` / `DiscoveredClues` 等 modifier 比後續的 `EnemyDamage` / `DiscoverClues` 訊息更早進佇列。涉及 40 個 .hs 檔案。

完整變更紀錄請見 [`WINDOWS_DEPLOY.md` 的變更紀錄區](./WINDOWS_DEPLOY.md#變更紀錄)。

### 2. 修復 Bug：全滅調查員後無法替換（#3469）

當所有調查員都被擊敗時，後端會將他們移至 `killedInvestigators`，但前端仍在舊的 `game.investigators` 中查找，導致：
- `UpgradeDeck.vue` 找不到玩家，無法顯示「替換調查員」介面
- `StoryQuestion.vue`、`Question.vue`、`ExchangeTokens.vue` 的頭像查找 function 因 `undefined` 而 crash

**修正內容：**
- `UpgradeDeck.vue`：增加 `killedInvestigators` fallback 查找
- 其餘三個元件：增加 `null` 檢查，找不到時直接回傳預設頭像路徑

### 3. 修正圖片下載腳本（BusyBox 相容）

原作者的 `scripts/fetch-assets.sh` 使用 `stat` 取得檔案大小，但 Alpine / aws-cli 容器內的 BusyBox `stat` 不支援 `-c%s` 與 `-f%z` 參數，導致在 Docker 容器內執行下載時報錯。

**修正內容：** 增加 `wc -c` 作為 fallback，確保在各種 Linux 環境都能正常執行。

### 4. Windows x86_64 部署指南

原作者的 `docker-compose.yml` 預設會觸發 Haskell 後端編譯，在 Windows 一般 PC 上可能需要 **2～6 小時**。

**新增內容：**
- `docker-compose.windows.yml`：覆寫設定，直接使用原作者編好的多架構 Docker 映像檔（`amd64`），只替換前端
- `WINDOWS_DEPLOY.md`：完整步驟教學，包含「用 Docker 容器編譯前端，完全不用在 Windows 安裝 Node.js」、更新流程、變更紀錄

### 5. Dockerfile 編譯記憶體優化

原作者的 `Dockerfile` 用 `stack build -j4`，記憶體較小的機器（Docker 配 8 GB 左右）編譯到 `Entity.Arkham.Step` 之類的 Template Haskell 重模組會 OOM。

**修正內容：** 把 `-j4` 降為 `-j2`，並把同樣的 ghc-options 也傳給 `stack install`，讓低配機器也能順利從零 build。

### 6. 繁體中文翻譯持續補上

- 整套「Feast of Hemlock Vale」劇本繁中化
- 持續補上其他卡牌翻譯（賽拉斯·馬什、銘刻於石、珍妮·巴恩斯…）
- 前端遇到原文卡牌時自動疊上譯文 overlay

---

## 快速開始

### macOS / Linux（Apple Silicon / x86_64）

```bash
# 1. clone 這個 fork
git clone https://github.com/Matlin99/ArkhamHorror.git
cd ArkhamHorror

# 2. 產生資料庫密碼
openssl rand -base64 32 > config/postgres_password.txt

# 3. 啟動（會自動編譯，Mac ARM64 約 10～20 分鐘）
docker compose up

# 4. 開瀏覽器訪問 http://localhost:3000
```

### 卡片圖片（可選，約 1.3～2.9 GB）

遊戲可以完全不抓圖片，會自動從 CDN 載入。如果你想離線玩或加速讀取：

```bash
# 英文 + 中文（推薦）
docker compose --profile fetch-images run --rm fetch-images en+zh

# 全部語言
docker compose --profile fetch-images run --rm fetch-images all
```

圖片會存在 `frontend/public/img/`，抓完後 `docker compose restart web` 即可生效。

---

### Windows x86_64（Intel / AMD）

**核心概念：** 不編譯 Haskell 後端，直接拉原作者的 Docker 映像檔，只替換成我們修正過的前端。

#### 前置需求
- [Docker Desktop](https://www.docker.com/products/docker-desktop)（安裝時勾選 WSL2）
- [Git for Windows](https://git-scm.com/download/win)

#### 步驟

```powershell
# 1. clone 這個 fork
git clone https://github.com/Matlin99/ArkhamHorror.git
cd ArkhamHorror

# 2. 產生資料庫密碼
openssl rand -base64 32 > config/postgres_password.txt

# 3. （放卡片圖片到 frontend/public/img/arkham/...，或執行 fetch-images）
# docker compose --profile fetch-images run --rm fetch-images en+zh

# 4. 用 Docker 容器編譯前端（不用裝 Node.js！）
docker run --rm -v "${PWD}/frontend:/app" -w /app node:24.7.0-alpine sh -c "npm ci && npm run build"

# 5. 啟動
docker compose -f docker-compose.yml -f docker-compose.windows.yml up
```

打開 [http://localhost:3000](http://localhost:3000) 即可開始。

詳細說明請見 [`WINDOWS_DEPLOY.md`](./WINDOWS_DEPLOY.md)。

---

## 讓朋友從外網連進來（Cloudflare Tunnel）

如果你不想搞 VPS，最簡單的做法是用 Cloudflare Tunnel：

```bash
# macOS
brew install cloudflared
cloudflared tunnel --url http://localhost:3000

# Windows（下載 cloudflared.exe 後執行）
cloudflared.exe tunnel --url http://localhost:3000
```

執行後會給你一個 `https://xxxx.trycloudflare.com` 網址，直接丟給朋友即可。  
**注意：** 這個網址每次重啟 tunnel 都會變，如果要固定網址需要註冊 Cloudflare 帳號綁定 domain。

---

## 戰役進度與內容

原專案已實作以下內容：

- 玩家卡牌：2026 年以前全部卡牌
- 戰役：
  - 狂熱之夜（Night of the Zealot）+ Return to
  - 敦威治遺產（The Dunwich Legacy）+ Return to
  - 卡寇沙之路（The Path to Carcosa）+ Return to
  - 失落的年代（The Forgotten Age）+ Return to
  - 圓環祕語（The Circle Undone）+ Return to
  - 夢尋秘境（The Dream-Eaters）
  - 印斯茅斯陰謀（The Innsmouth Conspiracy）
  - 地球邊緣（Edge of the Earth）

---

## 技術棧

| 層級 | 技術 |
|------|------|
| 後端 API | Haskell (Servant) |
| 前端 | Vue 3 + TypeScript + Vite |
| 資料庫 | PostgreSQL 14 |
| 容器 | Docker / Docker Compose |

---

## 授權

本專案沿用原作者的授權條款。  
Arkham Horror 為 Fantasy Flight Games 之商標，本專案為粉絲非官方實作，無任何營利行為。

---

## 相關連結

- 原作者專案：[halogenandtoast/ArkhamHorror](https://github.com/halogenandtoast/ArkhamHorror)
- 線上牌組編輯器：[arkham.build](https://arkham.build)
- 官方牌組資料庫：[ArkhamDB](https://arkhamdb.com)
