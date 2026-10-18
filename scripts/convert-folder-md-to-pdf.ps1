Add-Type -AssemblyName System.Windows.Forms

$workspace = "D:/repo/LawExam"
$cssPath = Join-Path $workspace "style.css"

if (-not (Test-Path $cssPath)) {
    Write-Error "Cannot find style file: $cssPath"
    exit 1
}

$dialog = New-Object System.Windows.Forms.FolderBrowserDialog
$dialog.Description = "Select a folder to convert Markdown files"
$dialog.SelectedPath = $workspace

$result = $dialog.ShowDialog()
if ($result -ne [System.Windows.Forms.DialogResult]::OK -or [string]::IsNullOrWhiteSpace($dialog.SelectedPath)) {
    Write-Output "No folder selected. Cancelled."
    exit 0
}

$targetFolder = $dialog.SelectedPath
Write-Output "Target folder: $targetFolder"

$mdFiles = Get-ChildItem -Path $targetFolder -Filter "*.md" -File -Recurse

if ($mdFiles.Count -eq 0) {
    Write-Output "No .md files found in the selected folder."
    exit 0
}

$failed = @()

foreach ($file in $mdFiles) {
    Write-Output "Converting: $($file.FullName)"
    npx markdown-pdf "$($file.FullName)" -s "$cssPath"

    if ($LASTEXITCODE -ne 0) {
        $failed += $file.FullName
    }
}

if ($failed.Count -gt 0) {
    Write-Error "Failed to convert these files:"
    $failed | ForEach-Object { Write-Error " - $_" }
    exit 1
}

Write-Output "All files converted successfully. Count: $($mdFiles.Count)"
exit 0
