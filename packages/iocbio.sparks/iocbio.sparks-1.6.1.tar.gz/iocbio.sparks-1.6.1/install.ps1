
#
# This script installs IOCBio sparks program to python virtual environment iocbio-sparks
#

$rname = 'iocbio-sparks_requirements.txt'
Invoke-WebRequest -Uri 'https://gitlab.com/iocbio/sparks/-/raw/master/requirements.txt' -OutFile $rname

python.exe -m venv iocbio-sparks
Write-Output "Python virtual environment for iocbio-sparks created"
Write-Output ""

# Upgrading pip
.\iocbio-sparks\Scripts\python.exe -m pip install --upgrade pip

.\iocbio-sparks\Scripts\pip install pip install msvc-runtime

.\iocbio-sparks\Scripts\pip install -r $rname
Remove-Item $rname
.\iocbio-sparks\Scripts\pip install iocbio.sparks

Write-Output ""
Write-Output "IOCBio-sparks installed"
Write-Output ""
Write-Output "To run the program use following commands"
Write-Output ".\iocbio-sparks\Scripts\Activate.ps1"
Write-Output "iocbio-sparks.exe"
