@echo off
REM 网文编辑部 - 门禁检查器快速入口
REM 
REM 使用方法:
REM   gate.bat writer-before 3
REM   gate.bat writer-after 3 chapter-03.md
REM   gate.bat editor-confirm 3 chapter-03.md

if "%1"=="" (
    echo 用法: gate.bat [命令] [参数...]
    echo.
    echo 命令:
    echo   writer-before ^<章节号^>        - 写手写作前检查
    echo   writer-after ^<章节号^> ^<文件^>  - 写手写作后检查
    echo   editor-before ^<章节号^>        - 编辑审核前检查
    echo   editor-after ^<章节号^> pass     - 编辑审核后检查
    echo   editor-confirm ^<章节号^> ^<文件^> - 总编确认前检查
    echo   checkpoint ^<章节号^>            - 检查点检查
    exit /b 1
)

set PROJECT_PATH=%~dp0..\..\..\..\..\..\Documents\webnovel\your-project
set GATE_MODULE=gate

if "%1"=="writer-before" (
    python -m %GATE_MODULE% %PROJECT_PATH% writer-before --chapter %2
    exit /b %errorlevel%
)

if "%1"=="writer-after" (
    python -m %GATE_MODULE% %PROJECT_PATH% writer-after --chapter %2 --file %3 --target-words 3000
    exit /b %errorlevel%
)

if "%1"=="editor-before" (
    python -m %GATE_MODULE% %PROJECT_PATH% editor-before --chapter %2
    exit /b %errorlevel%
)

if "%1"=="editor-after" (
    python -m %GATE_MODULE% %PROJECT_PATH% editor-after --chapter %2 --review-status %3
    exit /b %errorlevel%
)

if "%1"=="editor-confirm" (
    python -m %GATE_MODULE% %PROJECT_PATH% editor-confirm --chapter %2 --file %3
    exit /b %errorlevel%
)

if "%1"=="checkpoint" (
    python -m %GATE_MODULE% %PROJECT_PATH% checkpoint --chapter %2 --auto-checkpoint
    exit /b %errorlevel%
)

echo 未知命令: %1
exit /b 1