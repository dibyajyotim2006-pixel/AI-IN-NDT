# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, copy_metadata, collect_submodules
import os

block_cipher = None

# Collect all required metadata and data files for Streamlit & dependencies
datas = [
    ('app.py', '.'),
    ('paths.py', '.'),
    ('components', 'components'),
    ('model', 'model'),
    ('utils', 'utils'),
    ('data', 'data'),
    ('assets', 'assets'),
    ('.streamlit', '.streamlit'),
]

datas += collect_data_files('streamlit')
datas += collect_data_files('plotly')
datas += collect_data_files('reportlab')
datas += collect_data_files('webview')

datas += copy_metadata('streamlit')
datas += copy_metadata('altair')
datas += copy_metadata('pyarrow')
datas += copy_metadata('pandas')
datas += copy_metadata('scikit-learn')

hiddenimports = [
    'streamlit',
    'streamlit.web.bootstrap',
    'streamlit.web.cli',
    'streamlit.runtime',
    'streamlit.runtime.scriptrunner.magic_funcs',
    'streamlit.runtime.caching.storage.dummy_cache_storage',
    'sklearn',
    'sklearn.neural_network',
    'sklearn.compose',
    'sklearn.preprocessing',
    'joblib',
    'scipy',
    'scipy.special',
    'reportlab',
    'reportlab.lib',
    'reportlab.platypus',
    'plotly',
    'plotly.express',
    'plotly.graph_objects',
    'webview',
    'webview.platforms.winforms',
    'psutil',
    'PIL',
    'clr',
    'pythonnet',
]
hiddenimports += collect_submodules('streamlit')

a = Analysis(
    ['launcher.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'torch', 'tensorflow'],
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
    name='NDT Intelligence',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets/ndt_intelligence.ico'],
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='NDT Intelligence',
)
