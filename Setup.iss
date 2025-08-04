; LazyDS4 Inno Setup Script
; Enhanced version with better ViGEmBus integration and modern features

#define AppName "LazyDS4"
#define AppVersion "2.1.0"
#define AppVersionShort "2.1"
#define AppPublisher "Iván Eduardo Chavez Ayub"
#define AppURL "https://github.com/Ivan-Ayub97/LazyDS4"
#define AppExeName "LazyDS4.exe"
#define ViGEmBusInstaller "ViGEmBus_1.22.0_x64_x86_arm64.exe"

[Setup]
; Basic app info
AppId={{8B5F9F3C-1D4A-4C2B-8E3F-7A9B6C5D4E2F}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersionShort}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
AppCopyright=Copyright © 2024 {#AppPublisher}

; Installation settings
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
DisableDirPage=no
DisableReadyPage=no
AllowNoIcons=yes
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; Output settings
OutputDir=Output
OutputBaseFilename=LazyDS4-{#AppVersion}-Installer
SetupIconFile=assets\icon.ico
Compression=lzma2/max
SolidCompression=yes
InternalCompressLevel=max

; UI settings
WizardStyle=modern
WizardSizePercent=100
WizardSmallImageFile=assets\small_image.bmp
UninstallDisplayIcon={app}\{#AppExeName}
UninstallDisplayName={#AppName}
ShowLanguageDialog=no

; Version info
VersionInfoVersion={#AppVersion}
VersionInfoCompany={#AppPublisher}
VersionInfoDescription={#AppName} Setup
VersionInfoCopyright=Copyright © 2024 {#AppPublisher}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"; LicenseFile: "License.txt"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Archivos principales de la aplicación
Source: "{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
; Instalador de ViGEmBus (incluido en el paquete)
Source: "assets\{#ViGEmBusInstaller}"; DestDir: "{app}\assets"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\assets\icon.ico"; WorkingDir: "{app}"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\assets\icon.ico"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
; Always install ViGEmBus driver (interactive)
Filename: "{app}\assets\{#ViGEmBusInstaller}"; StatusMsg: "Installing the required ViGEmBus driver..."; Flags: waituntilterminated

; Launch LazyDS4 after installation (optional)
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\assets"

[Messages]
; Custom messages for better UX
WelcomeLabel2=This will install [name/ver] on your computer.%n%nLazyDS4 allows you to use your DualShock 4 controller as an Xbox 360 controller on Windows.%n%nThis installer will also install the required ViGEmBus driver to ensure full functionality.
FinishedLabelNoIcons=Setup has finished installing [name] on your computer.%n%nYou can now connect your DualShock 4 controller and start LazyDS4 to begin using it as an Xbox controller.

[Code]
// No custom code needed for unconditional install.
