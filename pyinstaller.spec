# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['src\\tiff_utility.py'],
             pathex=['C:\\Users\\us43060\\Documents\\Projects\\Tiff-Merge-Utility\\src'],
             binaries=[],
             datas=[
                ('src/icon.ico','.'),
                ('src/help.ico','.'),
                ('src/merge.png','.'),
                ('src/split.png','.'),
                ('src/help.html','.')],
             hiddenimports=[],
             hookspath=[],
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
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='Tiff Utility',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          icon='src\\icon.ico',
          console=False)
