# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app\\ui.py'],
    pathex=['app\\main.py'],
    binaries=[],
    datas=[
        ('D:\\applications\\ffmpeg-7.1.1-full_build\\bin\\ffmpeg.exe', '_internal'),
        ('.\\venv\\Lib\\site-packages\\whisper', '_internal'),
    ],
    hiddenimports=[
        'whisper',
        'whisper.tokenizer',
        'whisper.decoding',
    ],
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
    [],
    exclude_binaries=True,
    name='ui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ui',
)
