# -*- mode: python -*-

block_cipher = None
added_files = [
         ( 'images', 'images' ),
         ( 'config.ini', '.' ),
         ('third-party','third-party')
         ]

a = Analysis(['main.py'],
             pathex=['D:\\workspace\\OwnProject\\jyeoo-crawler-gui'],
             binaries=[],
             datas=added_files,
             hiddenimports=['pymysql'],
             hookspath=[],
             runtime_hooks=[],
             excludes=['phantomjs','phantomjs.zip'],
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
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False , icon='images\\main.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='main')
