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
