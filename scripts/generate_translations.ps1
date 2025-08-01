$scriptStart = Get-Date
Write-Host ""
Write-Host "==================== QT TRANSLATION AUTO-SYNC SCRIPT ====================" -ForegroundColor Yellow
Write-Host "Script started at: $($scriptStart.ToString('HH:mm:ss') )"

# [INFO] Get script *real* root (.. up from scripts/)
$ScriptPath = $PSScriptRoot
$ProjectRoot = Split-Path $ScriptPath -Parent

Write-Host ""
Write-Host "[INFO] Script dir   : $ScriptPath"
Write-Host "[INFO] Project root : $ProjectRoot"

$VenvScripts = Join-Path $ProjectRoot ".venv\Scripts"

if (-not (Test-Path $VenvScripts))
{
    Write-Error "[ERROR] .venv\Scripts not found! Did you create and activate the virtual environment in the project folder?"
    exit 1
}

Write-Host "[ENV DETECT] Using .venv path: $VenvScripts"

$TranslationDir = Join-Path $ProjectRoot "translations"
$GeneratedQmDir = Join-Path $TranslationDir "generated_qm"
$LupdateExe = Join-Path $VenvScripts "pyside6-lupdate.exe"
$LreleaseExe = Join-Path $VenvScripts "pyside6-lrelease.exe"

# --- Tool check ---
Write-Host ""
Write-Host "[CHECK] Checking PySide6 tools location: $LupdateExe, $LreleaseExe" -ForegroundColor Cyan

if (-not (Test-Path $LupdateExe))
{
    Write-Error "[ERROR] pyside6-lupdate.exe NOT FOUND in '$VenvScripts'! Did you 'pip install pyside6-tools'?";
    exit 1
}
if (-not (Test-Path $LreleaseExe))
{
    Write-Error "[ERROR] pyside6-lrelease.exe NOT FOUND in '$VenvScripts'! Did you 'pip install pyside6-tools'?";
    exit 1
}

# --- Step 0: CLEAN all old generated .qm files ---
Write-Host ""
Write-Host "[CLEAN] Deleting all old .qm files in $GeneratedQmDir..." -ForegroundColor Magenta

if (Test-Path $GeneratedQmDir)
{
    $qmToDelete = Get-ChildItem -Path $GeneratedQmDir -Filter *.qm -File

    foreach ($f in $qmToDelete)
    {
        Write-Host "Deleting: $( $f.FullName )" -ForegroundColor DarkYellow
        Remove-Item $f.FullName -Force
    }
}

Write-Host ""
Write-Host "[STEP 1/4] Searching for .py and .ui files in the project..." -ForegroundColor Green

$SourceFiles = Get-ChildItem -Path $ProjectRoot -Recurse -Include *.py,*.ui |
        Where-Object {
            $_.FullName -notmatch '\\.venv\\' -and
                    $_.FullName -notmatch '__pycache__' -and
                    $_.FullName -notmatch 'generated_qrc' -and
                    ($_.Name -notlike 'test_*') -and
                    ($_.Extension -ne '.spec')
        }

if ($SourceFiles.Count -eq 0)
{
    Write-Error "[ERROR] No source files found! Exiting."; exit 1
}

$SrcListStr = $SourceFiles | ForEach-Object { "   -> $( $_.FullName )" } | Out-String
Write-Host "[INFO] Found $( $SourceFiles.Count ) sources:"
Write-Host $SrcListStr

foreach ($dir in @($TranslationDir, $GeneratedQmDir))
{
    if (-not (Test-Path $dir))
    {
        Write-Host "[STEP 2/4] Creating directory: $dir" -ForegroundColor Green
        New-Item -ItemType Directory -Path $dir | Out-Null
    }
    else
    {
        Write-Host ("[STEP 2/4] Directory found: {0}" -f $dir) -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "[STEP 2/3] Checking for .ts translation files..." -ForegroundColor Green

$TsFiles = Get-ChildItem -Path $TranslationDir -Filter *.ts

# Prepare argument arrays for processes
$SourcePathsArgs = @()
foreach ($src in $SourceFiles)
{
    $SourcePathsArgs += $src.FullName
}

if ($TsFiles.Count -eq 0)
{
    Write-Host "[INFO] No .ts files found! Creating base Italian translation file (it.ts)..." -ForegroundColor Yellow
    $NewTsFile = Join-Path $TranslationDir "it.ts"
    $lupdateArgs = @($SourcePathsArgs + @("-ts", $NewTsFile))
    Write-Host ">> $LupdateExe $( $lupdateArgs -join ' ' )" -ForegroundColor Cyan
    $process = Start-Process -FilePath $LupdateExe -ArgumentList $lupdateArgs -NoNewWindow -Wait -PassThru

    if ($process.ExitCode -ne 0)
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

Write-Host ""
Write-Host "[STEP 3/3] Updating and compiling all .ts translation files..." -ForegroundColor Green

foreach ($ts in $TsFiles)
{
    Write-Host "  [UPDATE] Updating $( $ts.Name ) with new/found strings..."
    $lupdateArgs = @($SourcePathsArgs + @("-ts", $ts.FullName))
    Write-Host ">> $LupdateExe $( $lupdateArgs -join ' ' )" -ForegroundColor DarkGray
    $process = Start-Process -FilePath $LupdateExe -ArgumentList $lupdateArgs -NoNewWindow -Wait -PassThru

    if ($process.ExitCode -ne 0)
    {
        Write-Host "[ERROR] lupdate failed for $( $ts.Name )!" -ForegroundColor Red
        continue
    }

    $qmFileName = [System.IO.Path]::GetFileNameWithoutExtension($ts.Name) + ".qm"
    $qmFile = Join-Path $GeneratedQmDir $qmFileName
    Write-Host "  [COMPILE] Compiling $( $ts.Name ) -> generated_qm\$qmFileName"
    $lreleaseArgs = @($ts.FullName, "-qm", $qmFile)
    Write-Host ">> $LreleaseExe $( $lreleaseArgs -join ' ' )" -ForegroundColor DarkGray
    $process2 = Start-Process -FilePath $LreleaseExe -ArgumentList $lreleaseArgs -NoNewWindow -Wait -PassThru

    if ($process2.ExitCode -ne 0)
    {
        Write-Host "[ERROR] lrelease failed for $( $ts.Name )!" -ForegroundColor Red
    }
    else
    {
        Write-Host "      Result: OK"
    }
}

Write-Host ""
$scriptEnd = Get-Date
$duration = $scriptEnd - $scriptStart
Write-Host "Script finished at: $($scriptEnd.ToString('HH:mm:ss') )"
Write-Host ("Total elapsed time: {0:mm\:ss} (mm:ss)" -f $duration) -ForegroundColor Blue
Write-Host "[COMPLETE] All .ts translation files updated and compiled to .qm in generated_qm!" -ForegroundColor Magenta
Write-Host "[INFO] Edit your .ts files with PySide Linguist GUI, e.g.:" -ForegroundColor Cyan
Write-Host "    .venv\Scripts\pyside6-linguist.exe translations\it.ts"
Write-Host "=========================================================================" -ForegroundColor Yellow
