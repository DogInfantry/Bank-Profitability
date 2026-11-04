# Windows equivalent of the Makefile (no make, no WSL). Needs LibreOffice and a .venv with requirements.txt.
#   pipeline/build_windows.ps1            same steps as `make all`
#   pipeline/build_windows.ps1 -CiLocal   same as `make ci-local`: fresh clone of HEAD, committed files only
param([switch]$CiLocal, [switch]$SkipSite, [string]$Python)
$ErrorActionPreference = "Continue"  # native stderr warnings are not failures; exit codes are checked
$repo = Split-Path $PSScriptRoot -Parent
$py = if ($Python) { $Python } else { Join-Path $repo ".venv\Scripts\python.exe" }
if ($CiLocal) {
  $clone = Join-Path $repo ".ci-local"
  if (Test-Path $clone) { Remove-Item $clone -Recurse -Force }
  git clone -q $repo $clone
  & powershell -ExecutionPolicy Bypass -File (Join-Path $clone "pipeline\build_windows.ps1") -Python $py
  $status = $LASTEXITCODE
  Remove-Item $clone -Recurse -Force
  exit $status
}
Set-Location $repo
function Run([string[]]$a) {
  Write-Output ">> $($a -join ' ')"
  & $py -X utf8 @a  # -X utf8: the Windows default code page cannot encode the rupee sign
  if ($LASTEXITCODE -ne 0) { Write-Output "FAILED: $($a -join ' ')"; exit 1 }
}
foreach ($s in "hdfc_walk", "deposit_beta", "build_hdfc_model", "export_scenarios", "tornado", "build_hdfc_model", "export_scenarios",
               "call_topics", "warehouse", "run_sql") { Run @("-I", "pipeline/$s.py") }
foreach ($s in "decks/build_memo.py", "viz/build_dashboard.py", "viz/tableau/build_extracts.py", "pipeline/checks.py") { Run @("-I", $s) }
Run @("-m", "pytest", "-q", "-p", "no:cacheprovider", "tests")
Run @("-m", "ruff", "check", ".")
if (-not $SkipSite) {
  Run @("-I", "pipeline/export_site_data.py")
  Set-Location site
  foreach ($c in "npm ci --no-audit --no-fund", "npx vitest run", "npx vite build") {
    Write-Output ">> $c"; Invoke-Expression $c
    if ($LASTEXITCODE -ne 0) { Write-Output "FAILED: $c"; exit 1 }
  }
}
Write-Output "ALL STEPS PASSED"
