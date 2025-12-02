param(
  [switch]$OneFile
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

py -m pip install --upgrade pip
py -m pip install -r ..\requirements.txt

$argsList = @('build/pdf_split.spec')
if ($OneFile) {
  $argsList = @('--onefile','--windowed','--name','PDF Split','pdf_merger_splitter/gui/app.py')
}

py -m PyInstaller --noconfirm @argsList

Write-Host "Build complete. Output in dist/" -ForegroundColor Green
