@echo off


::Set personal Path to the Apps:
:: set PythonEXE=e:\devtool\EPD26\python.exe
set filePath=F:\\programing\\python\\autoexetool
set UpxEXE=%filePath%\upx.exe

echo %filePath%
set vc90_crt =  %filePath%\\Microsoft.VC90.CRT.manifest 
set msvcp90 =  %filePath%\\msvcp90.dll 
set msvcr90 = %filePath%\\msvcr90.dll

:: Compress=1 - Use CompressFiles
:: Compress=0 - Don't CompressFiles
set Compress=1


if not exist %~dpn0.py          call :FileNotFound %~dpn0.py
:: if not exist %PythonEXE%        call :FileNotFound %PythonEXE%
:: if not exist %UpxEXE%           call :FileNotFound %UpxEXE%


::Write the Py2EXE-Setup File
call :MakeSetupFile >"%~dpn0_EXESetup.py"


::Compile the Python-Script
python "%~dpn0_EXESetup.py" py2exe %1 %2 %3 %4 %5 %6 %7 %8 %9
if not "%errorlevel%"=="0" (
        echo Py2EXE Error!
        pause
        goto:eof
)


:: Delete the Py2EXE-Setup File
del "%~dpn0_EXESetup.py"


:: Copy the Py2EXE Results to the SubDirectory and Clean Py2EXE-Results
rd build /s /q
xcopy dist\*.* "%~dpn0_EXE\" /d /y
del %~dpn0_EXE\w9xpopen.exe
:: I use xcopy dist\*.* "%~dpn0_EXE\" /s /d /y
:: This is necessary when you have subdirectories - like when you use Tkinter
rd dist /s /q


if "%Compress%"=="1" call:CompressFiles
echo.
echo.
echo Done: "%~dpn0_EXE\"
echo.
pause
goto:eof



:CompressFiles
        cd %~dpn0_EXE\
        %UpxEXE% --best *.*
goto:eof



:MakeSetupFile
        echo.
        echo from distutils.core import setup
        echo import py2exe
        echo.
	::echo sysfiles=[r"F:\programing\python\autoexetool\Microsoft.VC90.CRT.manifest", r"F:\programing\python\autoexetool\msvcp90.dll", r"F:\programing\python\autoexetool\msvcr90.dll"]
        ::echo sysfiles
        ::data_files=sysfiles
        echo setup (zipfile=None,console=[{"script":r"%~dpn0.py","icon_resources": [(1, "%filePath%\some.ico")]}],
        echo options={"py2exe":{"compressed":True,"bundle_files":1,"packages": ["encodings"]}})
        echo.
goto:eof


:FileNotFound
        echo.
        echo Error, File not found:
        echo [%1]
        echo.
        echo Check Path in %~nx0???
        echo.
        pause
        exit
goto:eof