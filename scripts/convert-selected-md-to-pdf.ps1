Add-Type -AssemblyName System.Windows.Forms

$workspace = "D:/repo/LawExam"
$cssPath = Join-Path $workspace "style.css"

if (-not (Test-Path $cssPath)) {
    Write-Error "Cannot find style file: $cssPath"
    exit 1
}

$dialog = New-Object System.Windows.Forms.OpenFileDialog
$dialog.InitialDirectory = $workspace
$dialog.Multiselect = $true
$dialog.Filter = "Markdown files (*.md)|*.md"
$dialog.Title = "Select Markdown files to convert"

$result = $dialog.ShowDialog()
if ($result -ne [System.Windows.Forms.DialogResult]::OK -or $dialog.FileNames.Count -eq 0) {
    Write-Output "No files selected. Cancelled."
    exit 0
}

$failed = @()

foreach ($file in $dialog.FileNames) {
    Write-Output "Converting: $file"
    npx markdown-pdf "$file" -s "$cssPath"

    if ($LASTEXITCODE -ne 0) {
        $failed += $file
    }
}

if ($failed.Count -gt 0) {
    Write-Error "Failed to convert these files:"
    $failed | ForEach-Object { Write-Error " - $_" }
    exit 1
}

Write-Output "All files converted successfully."
exit 0
