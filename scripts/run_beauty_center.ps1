$scriptStart = Get-Date
Write-Host ""
Write-Host "==== [STEP 1] Convert QT files ====" -ForegroundColor Cyan
Write-Host "Script started at: $($scriptStart.ToString('HH:mm:ss') )"

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
Write-Host "==== [STEP 3] Run start_bc.py ====" -ForegroundColor Cyan

Set-Location ..
& .venv\Scripts\python.exe start_bc.py

if (-not $?)
{
    Write-Host "[FATAL] main.py failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
$scriptEnd = Get-Date
$duration = $scriptEnd - $scriptStart
Write-Host "Script finished at: $($scriptEnd.ToString('HH:mm:ss') )"
Write-Host ("Total elapsed time: {0:mm\:ss} (mm:ss)" -f $duration) -ForegroundColor Blue
Write-Host "==== ALL STEPS COMPLETED SUCCESSFULLY ====" -ForegroundColor Green
