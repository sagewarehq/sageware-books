"""One-time Calibre-Web data initialization, executed before web startup."""
import base64
import gzip
import hashlib
import os
from pathlib import Path
import sqlite3
import subprocess

config = Path('/config')
books = Path('/books')
config.mkdir(exist_ok=True)
books.mkdir(exist_ok=True)
if not (books / 'metadata.db').exists():
    seed = gzip.decompress(base64.b64decode(os.environ['LIBRARY_SEED']))
    assert hashlib.sha256(seed).hexdigest() == os.environ['LIBRARY_SEED_SHA256']
    (books / 'metadata.db').write_bytes(seed)

marker = config / '.books-initialized'
if not marker.exists():
    subprocess.run(['python3', '/app/calibre-web/cps.py', '-p', '/config/app.db', '-d'], check=True, cwd='/app/calibre-web')
    with sqlite3.connect(config / 'app.db') as db:
        assert db.execute('SELECT count(*) FROM user WHERE name = ?', ('admin',)).fetchone()[0] == 1
        db.execute('UPDATE user SET name = ?, email = ?, password = ? WHERE name = ?',
                   ('jesse', 'jesse@sageware.io', os.environ['ADMIN_PASSWORD_HASH'], 'admin'))
        db.execute('UPDATE settings SET config_calibre_dir = ?, config_calibre_web_title = ?, config_anonbrowse = 0, config_public_reg = 0, config_uploading = 1, config_remote_login = 0',
                   ('/books', 'Sageware Books'))
        assert db.execute('SELECT count(*) FROM settings').fetchone()[0] == 1
    marker.touch()
for root in (config, books):
    for parent, dirs, files in os.walk(root):
        os.chown(parent, 1000, 1000)
        for name in files:
            os.chown(Path(parent) / name, 1000, 1000)
with sqlite3.connect(books / 'metadata.db') as db:
    assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    print('Library book count:', db.execute('SELECT count(*) FROM books').fetchone()[0])
with sqlite3.connect(config / 'app.db') as db:
    print('Security configuration:', db.execute('SELECT config_anonbrowse, config_public_reg, config_calibre_dir FROM settings').fetchone())
    print('Administrator:', db.execute('SELECT name, email FROM user WHERE role & 1 = 1').fetchall())
subprocess.run(['df', '-h', '/books', '/config'], check=True)
print('Books bootstrap complete')
