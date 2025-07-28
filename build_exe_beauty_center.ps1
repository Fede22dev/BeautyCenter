# --- SMART ENVIRONMENT & FLAGS LOGIC ---
$console_or_windowed_flag = ""
$exe_name = ""
$exe_version = ""
$upx_flag = ""

Write-Host "=== [AUTO-BUILD SCRIPT] v.1.1 ===" -ForegroundColor Cyan

$version_line = Get-Content ".\name_version.py" | Where-Object { $_ -match 'APP_VERSION' }
$exe_version = ($version_line -split '=')[1].Trim().Trim("'").Trim('"')

if ($env:CI -ne 'true')
{
    # --- Local Environment Detected ---
    Write-Host "[INFO] Local build detected." -ForegroundColor Green

    # Activate the Python virtual environment
    $activate_script = ".\.venv\Scripts\activate.ps1"
    if (Test-Path $activate_script)
    {
        Write-Host "[INFO] Activating virtualenv..."
        & $activate_script
    }
    else
    {
        Write-Error "[FATAL] Venv not found! Exiting build."; exit 1
    }

    # Set flag for local debug mode (console)
    $console_or_windowed_flag = "--console"

    # Executable will have "DBG" suffix for local debug builds
    $exe_name = "Beauty Center DBG v. $exe_version"

    # Check for UPX in the default local path; update this path if needed
    $local_upx_path = "C:\Program Files\upx" # <-- MODIFY THIS IF YOUR UPX IS ELSEWHERE
    if (Test-Path $local_upx_path)
    {
        Write-Host "[INFO] UPX found at '$local_upx_path'. Compression will be enabled."
        # Set UPX flag to local path
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

    # Set PyInstaller to windowed mode for release
    $console_or_windowed_flag = "--windowed"

    # Executable will have release name for CI builds
    $exe_name = "Beauty Center v. $exe_version"

    # Use UPX path from workflow (must be set as env variable in CI YAML)
    if ($env:UPX_PATH)
    {
        Write-Host "[INFO] UPX found at '$env:UPX_PATH'. Compression will be enabled."
        # Set UPX flag using GitHub Actions env variable
        $upx_flag = "--upx-dir=$env:UPX_PATH"
    }
    else
    {
        Write-Host "[INFO] UPX_PATH variable not set, skipping compression."
    }
}

# --- PRE BUILD: CONVERT QT FILES TO PY ---
Write-Host "`n[STEP 1/3] Running Converting script (convert_qt_files_to_py.ps1)..." -ForegroundColor Yellow
if (Test-Path ".\convert_qt_files_to_py.ps1")
{
    & ".\convert_qt_files_to_py.ps1"
    if (-not $?)
    {
        Write-Error "[FATAL] Converting script failed! Aborting build."; exit 1
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
Write-Host "`n[STEP 2/3] Running translation script (generate_translations.ps1)..." -ForegroundColor Yellow
if (Test-Path ".\generate_translations.ps1")
{
    & ".\generate_translations.ps1"
    if (-not $?)
    {
        Write-Error "[FATAL] Translation script failed! Aborting build."; exit 1
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

# --- CLEAN FILES OLD BUILD ---
Write-Host ""
Write-Host "[STEP 3/4] Cleaning old files build..." -ForegroundColor Yellow
Remove-Item "dist" -Recurse -ErrorAction SilentlyContinue
Remove-Item "build" -Recurse -ErrorAction SilentlyContinue
Remove-Item "$exe_name.spec" -ErrorAction SilentlyContinue

# --- BUILD FINAL EXE ---
Write-Host "`n[STEP 4/4] Building EXE..."
Write-Host "      Name: $exe_name"
Write-Host "      Version: $exe_version"
Write-Host "      Console/Window: $console_or_windowed_flag"
Write-Host "      UPX: $upx_flag"

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
    $console_or_windowed_flag,
    "--name", "$exe_name",
    "--collect-submodules", "PySide6.QtCore",
    "--collect-submodules", "PySide6.QtNetwork",
    "--collect-submodules", "PySide6.QtUiTools",
    "--collect-submodules", "PySide6.QtWidgets",
    "--add-data", "ui/views${sep}ui/views",
    "--add-data", "translations/generated_qm${sep}translations/generated_qm",
    "--splash", "resources/images/a350.png"
)

if ($upx_flag)
{
    $pyArgs += $upx_flag
}

$pyArgs += "main.py"

Write-Host "`n[INFO] PyInstaller command (ready to launch):"
Write-Host "pyinstaller $( $pyArgs -join ' ' )" -ForegroundColor Magenta
Write-Host "[STEP 4/4] Executing PyInstaller build..." -ForegroundColor Yellow

pyinstaller @pyArgs

if ($LASTEXITCODE -eq 0)
{
    Write-Host "[SUCCESS] Build completed successfully!" -ForegroundColor Green
    Write-Host "[INFO] Check the /dist directory for your EXE."
}
else
{
    Write-Error "[FAIL] Build failed. Check errors above."
}
Write-Host "=== BUILD SCRIPT COMPLETE ===" -ForegroundColor Cyan
