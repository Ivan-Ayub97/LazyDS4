# -*- mode: python ; coding: utf-8 -*-
import os
import site

# Find vgamepad installation path
vgamepad_path = None

# Try to find vgamepad, but don't fail if it's not found
try:
    for site_package in site.getsitepackages():
        potential_path = os.path.join(site_package, 'vgamepad')
        if os.path.exists(potential_path):
            vgamepad_path = potential_path
            break
    
    # Also check user site-packages
    if not vgamepad_path:
        user_site = site.getusersitepackages()
        if user_site:
            potential_path = os.path.join(user_site, 'vgamepad')
            if os.path.exists(potential_path):
                vgamepad_path = potential_path
except Exception as e:
    print(f"Warning: Could not locate vgamepad package: {e}")
    vgamepad_path = None

if not vgamepad_path:
    print("Warning: vgamepad path not found, continuing without vgamepad-specific includes")

# Build binaries list with the correct vgamepad DLLs
binaries = []
if vgamepad_path:
    vigem_x64_dll = os.path.join(vgamepad_path, 'win', 'vigem', 'client', 'x64', 'ViGEmClient.dll')
    vigem_x86_dll = os.path.join(vgamepad_path, 'win', 'vigem', 'client', 'x86', 'ViGEmClient.dll')
    
    if os.path.exists(vigem_x64_dll):
        binaries.append((vigem_x64_dll, 'vgamepad/win/vigem/client/x64'))
        print(f"Including ViGEmClient x64 DLL: {vigem_x64_dll}")
    if os.path.exists(vigem_x86_dll):
        binaries.append((vigem_x86_dll, 'vgamepad/win/vigem/client/x86'))
        print(f"Including ViGEmClient x86 DLL: {vigem_x86_dll}")
else:
    print("Skipping vgamepad DLLs - vgamepad path not found")

# Build datas list including vgamepad installers and our local assets
datas = [('assets', 'assets'), ('core', 'core'), ('ui', 'ui'), ('utils', 'utils')]

# Include ViGEmBus installers from vgamepad package
if vgamepad_path:
    vigem_x64_msi = os.path.join(vgamepad_path, 'win', 'vigem', 'install', 'x64', 'ViGEmBusSetup_x64.msi')
    vigem_x86_msi = os.path.join(vgamepad_path, 'win', 'vigem', 'install', 'x86', 'ViGEmBusSetup_x86.msi')
    
    if os.path.exists(vigem_x64_msi):
        datas.append((vigem_x64_msi, 'vgamepad/win/vigem/install/x64'))
        print(f"Including ViGEmBus x64 installer: {vigem_x64_msi}")
    if os.path.exists(vigem_x86_msi):
        datas.append((vigem_x86_msi, 'vgamepad/win/vigem/install/x86'))
        print(f"Including ViGEmBus x86 installer: {vigem_x86_msi}")
else:
    print("Skipping vgamepad installers - vgamepad path not found")

# Ensure our local ViGEmBus installer is included if it exists
local_vigem_installer = 'assets/ViGEmBus_1.22.0_x64_x86_arm64.exe'
if os.path.exists(local_vigem_installer):
    print(f"Including local ViGEmBus installer: {local_vigem_installer}")

a = Analysis(
    ['LazyDS4.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=['vgamepad', 'vgamepad.win', 'vgamepad.win.vigem_client', 'vgamepad.win.vigem_commons', 'vgamepad.win.virtual_gamepad'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='LazyDS4',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets\\icon.ico'],
)
