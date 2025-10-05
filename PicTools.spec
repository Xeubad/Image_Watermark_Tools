# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('fonts/ChillDuanHeiSongPro_Regular.otf', 'fonts')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas', 'scipy', 'PyQt5', 'tkinter', 
              'PySide2', 'qt', 'PyQt4', 'django', 'IPython', 'notebook', 
              'sphinx', 'skimage', 'tensorflow', 'wx'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

a.binaries = [x for x in a.binaries if not x[0].startswith("sqlite")]
a.binaries = [x for x in a.binaries if not x[0].startswith("tcl")]
a.binaries = [x for x in a.binaries if not x[0].startswith("tk")]
a.binaries = [x for x in a.binaries if not x[0].startswith("opengl")]
a.binaries = [x for x in a.binaries if not x[0].startswith("Qt")]
a.binaries = [x for x in a.binaries if not x[0].startswith("PyQt")]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PicTools',
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
)
