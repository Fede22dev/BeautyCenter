$scriptStart = Get-Date
Write-Host ""
Write-Host "================= QT UI + QRC -> PY BUILD PIPELINE =================" -ForegroundColor Yellow
Write-Host "Script started at: $($scriptStart.ToString('HH:mm:ss') )"

# --- [STEP 1/7] Define directory structure
Write-Host ""
Write-Host "[STEP 1/7] Setting up paths..." -ForegroundColor Magenta

$ScriptPath = $PSScriptRoot
$ProjectRoot = Split-Path $ScriptPath -Parent
$inputDir = Join-Path $ProjectRoot "src" "ui" "views"
$outputDir = Join-Path $ProjectRoot "src" "ui" "generated_ui"
$resourcesDir = Join-Path $ProjectRoot "src" "resources"
$qrcDir = Join-Path $resourcesDir "qrc"
$generatedQrcDir = Join-Path $resourcesDir "generated_qrc"

# List of all QRC file paths
$qrcFiles = @(
    (Join-Path $qrcDir "icons.qrc"), # Path to icons QRC
    (Join-Path $qrcDir "images.qrc"), # Path to images QRC
    (Join-Path $qrcDir "styles.qrc")     # Path to styles QRC
)

# --- [STEP 2/7] Ensure output directories exist
Write-Host ""
Write-Host "[STEP 2/7] Ensuring output directories exist..." -ForegroundColor Magenta

foreach ($dir in @($outputDir, $generatedQrcDir))
{
    if (-not (Test-Path $dir))
    {
        Write-Host "Creating missing dir: $dir" -ForegroundColor Yellow
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }
    else
    {
        Write-Host "Output dir exists: $dir" -ForegroundColor Cyan
    }
}

# --- [STEP 3/7] Clean old generated files (UI and _rc.py)
Write-Host ""
Write-Host "[STEP 3/7] Cleaning old build files..." -ForegroundColor Magenta

# Remove old UI Python files
if (Test-Path $outputDir)
{
    $uiFiles = Get-ChildItem -Path $outputDir -Filter *.py -File
    if ($uiFiles)
    {
        Write-Host "Deleting UI Python files in ${outputDir}: " -ForegroundColor DarkYellow

        foreach ($file in $uiFiles)
        {
            Write-Host "  - $( $file.FullName )" -ForegroundColor DarkYellow
        }

        $uiFiles | Remove-Item -Force
    }
    else
    {
        Write-Host "No UI Python files to delete in $outputDir." -ForegroundColor DarkYellow
    }
}

# Remove old resource Python files in generated_qrc
if (Test-Path $generatedQrcDir)
{
    $rcFiles = Get-ChildItem -Path $generatedQrcDir -Filter *_rc.py -File
    if ($rcFiles)
    {
        Write-Host "Deleting resource Python files in ${generatedQrcDir}: " -ForegroundColor DarkYellow

        foreach ($file in $rcFiles)
        {
            Write-Host "  - $( $file.FullName )" -ForegroundColor DarkYellow
        }

        $rcFiles | Remove-Item -Force
    }
    else
    {
        Write-Host "No resource Python files to delete in $generatedQrcDir." -ForegroundColor DarkYellow
    }
}
# --- [STEP 4/7] Find PySide6 tools
Write-Host ""
Write-Host "[STEP 4/7] Locating pyside6-uic and pyside6-rcc..." -ForegroundColor Magenta

function Find-Tool($winPath, $nixPath, $toolName)
{
    if (Test-Path $winPath)
    {
        return $winPath
    }

    if (Test-Path $nixPath)
    {
        return $nixPath
    }

    $tool = Get-Command $toolName -ErrorAction SilentlyContinue

    if ($tool)
    {
        return $tool.Path
    }

    throw "'$toolName' NOT found in virtualenv or system PATH."
}

$venvScriptsWin = Join-Path $ProjectRoot ".venv" "Scripts"
$venvBinNix = Join-Path $ProjectRoot ".venv" "bin"

$uicCommand = Find-Tool (Join-Path $venvScriptsWin "pyside6-uic.exe") (Join-Path $venvBinNix "pyside6-uic") "pyside6-uic"
$rccCommand = Find-Tool (Join-Path $venvScriptsWin "pyside6-rcc.exe") (Join-Path $venvBinNix "pyside6-rcc") "pyside6-rcc"

Write-Host "Found tools:" -ForegroundColor Green
Write-Host "  UIC: $uicCommand" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  RCC: $rccCommand" -ForegroundColor DarkGray
Write-Host ""

# --- [STEP 5/7] Convert all .ui files to Python
Write-Host ""
Write-Host "[STEP 5/7] Converting .ui files to .py..." -ForegroundColor Magenta

$uiFiles = Get-ChildItem -Path $inputDir -Filter *.ui -Recurse

foreach ($file in $uiFiles)
{
    $inputFile = $file.FullName
    $outputFile = Join-Path $outputDir ("{0}.py" -f $file.BaseName)
    $process = Start-Process -FilePath $uicCommand `
        -ArgumentList '-o', $outputFile, $inputFile `
        -NoNewWindow -Wait -PassThru

    if ($process.ExitCode -eq 0)
    {
        Write-Host "Converted: $( $file.Name ) -> $outputFile" -ForegroundColor Green
    }
    else
    {
        Write-Host "ERROR converting $inputFile (ExitCode: $( $process.ExitCode ))" -ForegroundColor Red
    }
}

# --- [STEP 6/7] Compile all .qrc files to Python resource modules
Write-Host ""
Write-Host "[STEP 6/7] Compiling QRC resource files..." -ForegroundColor Magenta

foreach ($qrcFile in $qrcFiles)
{
    if (Test-Path $qrcFile)
    {
        $qrcBaseName = [System.IO.Path]::GetFileNameWithoutExtension($qrcFile)
        $outputQrcPy = Join-Path $generatedQrcDir ("{0}_rc.py" -f $qrcBaseName)
        $qrcFileName = Split-Path $qrcFile -Leaf
        $absOutputQrcPy = [System.IO.Path]::GetFullPath($outputQrcPy)
        $process = Start-Process -FilePath $rccCommand `
            -WorkingDirectory (Split-Path $qrcFile) `
            -ArgumentList $qrcFileName, "-o", $absOutputQrcPy `
            -NoNewWindow -Wait -PassThru

        if ($process.ExitCode -eq 0)
        {
            Write-Host "QRC Compiled: $qrcFile -> $absOutputQrcPy" -ForegroundColor Green
        }
        else
        {
            Write-Host "ERROR compiling $qrcFile (ExitCode: $( $process.ExitCode ))" -ForegroundColor Red
        }
    }
    else
    {
        Write-Host "Resource file not found: $qrcFile" -ForegroundColor Red
    }
}

# --- [STEP 7/7] Patch all generated UI files to fix QRC resource imports
Write-Host ""
Write-Host ("[STEP 7/7] Patching resource imports (e.g., icons_rc, images_rc, styles_rc)...") -ForegroundColor Magenta

$patchPattern = 'import (\w+_rc)\b'
$patchReplacement = 'from src.resources.generated_qrc import $1'

$uiPyFiles = Get-ChildItem -Path $outputDir -Filter *.py

foreach ($f in $uiPyFiles)
{
    $content = Get-Content $f.FullName -Raw

    if ($content -match $patchPattern)
    {
        $content = [regex]::Replace($content, $patchPattern, $patchReplacement)
        Set-Content $f.FullName $content
        Write-Host "  Patched: $( $f.Name )" -ForegroundColor Green
    }
    else
    {
        Write-Host "  No resource patch needed: $( $f.Name )" -ForegroundColor Gray
    }
}

Write-Host ""
$scriptEnd = Get-Date
$duration = $scriptEnd - $scriptStart
Write-Host "Script finished at: $($scriptEnd.ToString('HH:mm:ss') )"
Write-Host ("Total elapsed time: {0:mm\:ss} (mm:ss)" -f $duration) -ForegroundColor Blue
Write-Host "Pipeline completed! All UI and QRC files processed with patched imports." -ForegroundColor Yellow
Write-Host "====================================================================" -ForegroundColor Yellow
