#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif

[Setup]
AppId={{26414995-6FF4-4370-8538-86721691496A}
AppName=Verificador de líneas registradas
AppVersion={#AppVersion}
AppPublisher=Josyrus
DefaultDirName={autopf}\VerificadorLineas
DefaultGroupName=Verificador de líneas
OutputDir=..\dist-installer
OutputBaseFilename=VerificadorLineas-Setup-{#AppVersion}
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
WizardStyle=modern
UninstallDisplayIcon={app}\VerificadorLineas.exe
; SetupIconFile=..\media\icon.ico

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear un acceso directo en el escritorio"; Flags: unchecked

[Files]
Source: "..\dist\VerificadorLineas\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\Verificador de líneas"; Filename: "{app}\VerificadorLineas.exe"
Name: "{autodesktop}\Verificador de líneas"; Filename: "{app}\VerificadorLineas.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\VerificadorLineas.exe"; Description: "Abrir el programa"; Flags: nowait postinstall skipifsilent