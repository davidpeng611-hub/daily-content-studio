$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$Dirs = @(
  "input",
  "output",
  "素材库",
  "今日推文",
  "local"
)

foreach ($Dir in $Dirs) {
  $Path = Join-Path $Root $Dir
  if (-not (Test-Path $Path)) {
    New-Item -ItemType Directory -Path $Path | Out-Null
    Write-Host "created $Path"
  } else {
    Write-Host "exists  $Path"
  }
}

$Example = Join-Path $Root "config\workflow.example.json"
$Local = Join-Path $Root "local\workflow.local.json"
if ((Test-Path $Example) -and -not (Test-Path $Local)) {
  Copy-Item $Example $Local
  Write-Host "created $Local"
}

Write-Host ""
Write-Host "Next:"
Write-Host "  python .\scripts\doctor.py"

