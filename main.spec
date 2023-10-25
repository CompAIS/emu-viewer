# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata

# 	lots of nonsense here

#   astroquery requires the CITATION file but for some reason it doesn't automatically get added in
datas = [("resources/assets", "resources/assets"), ("resources/CITATION", "astroquery")]
#   - we need to for some reason copy the Pillow metadata in, otherwise astropy hats us
datas += copy_metadata("Pillow")


block_cipher = None


a = Analysis(
    ["src/main.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['PIL._tkinter_finder'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="EMU Viewer",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=["resources/assets/favicon-32x32.png"],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="EMU Viewer",
)
app = BUNDLE(
    coll,
    name="EMU Viewer.app",
    icon="resources/assets/favicon-32x32.png",
    bundle_identifier=None,
)
