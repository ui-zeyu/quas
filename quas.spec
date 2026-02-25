# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import copy_metadata, collect_submodules, collect_data_files

datas = [('src/quas/analysis/english_quadgrams.txt', 'quas/analysis')] + copy_metadata('gmpy2')
hidden_imports = collect_submodules('rich')

a = Analysis(
    ['src/quas/__init__.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports + ['gmpy2'],
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
    name='quas',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
