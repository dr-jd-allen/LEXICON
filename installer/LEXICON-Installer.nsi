; LEXICON Installer Script for NSIS
; Creates a simple one-click installer for lawyers

!include "MUI2.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"

; General settings
Name "LEXICON Legal AI System"
OutFile "..\LEXICON-Setup-v1.0.exe"
InstallDir "$PROGRAMFILES64\LEXICON"
InstallDirRegKey HKLM "Software\LEXICON" "Install_Dir"
RequestExecutionLevel admin
ShowInstDetails show
ShowUninstDetails show

; Version info
VIProductVersion "1.0.0.0"
VIAddVersionKey "ProductName" "LEXICON Legal AI"
VIAddVersionKey "CompanyName" "Allen Law Group"
VIAddVersionKey "LegalCopyright" "© 2024 Allen Law Group"
VIAddVersionKey "FileDescription" "AI-Powered Legal Brief Generation System"
VIAddVersionKey "FileVersion" "1.0.0"

; Modern UI Configuration
!define MUI_ABORTWARNING
!define MUI_ICON "..\assets\lexicon.ico"
!define MUI_UNICON "..\assets\lexicon.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "..\assets\installer-side.bmp"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "..\assets\installer-header.bmp"
!define MUI_HEADERIMAGE_RIGHT

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\LICENSE.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES

; Custom finish page
!define MUI_FINISHPAGE_TITLE "LEXICON Installation Complete"
!define MUI_FINISHPAGE_TEXT "LEXICON has been successfully installed on your computer.$\r$\n$\r$\nClick 'Launch LEXICON' to start the application."
!define MUI_FINISHPAGE_RUN "$INSTDIR\LEXICON.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Launch LEXICON"
!define MUI_FINISHPAGE_RUN_CHECKED
!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\Quick Start Guide.pdf"
!define MUI_FINISHPAGE_SHOWREADME_TEXT "View Quick Start Guide"
!define MUI_FINISHPAGE_SHOWREADME_CHECKED
!define MUI_FINISHPAGE_LINK "Visit LEXICON Support"
!define MUI_FINISHPAGE_LINK_LOCATION "https://lexicon-support.com"

!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Language
!insertmacro MUI_LANGUAGE "English"

; Installer Sections
Section "LEXICON Core System" SEC_CORE
    SectionIn RO ; Required
    
    SetOutPath "$INSTDIR"
    
    ; Create directories
    CreateDirectory "$INSTDIR\app"
    CreateDirectory "$INSTDIR\data"
    CreateDirectory "$INSTDIR\docker"
    CreateDirectory "$INSTDIR\logs"
    CreateDirectory "$DOCUMENTS\LEXICON"
    CreateDirectory "$DOCUMENTS\LEXICON\Generated Briefs"
    CreateDirectory "$DOCUMENTS\LEXICON\Uploaded Documents"
    CreateDirectory "$DOCUMENTS\LEXICON\Strategic Recommendations"
    
    ; Extract application files
    File /r "..\app\*.*"
    File "..\LEXICON.exe"
    File "..\Quick Start Guide.pdf"
    File "..\assets\lexicon.ico"
    
    ; Write registry keys
    WriteRegStr HKLM "Software\LEXICON" "Install_Dir" "$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LEXICON" "DisplayName" "LEXICON Legal AI System"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LEXICON" "UninstallString" '"$INSTDIR\uninstall.exe"'
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LEXICON" "DisplayIcon" "$INSTDIR\lexicon.ico"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LEXICON" "Publisher" "Allen Law Group"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LEXICON" "DisplayVersion" "1.0.0"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LEXICON" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LEXICON" "NoRepair" 1
    
    ; Create uninstaller
    WriteUninstaller "uninstall.exe"
    
SectionEnd

Section "Desktop Shortcuts" SEC_DESKTOP
    CreateShortcut "$DESKTOP\LEXICON.lnk" "$INSTDIR\LEXICON.exe" "" "$INSTDIR\lexicon.ico" 0
    CreateShortcut "$DESKTOP\LEXICON Documents.lnk" "$DOCUMENTS\LEXICON" "" "$INSTDIR\lexicon.ico" 0
SectionEnd

Section "Start Menu Shortcuts" SEC_STARTMENU
    CreateDirectory "$SMPROGRAMS\LEXICON"
    CreateShortcut "$SMPROGRAMS\LEXICON\LEXICON.lnk" "$INSTDIR\LEXICON.exe" "" "$INSTDIR\lexicon.ico" 0
    CreateShortcut "$SMPROGRAMS\LEXICON\Documents Folder.lnk" "$DOCUMENTS\LEXICON" "" "$INSTDIR\lexicon.ico" 0
    CreateShortcut "$SMPROGRAMS\LEXICON\Quick Start Guide.lnk" "$INSTDIR\Quick Start Guide.pdf"
    CreateShortcut "$SMPROGRAMS\LEXICON\Uninstall.lnk" "$INSTDIR\uninstall.exe"
SectionEnd

Section "Docker Runtime" SEC_DOCKER
    ; Check if Docker is installed
    ReadRegStr $0 HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Docker Desktop" "DisplayVersion"
    ${If} $0 == ""
        MessageBox MB_YESNO|MB_ICONQUESTION "Docker Desktop is required but not installed. Would you like to download it now?" IDYES download_docker
        Goto skip_docker
        
        download_docker:
        ExecShell "open" "https://www.docker.com/products/docker-desktop/"
        MessageBox MB_OK "Please install Docker Desktop and run the LEXICON installer again."
        Abort
        
        skip_docker:
    ${EndIf}
SectionEnd

; Section descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SEC_CORE} "Core LEXICON application files (required)"
    !insertmacro MUI_DESCRIPTION_TEXT ${SEC_DESKTOP} "Create shortcuts on your desktop"
    !insertmacro MUI_DESCRIPTION_TEXT ${SEC_STARTMENU} "Create shortcuts in Start Menu"
    !insertmacro MUI_DESCRIPTION_TEXT ${SEC_DOCKER} "Check for Docker Desktop installation"
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; Uninstaller Section
Section "Uninstall"
    ; Ask about data deletion
    MessageBox MB_YESNO|MB_ICONQUESTION "Do you want to keep your generated briefs and documents?$\r$\n$\r$\nClick 'Yes' to keep your data or 'No' to delete everything." IDYES keep_data
    
    ; Delete data if requested
    RMDir /r "$DOCUMENTS\LEXICON"
    
    keep_data:
    
    ; Remove installation files
    Delete "$INSTDIR\LEXICON.exe"
    Delete "$INSTDIR\Quick Start Guide.pdf"
    Delete "$INSTDIR\lexicon.ico"
    Delete "$INSTDIR\uninstall.exe"
    RMDir /r "$INSTDIR\app"
    RMDir /r "$INSTDIR\docker"
    RMDir /r "$INSTDIR\logs"
    RMDir "$INSTDIR"
    
    ; Remove shortcuts
    Delete "$DESKTOP\LEXICON.lnk"
    Delete "$DESKTOP\LEXICON Documents.lnk"
    RMDir /r "$SMPROGRAMS\LEXICON"
    
    ; Remove registry keys
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\LEXICON"
    DeleteRegKey HKLM "Software\LEXICON"
    
    ; Stop and remove Docker containers
    ExecWait '"$PROGRAMFILES\Docker\Docker\resources\bin\docker.exe" stop $(docker ps -aq --filter "name=lexicon")'
    ExecWait '"$PROGRAMFILES\Docker\Docker\resources\bin\docker.exe" rm $(docker ps -aq --filter "name=lexicon")'
    
SectionEnd

; Installer Functions
Function .onInit
    ; Check for admin rights
    UserInfo::GetAccountType
    Pop $0
    ${If} $0 != "admin"
        MessageBox MB_ICONSTOP "Administrator rights required!"
        SetErrorLevel 740 ; ERROR_ELEVATION_REQUIRED
        Quit
    ${EndIf}
    
    ; Check system requirements
    ${GetSize} "$PROGRAMFILES64" "/S=0K" $0 $1 $2
    IntOp $0 $2 / 1048576 ; Convert to GB
    ${If} $0 < 10
        MessageBox MB_ICONEXCLAMATION "Warning: Less than 10GB free space on system drive."
    ${EndIf}
FunctionEnd

Function .onInstSuccess
    ; Create initial configuration
    FileOpen $0 "$INSTDIR\config.json" w
    FileWrite $0 '{'
    FileWrite $0 '$\r$\n  "first_run": true,'
    FileWrite $0 '$\r$\n  "data_path": "$DOCUMENTS\\LEXICON",'
    FileWrite $0 '$\r$\n  "auto_backup": true,'
    FileWrite $0 '$\r$\n  "theme": "professional"'
    FileWrite $0 '$\r$\n}'
    FileClose $0
FunctionEnd