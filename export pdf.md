```
markdown-pdf --css d:/repo/LawExam/style.css *.md
```

```
for %f in (*.md) do markdown-pdf --css d:/repo/LawExam/style.css "%f"
```

```
Get-ChildItem *.md | ForEach-Object {
  markdown-pdf --css d:/repo/LawExam/style.css $_.Name
}

```