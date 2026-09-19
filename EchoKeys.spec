# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['EchoKeys.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'tools',
        'tools.Log',
        'tools.Dialog',
        'tools.key_mouse_monitor',
        'tools.mouse_highlight',
        'tools.ToolTip',
        'tools.mouse_trail',
        'tools.water_skip',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除不需要的 PyQt5 模块
        'PyQt5.QtWebKit',
        'PyQt5.QtWebKitWidgets',
        'PyQt5.QtXml',
        'PyQt5.QtXmlPatterns',
        'PyQt5.QtHelp',
        'PyQt5.QtDesigner',
        'PyQt5.QtTest',
        'PyQt5.QtSql',
        'PyQt5.QtNetwork',
        'PyQt5.QtMultimedia',
        'PyQt5.QtMultimediaWidgets',
        'PyQt5.QtOpenGL',
        'PyQt5.QtScript',
        'PyQt5.QtScriptTools',
        'PyQt5.QtSerialPort',
        'PyQt5.QtDBus',
        'PyQt5.QtBluetooth',
        'PyQt5.QtNfc',
        'PyQt5.QtPositioning',
        'PyQt5.QtSensors',
        'PyQt5.QtRemoteObjects',
        'PyQt5.QtWebChannel',
        'PyQt5.QtWebEngineCore',
        'PyQt5.QtWebEngineWidgets',
        'PyQt5.QtWebSockets',
        'PyQt5.QtLocation',
        'PyQt5.QtQuick',
        'PyQt5.QtQuickWidgets',
        'PyQt5.QtQml',
        'PyQt5.QtUiTools',
        
        # 排除标准库中不需要的模块
        'tkinter',
        'unittest',
        'test',
        'xmlrpc',
        'pydoc',
        'doctest',
        'pdb',
        'profile',
        'cProfile',
        
        # 排除其他第三方库（如果有安装但不使用的）
        'numpy',
        'pandas',
        'scipy',
        'matplotlib',
        'PIL',
        'cv2',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='EchoKeys',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # 不显示控制台
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以设置图标路径，如 icon='icon.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='EchoKeys',
)
