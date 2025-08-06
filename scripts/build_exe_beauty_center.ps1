$scriptStart = Get-Date
Write-Host ""
Write-Host "========= [AUTO-BUILD SCRIPT] =========" -ForegroundColor Cyan
Write-Host "Script started at: $($scriptStart.ToString('HH:mm:ss') )"

# --- SETUP ENVIRONMENT & FLAGS LOGIC ---
$ScriptPath = $PSScriptRoot
$ProjectRoot = Split-Path $ScriptPath -Parent
$exeDir = Join-Path $ProjectRoot "exe"
$name_version_file = Join-Path $ProjectRoot "src" "name_version.py"

if (-not (Test-Path $name_version_file))
{
    Write-Error "[FATAL] name_version.py not found! (Expected: $name_version_file)"
    exit 1
}

$version_line = Get-Content $name_version_file | Where-Object { $_ -match 'APP_VERSION' }
$exe_version = ($version_line -split '=')[1].Trim().Trim("'").Trim('"')

$console_or_windowed_flag = ""
$exe_name = ""
$upx_flag = ""

Write-Host ""

if ($env:CI -ne 'true')
{
    # --- Local Environment Detected ---
    Write-Host "[INFO] Local build detected." -ForegroundColor Green

    $activate_script = Join-Path $ProjectRoot ".venv\Scripts\activate.ps1"

    if (Test-Path $activate_script)
    {
        Write-Host "[INFO] Activating virtualenv..."
        & $activate_script
    }
    else
    {
        Write-Error "[FATAL] Venv not found! Exiting build.";
        exit 1
    }

    $console_or_windowed_flag = "--console"
    $exe_name = "Beauty Center DBG v. $exe_version"
    $local_upx_path = "C:\Program Files\upx" # <-- MODIFY THIS IF YOUR UPX IS ELSEWHERE

    if (Test-Path $local_upx_path)
    {
        Write-Host "[INFO] UPX found at '$local_upx_path'. Compression will be enabled."
        $upx_flag = "--upx-dir=$local_upx_path"
    }
    else
    {
        Write-Host "[INFO] UPX not found at '$local_upx_path', skipping compression."
    }
}
else
{
    # --- CI Environment Detected (e.g., GitHub Actions) ---
    Write-Host "[INFO] CI environment detected." -ForegroundColor Green

    $console_or_windowed_flag = "--windowed"
    $exe_name = "Beauty Center v. $exe_version"

    if ($env:UPX_PATH)
    {
        Write-Host "[INFO] UPX found at '$env:UPX_PATH'. Compression will be enabled."
        $upx_flag = "--upx-dir=$env:UPX_PATH"
    }
    else
    {
        Write-Host "[INFO] UPX_PATH variable not set, skipping compression."
    }
}

$console_or_windowed_flag = "--console" # TODO REMOVE FOR FINAL RELEASE

# --- PRE BUILD: CONVERT QT FILES TO PY ---
Write-Host ""
Write-Host "[STEP 1/3] Running Converting script (convert_qt_files_to_py.ps1)..." -ForegroundColor Yellow

$convert_script = Join-Path $ScriptPath "convert_qt_files_to_py.ps1"

if (Test-Path  $convert_script)
{
    &  $convert_script

    if (-not $?)
    {
        Write-Error "[FATAL] Converting script failed! Aborting build.";
        exit 1
    }
    else
    {
        Write-Host "[OK] Converting successfully."
    }
}
else
{
    Write-Warning "[WARN] convert_qt_files_to_py.ps1 NOT FOUND. Converting will NOT be done!"
}

# --- PRE BUILD: GENERATE AND UPDATE TRANSLATIONS ---
Write-Host ""
Write-Host "[STEP 2/3] Running translation script (generate_translations.ps1)..." -ForegroundColor Yellow

$translation_script = Join-Path $ScriptPath "generate_translations.ps1"

if (Test-Path $translation_script)
{
    & $translation_script

    if (-not $?)
    {
        Write-Error "[FATAL] Translation script failed! Aborting build.";
        exit 1
    }
    else
    {
        Write-Host "[OK] Translations updated successfully."
    }
}
else
{
    Write-Warning "[WARN] generate_translations.ps1 NOT FOUND. Translations will NOT be updated!"
}

# --- CLEAN OLD FILES ONLY IN exe/ ---
Write-Host ""
Write-Host "[STEP 3/4] Cleaning old build files in /exe..." -ForegroundColor Yellow

if (Test-Path $exeDir)
{
    Remove-Item "$exeDir\*" -Recurse -ErrorAction SilentlyContinue
}
else
{
    New-Item -ItemType Directory -Path $exeDir | Out-Null
}

# --- BUILD FINAL EXE ---
Write-Host ""
Write-Host "[STEP 4/4] Executing PyInstaller build..." -ForegroundColor Yellow

Set-Location $ProjectRoot

Write-Host "      Name:     $exe_name"
Write-Host "      Version:  $exe_version"
Write-Host "      Out dir:  $exeDir"
Write-Host "      Console/Window: $console_or_windowed_flag"
Write-Host "      UPX:      $upx_flag"

$sep = if ($IsWindows)
{
    ";"
}
else
{
    ":"
}

$pyArgs = @(
    "--onefile",
    "--clean",
    "--noconfirm",
    "--strip",
    "--distpath", $exeDir,
    "--workpath", (Join-Path $exeDir "build"),
    "--specpath", $exeDir,
    $console_or_windowed_flag,
    "--name", "$exe_name",
    "--collect-submodules", "PySide6.QtCore",
    "--collect-submodules", "PySide6.QtNetwork",
    "--collect-submodules", "PySide6.QtUiTools",
    "--collect-submodules", "PySide6.QtWidgets",
    "--add-data", "../translations/generated_qm${sep}translations/generated_qm",
    "--splash", "../src/resources/images/splash_screen.png",
    "--icon", "../src/resources/icons/windows_icon.ico"
)

if ($upx_flag)
{
    $pyArgs += $upx_flag
}

$pyArgs += "start_bc.py"

Write-Host ""
Write-Host "[INFO] PyInstaller command (ready to launch):"
Write-Host "pyinstaller $( $pyArgs -join ' ' )" -ForegroundColor Magenta

pyinstaller @pyArgs

if ($LASTEXITCODE -eq 0)
{
    Write-Host "[SUCCESS] Build completed successfully!" -ForegroundColor Green
    Write-Host "[INFO] Check the /exe directory for your EXE."
}
else
{
    Write-Error "[FAIL] Build failed. Check errors above."
}

Write-Host ""
$scriptEnd = Get-Date
$duration = $scriptEnd - $scriptStart
Write-Host "Script finished at: $($scriptEnd.ToString('HH:mm:ss') )"
Write-Host ("Total elapsed time: {0:mm\:ss} (mm:ss)" -f $duration) -ForegroundColor Blue
Write-Host "========= BUILD SCRIPT COMPLETE =========" -ForegroundColor Cyan
