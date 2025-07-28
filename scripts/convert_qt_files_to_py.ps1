Write-Host ""
Write-Host "==================== QT CONVERT UI TO PY + QRC ====================" -ForegroundColor Yellow

# [STEP 1/6] Get script root and define dirs
Write-Host "[STEP 1/6] Setting paths..." -ForegroundColor Magenta

$ScriptPath  = $PSScriptRoot
$ProjectRoot = Split-Path $ScriptPath -Parent

$inputDir        = Join-Path $ProjectRoot "src" "beauty_center" "ui" "views"
$outputDir       = Join-Path $ProjectRoot "src" "beauty_center" "ui" "generated_ui"
$resourcesDir    = Join-Path $ProjectRoot "src" "beauty_center" "resources"
$qrcDir          = Join-Path $resourcesDir "qrc"
$iconsQrc        = Join-Path $qrcDir "icons.qrc"
$imagesQrc       = Join-Path $qrcDir "images.qrc"
$stylesQrc       = Join-Path $qrcDir "styles.qrc"
$generatedQrcDir = Join-Path $resourcesDir "generated_qrc"

# [STEP 2/6] Ensure output directories exist
Write-Host "[STEP 2/6] Checking output directories..." -ForegroundColor Magenta
foreach ($dir in @($outputDir, $generatedQrcDir))
{
    if (-not (Test-Path $dir))
    {
        Write-Host "Output dir not found. Creating: $dir" -ForegroundColor Yellow
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }
    else
    {
        Write-Host "Output dir exists: $dir" -ForegroundColor Cyan
    }
}

# [STEP 3/6] CLEAN all old generated files
Write-Host "[STEP 3/6] Cleaning old generated files..." -ForegroundColor Magenta
# Delete ALL .py in UI generated dir
if (Test-Path $outputDir)
{
    $uiToDelete = Get-ChildItem -Path $outputDir -Filter *.py -File
    foreach ($f in $uiToDelete)
    {
        Write-Host "Deleting: $( $f.FullName )" -ForegroundColor DarkYellow
        Remove-Item $f.FullName -Force
    }
}

# Delete ALL _rc.py files in generated_qrc
if (Test-Path $generatedQrcDir)
{
    $qrcToDelete = Get-ChildItem -Path $generatedQrcDir -Filter *_rc.py -File
    foreach ($f in $qrcToDelete)
    {
        Write-Host "Deleting: $( $f.FullName )" -ForegroundColor DarkYellow
        Remove-Item $f.FullName -Force
    }
}

# [STEP 4/6] Find PySide6 UIC and RCC commands
Write-Host "[STEP 4/6] Searching for pyside6-uic and pyside6-rcc..." -ForegroundColor Magenta
$uicCommand = ""
$rccCommand = ""

$venvScriptsWin = Join-Path $ProjectRoot ".venv" "Scripts"
$venvBinNix     = Join-Path $ProjectRoot ".venv" "bin"
$uicInVenvWin   = Join-Path $venvScriptsWin "pyside6-uic.exe"
$uicInVenvNix   = Join-Path $venvBinNix "pyside6-uic"
$rccInVenvWin   = Join-Path $venvScriptsWin "pyside6-rcc.exe"
$rccInVenvNix   = Join-Path $venvBinNix "pyside6-rcc"

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
elseif(Get-Command pyside6-uic -ErrorAction SilentlyContinue)
{
    Write-Host "Found pyside6-uic in system PATH." -ForegroundColor Cyan
    $uicCommand = "pyside6-uic"
}
else
{
    Write-Host "'pyside6-uic' NOT found in venv or system PATH." -ForegroundColor Red
    exit 1
}

if (Test-Path $rccInVenvWin)
{
    Write-Host "Found pyside6-rcc in venv (Windows): $rccInVenvWin" -ForegroundColor Cyan
    $rccCommand = $rccInVenvWin
}
elseif (Test-Path $rccInVenvNix)
{
    Write-Host "Found pyside6-rcc in venv (Unix): $rccInVenvNix" -ForegroundColor Cyan
    $rccCommand = $rccInVenvNix
}
elseif (Get-Command pyside6-rcc -ErrorAction SilentlyContinue)
{
    Write-Host "Found pyside6-rcc in system PATH." -ForegroundColor Cyan
    $rccCommand = "pyside6-rcc"
}
else
{
    Write-Host "'pyside6-rcc' NOT found in venv or system PATH." -ForegroundColor Red
    exit 1
}

# [STEP 5/6] Search .ui files and convert
Write-Host "[STEP 5/6] Searching for .ui files and launching conversion..." -ForegroundColor Magenta

$uiFiles = Get-ChildItem -Path $inputDir -Filter *.ui -Recurse
if (-not $uiFiles)
{
    Write-Host "No .ui files found in $inputDir. Nothing to do." -ForegroundColor Yellow
}
else
{
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
}

# [STEP 6/6] Compile .qrc files into Python resource modules in 'generated_qrc'
Write-Host "[STEP 6/6] Compiling .qrc resource files..." -ForegroundColor Magenta
$compiledQrcFiles = @{ }
foreach ($qrcFile in @($iconsQrc, $imagesQrc, $stylesQrc))
{
    if (Test-Path $qrcFile)
    {
        $qrcBaseName = [System.IO.Path]::GetFileNameWithoutExtension($qrcFile)
        $outputQrcPy = Join-Path $generatedQrcDir ("{0}_rc.py" -f $qrcBaseName)
        $qrcWorkingDir = Split-Path $qrcFile
        # Get the output as an absolute path (for Start-Process from different dir)
        $absOutputQrcPy = [System.IO.Path]::GetFullPath($outputQrcPy)
        $qrcFileName = Split-Path $qrcFile -Leaf
        Write-Host ("Compiling {0} in {1} -> {2}" -f $qrcFile, $qrcWorkingDir, $absOutputQrcPy) -ForegroundColor Yellow
        $process = Start-Process -FilePath $rccCommand `
                    -WorkingDirectory $qrcWorkingDir `
                    -ArgumentList $qrcFileName, "-o", $absOutputQrcPy `
                    -NoNewWindow -Wait -PassThru
        if ($process.ExitCode -eq 0)
        {
            Write-Host "QRC Compile OK -> $absOutputQrcPy" -ForegroundColor Green
            $compiledQrcFiles[$qrcFile] = $absOutputQrcPy
        }
        else
        {
            Write-Host "ERROR compiling $qrcFile (ExitCode: $( $process.ExitCode ))" -ForegroundColor Red
        }
    }
    else
    {
        Write-Host ("Resource file not found: {0}" -f $qrcFile) -ForegroundColor Red
    }
}

Write-Host "`nPipeline completed: all UI and QRC files processed." -ForegroundColor Green
Write-Host "=========================================================================" -ForegroundColor Yellow
