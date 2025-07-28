Write-Host ""
Write-Host "==== [STEP 1] Convert QT files ====" -ForegroundColor Cyan
& .\convert_qt_files_to_py.ps1
if (-not $?)
{
    Write-Host "[FATAL] QT files conversion failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "==== [STEP 2] Generate/Sync Translations ====" -ForegroundColor Cyan
& .\generate_translations.ps1
if (-not $?)
{
    Write-Host "[FATAL] Translation generation failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "==== [STEP 3] Run main.py ====" -ForegroundColor Cyan
Set-Location ..
& .venv\Scripts\python.exe src/beauty_center/main.py
if (-not $?)
{
    Write-Host "[FATAL] main.py failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "==== ALL STEPS COMPLETED SUCCESSFULLY ====" -ForegroundColor Green
