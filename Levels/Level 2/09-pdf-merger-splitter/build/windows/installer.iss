; Inno Setup script for PDF Split (unsigned)
[Setup]
AppName=PDF Split
AppVersion=1.0.0
DefaultDirName={autopf64}\PDF Split
DefaultGroupName=PDF Split
OutputBaseFilename=PDFSplitSetup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64

[Files]
Source:"dist\PDF Split\*"; DestDir:"{app}"; Flags: recursesubdirs

[Icons]
Name:"{group}\PDF Split"; Filename:"{app}\PDF Split.exe"
Name:"{commondesktop}\PDF Split"; Filename:"{app}\PDF Split.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop icon"; Flags: unchecked

[Run]
Filename: "{app}\\PDF Split.exe"; Description: "Launch PDF Split"; Flags: nowait postinstall skipifsilent
