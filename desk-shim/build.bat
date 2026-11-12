@echo off
rem Builds bridge_desk.dll (32-bit, like the game). Needs Visual Studio 2022's C++ tools (x86).
setlocal
set "VSWHERE=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
for /f "usebackq delims=" %%i in (`"%VSWHERE%" -latest -products * -property installationPath`) do set "VS=%%i"
call "%VS%\VC\Auxiliary\Build\vcvarsall.bat" x86 >nul || exit /b 1
if not exist out mkdir out
cl /nologo /O2 /MT /W4 /EHa /LD bridge_desk.cpp d3d11_probe.cpp shareable.cpp /Fo:out\ /Fe:out\bridge_desk.dll /link /NOLOGO /NOIMPLIB /NOEXP /MACHINE:X86 || exit /b 1
echo built out\bridge_desk.dll
