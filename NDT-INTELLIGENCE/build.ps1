# build.ps1 - Automated build script for NDT Intelligence Desktop Application
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Building NDT Intelligence Windows 11 App" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. Clean previous build artifacts
if (Test-Path "build") { 
    Write-Host "Removing old build directory..."
    Remove-Item -Path "build" -Recurse -Force 
}
if (Test-Path "dist\NDT Intelligence") { 
    Write-Host "Removing old dist\NDT Intelligence directory..."
    Remove-Item -Path "dist\NDT Intelligence" -Recurse -Force 
}

# 2. Run icon generator if needed
python assets\make_icon.py

# 3. Compile with PyInstaller
python -m PyInstaller NDT_Intelligence.spec --clean --noconfirm

Write-Host "Build complete! Output in dist\NDT Intelligence" -ForegroundColor Green
