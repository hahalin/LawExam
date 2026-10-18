# Python 環境設定

本專案使用 Conda 環境管理 Python 套件。

## 環境資訊

| 項目 | 值 |
|------|-----|
| 環境類型 | Conda |
| 環境名稱 | `tf_gpu_env` |
| Python 版本 | 3.12.4 |

## 執行 Python 的指令

### 建議方式：直接 Python 路徑

```powershell
C:/Users/User/anaconda3/envs/tf_gpu_env/python.exe
```

> ⚠️ 使用 `conda run` 在 PowerShell 中執行含中文輸出的腳本時，會出現亂碼或輸出消失的問題。**建議使用直接路徑**。

### 範例

```powershell
# 執行腳本
C:/Users/User/anaconda3/envs/tf_gpu_env/python.exe script.py

# 執行指令
C:/Users/User/anaconda3/envs/tf_gpu_env/python.exe -c "print('Hello')"
```

### 備選方式：conda run（不建議用於中文輸出場景）

```powershell
C:/Users/User/anaconda3/Scripts/conda.exe run -n tf_gpu_env --no-capture-output python
```

## 必要套件

### PDF 處理（exam-pdf-to-markdown）

```powershell
C:/Users/User/anaconda3/envs/tf_gpu_env/python.exe -m pip install pdfplumber -q
```

### HTML 處理（html-subtitle-to-markdown）

```powershell
C:/Users/User/anaconda3/envs/tf_gpu_env/python.exe -m pip install beautifulsoup4 -q
```

### EPUB 產生（markdown-to-epub）

```powershell
C:/Users/User/anaconda3/envs/tf_gpu_env/python.exe -m pip install ebooklib markdown -q
```

## 安裝所有套件

```powershell
C:/Users/User/anaconda3/envs/tf_gpu_env/python.exe -m pip install pdfplumber beautifulsoup4 ebooklib markdown -q
```

## 確認環境

```powershell
# 確認 Python 版本
C:/Users/User/anaconda3/envs/tf_gpu_env/python.exe --version

# 確認已安裝套件
C:/Users/User/anaconda3/envs/tf_gpu_env/python.exe -m pip list | Select-String "pdfplumber|beautifulsoup4|ebooklib|markdown"
```
