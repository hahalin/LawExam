# Python 環境設定

本專案使用 Conda 環境管理 Python 套件。

## 環境資訊

| 項目 | 值 |
|------|-----|
| 環境類型 | Conda |
| 環境名稱 | `tf_gpu_env` |
| Python 版本 | 3.12.4 |

## 執行 Python 的指令前綴

在終端機執行 Python 腳本時，使用以下前綴：

```powershell
C:/Users/User/anaconda3/Scripts/conda.exe run -n tf_gpu_env --no-capture-output python
```

### 範例

```powershell
# 執行腳本
C:/Users/User/anaconda3/Scripts/conda.exe run -n tf_gpu_env --no-capture-output python script.py

# 執行指令
C:/Users/User/anaconda3/Scripts/conda.exe run -n tf_gpu_env --no-capture-output python -c "print('Hello')"
```

## 必要套件

### PDF 處理（exam-pdf-to-markdown）

```powershell
C:/Users/User/anaconda3/Scripts/conda.exe run -n tf_gpu_env --no-capture-output python -m pip install pdfplumber -q
```

### HTML 處理（html-subtitle-to-markdown）

```powershell
C:/Users/User/anaconda3/Scripts/conda.exe run -n tf_gpu_env --no-capture-output python -m pip install beautifulsoup4 -q
```

## 安裝所有套件

```powershell
C:/Users/User/anaconda3/Scripts/conda.exe run -n tf_gpu_env --no-capture-output python -m pip install pdfplumber beautifulsoup4 -q
```

## 確認環境

```powershell
# 確認 Python 版本
C:/Users/User/anaconda3/Scripts/conda.exe run -n tf_gpu_env --no-capture-output python --version

# 確認已安裝套件
C:/Users/User/anaconda3/Scripts/conda.exe run -n tf_gpu_env --no-capture-output python -m pip list | Select-String "pdfplumber|beautifulsoup4"
```
