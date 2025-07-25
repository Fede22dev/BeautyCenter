Write-Host ""
Write-Host "==================== QT TRANSLATION AUTO-SYNC SCRIPT ====================" -ForegroundColor Yellow

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
if ($env:CI -ne 'true')
{
    $VenvScripts = Join-Path $ProjectRoot ".venv\Scripts"
    Write-Host "[ENV DETECT] Using local .venv: $VenvScripts"
}
else
{
    if (-not $env:VIRTUAL_ENV)
    {
        Write-Error "[ENV DETECT] CI true, but VIRTUAL_ENV is NOT set! Are you sure your virtual environment is active?" -ForegroundColor Red
        exit 1
    }

    $VenvScripts = Join-Path $env:VIRTUAL_ENV "Scripts"
    Write-Host "[ENV DETECT] Using VIRTUAL_ENV: $VenvScripts"
}

$TranslationDir = Join-Path $ProjectRoot "translations"
$LupdateExe = Join-Path $VenvScripts "pyside6-lupdate.exe"
$LreleaseExe = Join-Path $VenvScripts "pyside6-lrelease.exe"

# --- Tool check ---
Write-Host "[CHECK] Checking PySide6 tools location: $LupdateExe, $LreleaseExe" -ForegroundColor Cyan
if (-not (Test-Path $LupdateExe))
{
    Write-Error "[ERROR] pyside6-lupdate.exe NOT FOUND in '$VenvScripts'! Did you 'pip install pyside6-tools'?"; exit 1
}
if (-not (Test-Path $LreleaseExe))
{
    Write-Error "[ERROR] pyside6-lrelease.exe NOT FOUND in '$VenvScripts'! Did you 'pip install pyside6-tools'?"; exit 1
}

# --- Gather sources ---
Write-Host "`n[STEP 1/4] Searching for .py and .ui files in the project..." -ForegroundColor Green
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path  # define if not already
$SourceFiles = Get-ChildItem -Path $ProjectRoot -Recurse -Include *.py,*.ui `
    | Where-Object { $_.FullName -notmatch '\\.venv\\' -and $_.FullName -notmatch '__pycache__' }
if ($SourceFiles.Count -eq 0)
{
    Write-Error "[ERROR] No source files found! Exiting."; exit 1
}

$SrcListStr = $SourceFiles | ForEach-Object { "   -> $( $_.FullName )" } | Out-String
Write-Host "[INFO] Found $( $SourceFiles.Count ) sources:"
Write-Host $SrcListStr

# --- Ensure translations folder ---
if (-not (Test-Path $TranslationDir))
{
    Write-Host "[STEP 2/4] Creating translations directory: $TranslationDir" -ForegroundColor Green
    New-Item -ItemType Directory -Path $TranslationDir | Out-Null
}
else
{
    Write-Host "[STEP 2/4] Translations directory found: $TranslationDir" -ForegroundColor Green
}

# --- Ensure at least one .ts file exists, create 'it.ts' if none ---
Write-Host "[STEP 2/4] Checking for .ts translation files..." -ForegroundColor Green
$TsFiles = Get-ChildItem -Path $TranslationDir -Filter *.ts
if ($TsFiles.Count -eq 0)
{
    Write-Host "[INFO] No .ts files found! Creating base Italian translation file (it.ts)..." -ForegroundColor Yellow
    $NewTsFile = Join-Path $TranslationDir "it.ts"
    & $LupdateExe @($SourceFiles.FullName) -ts $NewTsFile
    if (-not $?)
    {
        Write-Error "[ERROR] Failed creating it.ts! Exiting."; exit 1
    }
    $TsFiles = Get-ChildItem -Path $TranslationDir -Filter *.ts
    Write-Host "[INFO] Created $NewTsFile"
}
else
{
    Write-Host "[INFO] .ts files found!"
}

Write-Host "`n[STEP 3/4] Updating and compiling all .ts translation files..." -ForegroundColor Green
foreach ($ts in $TsFiles)
{
    Write-Host "  [UPDATE] Updating $( $ts.Name ) with new/found strings..."
    & $LupdateExe @($SourceFiles.FullName) -ts $ts.FullName
    if (-not $?)
    {
        Write-Host "[ERROR] lupdate failed for $( $ts.Name )!" -ForegroundColor Red
        continue
    }
    $qmFile = [System.IO.Path]::ChangeExtension($ts.FullName, "qm")
    Write-Host "  [COMPILE] Compiling $( $ts.Name ) -> $([System.IO.Path]::GetFileName($qmFile) )"
    & $LreleaseExe $ts.FullName -qm $qmFile
    if (-not $?)
    {
        Write-Host "[ERROR] lrelease failed for $( $ts.Name )!" -ForegroundColor Red
    }
    else
    {
        Write-Host "      Result: OK"
    }
}

Write-Host "`n[COMPLETE] All .ts translation files updated and compiled to .qm!" -ForegroundColor Magenta
Write-Host "[INFO] Edit your .ts files with PySide Linguist GUI, e.g.:" -ForegroundColor Cyan
Write-Host "    .venv\Scripts\pyside6-linguist.exe translations\it.ts"
Write-Host "========================================================================="
