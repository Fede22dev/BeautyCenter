Write-Host ""
Write-Host "==================== QT CONVERT UI TO PY ====================" -ForegroundColor Yellow

# [STEP 1/4] Get script root and define dirs
Write-Host "[STEP 1/4] Setting paths..." -ForegroundColor Magenta
$scriptPath = $PSScriptRoot
$inputDir = Join-Path $scriptPath "ui" "views"
$outputDir = Join-Path $scriptPath "ui" "generated_ui"

# [STEP 2/4] Ensure output directory exists
Write-Host "[STEP 2/4] Checking output directory..." -ForegroundColor Magenta
if (-not (Test-Path $outputDir))
{
    Write-Host "Output dir not found. Creating: $outputDir" -ForegroundColor Yellow
    New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
}
else
{
    Write-Host "Output dir exists: $outputDir" -ForegroundColor Cyan
}

# [STEP 3/4] Find PySide6 UIC command
Write-Host "[STEP 3/4] Searching for pyside6-uic..." -ForegroundColor Magenta
$uicCommand = ""
$uicInVenvWin = Join-Path $scriptPath ".venv" "Scripts" "pyside6-uic.exe"
$uicInVenvNix = Join-Path $scriptPath ".venv" "bin" "pyside6-uic"

if (Test-Path $uicInVenvWin)
{
    Write-Host "Found pyside6-uic in venv (Windows): $uicInVenvWin" -ForegroundColor Cyan
    $uicCommand = $uicInVenvWin
}
elseif (Test-Path $uicInVenvNix)
{
    Write-Host "Found pyside6-uic in venv (Unix): $uicInVenvNix" -ForegroundColor Cyan
    $uicCommand = $uicInVenvNix
}
elseif (Get-Command pyside6-uic -ErrorAction SilentlyContinue)
{
    Write-Host "Found pyside6-uic in system PATH." -ForegroundColor Cyan
    $uicCommand = "pyside6-uic"
}
else
{
    Write-Host "'pyside6-uic' NOT found in venv or system PATH." -ForegroundColor Red
    exit 1
}

# [STEP 4/4] Search .ui files and convert
Write-Host "[STEP 4/4] Searching for .ui files and launching conversion..." -ForegroundColor Magenta
$uiFiles = Get-ChildItem -Path $inputDir -Filter *.ui -Recurse

if (-not $uiFiles)
{
    Write-Host "No .ui files found in $inputDir. Nothing to do." -ForegroundColor Yellow
    exit 0
}

Write-Host ("Found {0} UI file(s) to convert." -f $uiFiles.Count) -ForegroundColor Cyan

foreach ($file in $uiFiles)
{
    $inputFile = $file.FullName
    $outputFile = Join-Path $outputDir ($file.BaseName + ".py")
    Write-Host ("Converting {0} ..." -f $file.Name) -ForegroundColor Cyan

    $process = Start-Process -FilePath $uicCommand `
                             -ArgumentList '-o', $outputFile, $inputFile `
                             -NoNewWindow -Wait -PassThru

    if ($process.ExitCode -eq 0)
    {
        Write-Host "Conversion OK -> $outputFile" -ForegroundColor Green
    }
    else
    {
        Write-Host "ERROR converting $inputFile (ExitCode: $( $process.ExitCode ))" -ForegroundColor Red
    }
}

Write-Host "`nPipeline completed: all UI files processed." -ForegroundColor Green
Write-Host "========================================================================="
