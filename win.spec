# -*- mode: python -*-
# coding=utf-8
block_cipher = None

added_files = [
         ( 'images', 'images' ),
         ( 'config.ini', '.' ),
         ('third-party','third-party')
         ]
a = Analysis(['D:\\workspace\\OwnProject\\jyeoo-crawler-gui\\main.py'],
             pathex=['D:\\workspace\\OwnProject\\jyeoo-crawler-gui', 'D:\\workspace\\OwnProject\\jyeoo-crawler-gui'],
             binaries=[],
             datas=added_files,
             hiddenimports=['pymysql'],
             hookspath=['d:\\virtualenv\\web-crawler\\lib\\site-packages\\pyupdater\\hooks'],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='win',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False ,icon='images\\main.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='win')
