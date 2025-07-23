# --- SMART ENVIRONMENT & FLAGS LOGIC ---
$console_or_windowed_flag = ""
$exe_name = ""
$exe_version = ""
$upx_flag = ""

$version_line = Get-Content ".\name_version.py" | Where-Object { $_ -match 'APP_VERSION' }
$exe_version = ($version_line -split '=')[1].Trim().Trim("'").Trim('"')

if ($env:CI -ne 'true')
{
    # --- Local Environment Detected ---
    Write-Host "Local build detected."

    # Activate the Python virtual environment
    $activate_script = ".\.venv\Scripts\activate.ps1"
    if (Test-Path $activate_script)
    {
        & $activate_script
    }
    else
    {
        Write-Error "Venv not found."; exit 1
    }

    # Set flag for local debug mode (console)
    $console_or_windowed_flag = "--console"

    # Executable will have "DBG" suffix for local debug builds
    $exe_name = "Beauty Center DBG v. $exe_version"

    # Check for UPX in the default local path; update this path if needed
    $local_upx_path = "C:\Program Files\upx" # <-- MODIFY THIS IF YOUR UPX IS ELSEWHERE
    if (Test-Path $local_upx_path)
    {
        Write-Host "UPX found at '$local_upx_path'. Compression will be enabled."
        # Set UPX flag to local path
        $upx_flag = "--upx-dir=$local_upx_path"
    }
    else
    {
        Write-Host "UPX not found at '$local_upx_path', skipping compression."
    }
}
else
{
    # --- CI Environment Detected (e.g., GitHub Actions) ---
    Write-Host "CI environment detected."

    # Set PyInstaller to windowed mode for release
    $console_or_windowed_flag = "--windowed"

    # Executable will have release name for CI builds
    $exe_name = "Beauty Center v. $exe_version"

    # Use UPX path from workflow (must be set as env variable in CI YAML)
    if ($env:UPX_PATH)
    {
        Write-Host "UPX found at '$env:UPX_PATH' in CI environment. Compression will be enabled."
        # Set UPX flag using GitHub Actions env variable
        $upx_flag = "--upx-dir=$env:UPX_PATH"
    }
    else
    {
        Write-Host "UPX_PATH variable not set, skipping compression."
    }
}

# --- BUILD FINAL EXE ---
Write-Host "Building: $exe_name, Version: $exe_version, PyInstaller flags: $console_or_windowed_flag $upx_flag"
Write-Host "PyInstaller command will be run from: $( Get-Location )"

pyinstaller --onefile $console_or_windowed_flag --name $exe_name `
    --collect-submodules PySide6.QtCore `
    --collect-submodules PySide6.QtNetwork `
    --collect-submodules PySide6.QtUiTools `
    --collect-submodules PySide6.QtWidgets `
    --add-data "ui/main_window;ui/main_window" `
    --splash "resources/a350.png" $upx_flag main.py
