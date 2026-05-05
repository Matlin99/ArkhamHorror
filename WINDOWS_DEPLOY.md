# Windows 部署指南 (x86_64)

> 本指南讓你在 Windows 電腦上跑這個專案，**不用編譯 Haskell 後端**（省幾小時），直接沿用作者編好的 Docker 映像檔，只替換掉前端程式碼。

---

## 前置準備

1. **Docker Desktop**  
   下載並安裝：[https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)  
   安裝時記得勾選 **Use WSL 2 instead of Hyper-V**（建議）。

2. **Git**（可選，如果你打算用 Git  clone）  
   下載：[https://git-scm.com/download/win](https://git-scm.com/download/win)

---

## 步驟 1：把程式碼弄上 Windows

### 方法一：Git clone（推薦，可追蹤版本）

在你的 Windows 上打開 PowerShell 或 Git Bash：

```powershell
# 先到你想要放專案的目錄
cd C:\Users\你的使用者名稱\Documents

# clone 你自己的 fork（請把 YOUR_USERNAME 換成你的 GitHub 帳號）
git clone https://github.com/YOUR_USERNAME/ArkhamHorror.git
cd ArkhamHorror
```

### 方法二：直接複製資料夾

如果你不想裝 Git，也可以直接把這台 Mac 上的 `~/ArkhamHorror` 資料夾壓縮後搬去 Windows（USB、SMB、雲端硬碟都可以）。  
**注意**：不需要搬 `frontend/public/img` 裡面的圖片（見步驟 2）。

---

## 步驟 2：準備卡片圖片

遊戲需要卡牌圖片，有兩種方式取得：

### 方式 A：從 Mac 搬過來（最快，如果你已經下載好了）

1. 在 Mac 上把 `~/ArkhamHorror/frontend/public/img` 整個資料夾壓縮：
   ```bash
   cd ~/ArkhamHorror
   tar czf arkham-images.tar.gz frontend/public/img
   ```
2. 把 `arkham-images.tar.gz` 傳到 Windows，解壓縮到同樣的路徑 `ArkhamHorror/frontend/public/img`。

### 方式 B：在 Windows 重新下載

如果你有穩定的網路，也可以在 Windows 直接執行：

```powershell
cd ArkhamHorror
docker compose --profile fetch-images run fetch-images zh
```

（把 `zh` 換成 `en` 如果你要英文圖片，或兩個都跑一次。）

---

## 步驟 3：編譯前端（含你自己的修改）

作者的 Docker 映像檔裡的前端是舊版，**不會包含你自己改的 bug fix**。  
我們要在 Windows 上重新編譯前端，然後掛載進去。

**最簡單的方法**：用 Docker 裡的 Node.js 來編譯，完全不用在 Windows 安裝 Node：

```powershell
cd ArkhamHorror

# 用跟作者一樣版本的 Node 容器來編譯前端
docker run --rm -v "${PWD}/frontend:/app" -w /app node:24.7.0-alpine sh -c "npm ci && npm run build"
```

這會產生 `frontend/dist/` 資料夾，裡面就是最新的前端靜態檔案。

> 如果你已經在 Windows 裝了 Node 24+，也可以直接 `cd frontend && npm install && npm run build`。

---

## 步驟 4：啟動服務

```powershell
cd ArkhamHorror
docker compose -f docker-compose.yml -f docker-compose.windows.yml up
```

等資料庫初始化完成（看到 `database system is ready to accept connections`），再打開瀏覽器訪問：

```
http://localhost:3000
```

---

## 步驟 5：關閉 / 重新啟動

- **關閉**：在 PowerShell 視窗按 `Ctrl + C`，或另開一個視窗執行：
  ```powershell
  cd ArkhamHorror
  docker compose -f docker-compose.yml -f docker-compose.windows.yml down
  ```
- **下次啟動**：直接再跑一次 `docker compose ... up`。

---

## 更新到新版

### 純前端更新（卡片翻譯、UI 修正）

只要重新跑步驟 3 編前端、重啟容器就好：

```powershell
cd ArkhamHorror
git pull
docker run --rm -v "${PWD}/frontend:/app" -w /app node:24.7.0-alpine sh -c "npm ci && npm run build"
docker compose -f docker-compose.yml -f docker-compose.windows.yml restart web
```

### 後端更新（Haskell 程式碼修正）

> **注意**：本指南預設用作者的 `halogenandtoast/arkham-horror:latest` 映像檔。
> 如果新版改動了 Haskell 後端（例如 race condition 修正），單純 `git pull` 沒有用，
> 必須換掉那個映像檔。下面三種方式擇一。

#### 方式 A：從 Mac 把映像檔傳過來（推薦，一次性）

在已經 build 好的 Mac 上：

```bash
cd ~/ArkhamHorror
docker save halogenandtoast/arkham-horror:latest -o arkham-horror.tar
# 檔案約 1.2 GB，傳到 Windows（USB / SMB / 雲端）
```

到 Windows：

```powershell
cd ArkhamHorror
git pull
docker load -i arkham-horror.tar
docker run --rm -v "${PWD}/frontend:/app" -w /app node:24.7.0-alpine sh -c "npm ci && npm run build"
docker compose -f docker-compose.yml -f docker-compose.windows.yml up -d
```

#### 方式 B：Windows 端從零 build（不需傳檔，但會編譯 2~6 小時）

```powershell
cd ArkhamHorror
git pull
docker compose build web
docker compose -f docker-compose.yml -f docker-compose.windows.yml up -d
```

> Docker Desktop → Settings → Resources，記憶體至少給 **10 GB**，否則 `Entity.Arkham.Step` 那種 TH 重模組會 OOM。

#### 方式 C：把自己的映像檔推到 Docker Hub / GHCR（適合常常更新）

Mac 上 tag 並 push：

```bash
docker tag halogenandtoast/arkham-horror:latest YOUR_DOCKERHUB/arkham-horror:latest
docker push YOUR_DOCKERHUB/arkham-horror:latest
```

把 `docker-compose.windows.yml` 裡的 `image:` 改成你的 tag，然後 Windows 端：

```powershell
docker compose pull web
docker compose -f docker-compose.yml -f docker-compose.windows.yml up -d
```

### 資料庫不會被影響

`docker compose up -d` 只 recreate `web` 容器，`db` 容器和它的 volume 都保留，遊戲存檔不會掉。

---

## 變更紀錄

### 2026-05-05

#### 修了什麼 bug（玩家會碰到的症狀）

**戰鬥傷害沒正確結算**：用武器發動 fight 檢定通過時，武器上「依檢定結果造成額外傷害」的效果常常不生效，敵人只吃到 1 點基礎傷害；或 fight 失敗時、武器/事件上「對自己造成傷害」的反噬效果也沒觸發。原因是傷害數值的 modifier 比 `EnemyDamage` 訊息晚進佇列，等套到敵人身上時傷害已經結算完了。

受影響的卡：

- **fight 通過後加傷**：Beretta M1918、Bonesaw、Brand of Cthugha (1)/(4)、Butterfly Swords (5)、Cosmic Flame、Cyclopean Hammer (5)、.41 Derringer / .41 Derringer (2)、Hand Hook、Ice Pick (3)、Katana、Kukri、Machete、Sledgehammer (3)、Switchblade / Switchblade (2)、Trusty Bullwhip / Trusty Bullwhip (Advanced)、Enchanted Blade (Guardian) (3)
- **fight 失敗反噬自身**：Old Shotgun (2)、Sawed-Off Shotgun (5)、Shotgun (4)、Winchester Model 1912 (5)
- **特殊事件 / 技能**：Custom Modifications、Glassing、Marksmanship (1)、Brute Force (1)、Vicious Blow (2)、Broken Bottle、Baseball Bat (2)

**調查時少拿線索**：investigate 通過後，「依檢定結果或條件多拿 1 個線索」的效果有時候沒生效，只拿到地點原本提供的數量。

受影響的卡：Chemistry Set、Mariner's Compass / (2)、Nautical Charts、Old Keyring (3)、Second Sight、Damning Testimony、Deduction (2)、Sharp Vision (1)

> 上述 40 張卡都是同一個 race condition 的不同表現。修法是把 result handler 裡的 `skillTestModifier` 用 `priority` 包起來，確保 modifier 比後續的 `EnemyDamage` / `DiscoverClues` 訊息更早進佇列。
>
> **此修正屬於後端 Haskell 變更**，請依「更新到新版 → 後端更新」的方式更新映像檔，光 `git pull` 沒用。

#### 其他更新

- **fix(docker)**：把 `Dockerfile` 的 `stack build` 從 `-j4` 降為 `-j2`，記憶體較小的機器（Docker 配 8GB 左右）才不會在編譯 `Entity.Arkham.Step` 之類的 TH 重模組時 OOM。
- **feat(zh)**：新增部分卡牌的繁體中文翻譯（賽拉斯·馬什、銘刻於石、珍妮·巴恩斯 等）。屬純前端，照「純前端更新」流程即可。

---

## 常見問題

### Q：為什麼不直接 `docker compose up --build`？
A：因為 `--build` 會從頭編譯 Haskell 後端，在一般 PC 上可能要 **2～6 小時**。我們改用作者編好的映像檔，只替換前端，5 分鐘內搞定。

### Q：卡片圖片太大，傳輸很慢？
A：你可以只傳「有改過的圖片」，或直接讓 Windows 端重新執行 `fetch-images` 下載（見步驟 2）。

### Q：我想改前端程式碼，改完要怎麼更新？
A：只要重新執行步驟 3 的 `docker run ... npm run build`，然後 `docker compose restart web` 即可。

### Q：怎麼讓朋友從外網連進來？
A：Windows 上同樣可以跑 Cloudflare Tunnel：
```powershell
# 下載 cloudflared（Windows 版）
# https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
cloudflared.exe tunnel --url http://localhost:3000
```
