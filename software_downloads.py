"""Isolated software catalog and streamed file uploads; no billing dependencies."""
from contextlib import contextmanager
import hashlib
import json
import os
import re
import sqlite3
import time
import uuid
from pathlib import Path
from urllib.parse import quote, unquote, urlparse

INSTALLERS = {'.exe', '.msi', '.zip', '.7z', '.dmg', '.pkg', '.deb', '.rpm', '.appimage', '.tar.gz'}
IMAGES = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp'}
INSTALLER_LIMIT = 1024 ** 3
CHUNK_LIMIT = 8 * 1024 ** 2


@contextmanager
def connection(db_path):
    db = sqlite3.connect(db_path)
    try:
        with db:
            yield db
    finally:
        db.close()


def init_db(db_path):
    with connection(db_path) as db:
        db.executescript('''
        CREATE TABLE IF NOT EXISTS software_files (
          id TEXT PRIMARY KEY, owner_id INTEGER NOT NULL, filename TEXT NOT NULL,
          kind TEXT NOT NULL, content_type TEXT NOT NULL, size INTEGER NOT NULL,
          sha256 TEXT NOT NULL, created_at INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS software_releases (
          id TEXT PRIMARY KEY, name TEXT NOT NULL, version TEXT NOT NULL,
          platform TEXT NOT NULL, category TEXT NOT NULL, summary TEXT NOT NULL,
          description TEXT NOT NULL, requirements TEXT NOT NULL, changelog TEXT NOT NULL,
          installer_id TEXT NOT NULL, screenshots TEXT NOT NULL,
          published INTEGER NOT NULL DEFAULT 1, created_at INTEGER NOT NULL,
          updated_at INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS software_release_installers (
          release_id TEXT NOT NULL, file_id TEXT NOT NULL, platform TEXT NOT NULL,
          position INTEGER NOT NULL, PRIMARY KEY(release_id,file_id));
        ''')


def storage_root(db_path):
    return Path(os.environ.get('NBAPI_SOFTWARE_DIR', str(Path(db_path).parent / 'software-storage')))


def serialize(row, db):
    item = dict(row)
    file = db.execute('SELECT filename,size,sha256 FROM software_files WHERE id=?', (item.pop('installer_id'),)).fetchone()
    item.update(filename=file[0], size=file[1], sha256=file[2], downloadUrl='/api/software/' + item['id'] + '/download')
    item['screenshots'] = ['/api/software/' + item['id'] + '/screenshots/' + str(i) for i, _ in enumerate(json.loads(item['screenshots']))]
    item['published'] = bool(item['published'])
    packages = db.execute('SELECT f.id,f.filename,f.size,f.sha256,p.platform FROM software_release_installers p JOIN software_files f ON f.id=p.file_id WHERE p.release_id=? ORDER BY p.position', (item['id'],)).fetchall()
    item['installers'] = [dict(p) for p in packages] if packages else [dict(id=row['installer_id'], filename=item['filename'], size=item['size'], sha256=item['sha256'], platform=item['platform'])]
    for package in item['installers']:
        package['downloadUrl'] = '/api/software/' + item['id'] + '/download/' + package['id']
    return item


def metadata(payload):
    values = {}
    for key, limit, required in [('name',80,True),('version',40,True),('platform',80,True),('category',40,True),('summary',240,True),('description',12000,True),('requirements',2000,False),('changelog',6000,False)]:
        value = str(payload.get(key, '')).strip()
        if (required and not value) or len(value) > limit:
            raise ValueError('请填写有效的软件信息：' + key)
        values[key] = value
    if not isinstance(payload.get('published', True), bool):
        raise ValueError('发布状态无效')
    values['published'] = int(payload.get('published', True))
    return values


def send_blob(handler, path, file, attachment):
    size = file['size']
    start, end, status = 0, size - 1, 200
    range_header = handler.headers.get('Range')
    if range_header:
        match = re.fullmatch(r'bytes=(\d*)-(\d*)', range_header)
        if not match or (not match[1] and not match[2]):
            handler.send_json(416, {'error':'invalid_range'}, {'Content-Range':f'bytes */{size}'})
            return
        if not match[1]:
            start = max(0, size - int(match[2]))
        else:
            start = int(match[1])
            end = min(end, int(match[2])) if match[2] else end
        if start > end or start >= size:
            handler.send_json(416, {'error':'invalid_range'}, {'Content-Range':f'bytes */{size}'})
            return
        status = 206
    try:
        stream = path.open('rb')
    except FileNotFoundError:
        handler.send_json(404, {'error':'file_not_found'})
        return
    with stream:
        handler.send_response(status)
        handler.send_header('Content-Type', 'application/octet-stream' if attachment else file['content_type'])
        handler.send_header('Content-Length', str(end - start + 1))
        handler.send_header('Accept-Ranges', 'bytes')
        handler.send_header('X-Content-Type-Options', 'nosniff')
        handler.send_header('Cache-Control', 'no-store')
        if attachment:
            handler.send_header('Content-Disposition', "attachment; filename=software-download; filename*=UTF-8''" + quote(file['filename'], safe=''))
        if status == 206:
            handler.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        handler.end_headers()
        stream.seek(start)
        remaining = end - start + 1
        try:
            while remaining:
                chunk = stream.read(min(1024 * 1024, remaining))
                if not chunk:
                    break
                handler.wfile.write(chunk)
                remaining -= len(chunk)
        except (BrokenPipeError, ConnectionResetError):
            pass


def handle(handler, method, db_path):
    path = urlparse(handler.path).path
    public = path == '/api/software' or path.startswith('/api/software/')
    admin_path = path == '/api/admin/software' or path.startswith('/api/admin/software/')
    if not public and not admin_path:
        return False
    admin = None
    if admin_path:
        admin = handler.require_user(admin=True)
        if not admin:
            return True
        if admin[2] != 'super_admin':
            handler.send_json(403, {'error':'super_admin_only'})
            return True
    if method == 'POST' and path == '/api/admin/software/files':
        upload(handler, db_path, admin[0])
        return True
    with connection(db_path) as db:
        db.row_factory = sqlite3.Row
        if method == 'GET' and path in ('/api/software', '/api/admin/software'):
            rows = db.execute('SELECT * FROM software_releases' + ('' if admin else ' WHERE published=1') + ' ORDER BY updated_at DESC,id').fetchall()
            handler.send_json(200, {'items':[serialize(row, db) for row in rows]})
            return True
        match = re.fullmatch(r'/api/software/([a-f0-9]{32})/(download(?:/([a-f0-9]{32}))?|screenshots/(\d+))', path)
        if method == 'GET' and match:
            row = db.execute('SELECT * FROM software_releases WHERE id=? AND published=1', (match[1],)).fetchone()
            if row:
                try:
                    if match[2].startswith('download'):
                        fid = match[3] or row['installer_id']
                        if fid != row['installer_id'] and not db.execute('SELECT 1 FROM software_release_installers WHERE release_id=? AND file_id=?', (row['id'],fid)).fetchone():
                            raise IndexError()
                    else:
                        fid = json.loads(row['screenshots'])[int(match[4])]
                    file = db.execute('SELECT * FROM software_files WHERE id=?', (fid,)).fetchone()
                    send_blob(handler, storage_root(db_path) / fid, file, match[2].startswith('download'))
                    return True
                except (IndexError, TypeError):
                    pass
            handler.send_json(404, {'error':'software_not_found'})
            return True
        if admin and ((method == 'POST' and path == '/api/admin/software') or (method == 'PUT' and re.fullmatch(r'/api/admin/software/[a-f0-9]{32}', path))):
            try:
                payload = handler.read_json()
                if not isinstance(payload, dict):
                    raise ValueError('无效的软件信息')
                values = metadata(payload)
                rid = uuid.uuid4().hex if method == 'POST' else path.rsplit('/',1)[1]
                old = db.execute('SELECT * FROM software_releases WHERE id=?', (rid,)).fetchone()
                if method == 'PUT' and not old:
                    handler.send_json(404, {'error':'software_not_found'})
                    return True
                installer = payload.get('installerId', old['installer_id'] if old else '')
                packages = payload.get('installers')
                if packages is None:
                    existing = db.execute('SELECT file_id AS id,platform FROM software_release_installers WHERE release_id=? ORDER BY position',(rid,)).fetchall() if old and 'installerId' not in payload else []
                    packages = [dict(p) for p in existing] or [{'id':installer,'platform':values['platform']}]
                if not isinstance(packages,list) or not packages or any(not isinstance(p,dict) or not isinstance(p.get('id'),str) or p.get('platform') not in ('Windows','macOS','Linux','跨平台') for p in packages):
                    raise ValueError('请上传安装包并选择对应系统')
                if len(set(p['id'] for p in packages)) != len(packages):
                    raise ValueError('安装包不能重复')
                installer = packages[0]['id']
                screenshots = payload.get('screenshotIds', json.loads(old['screenshots']) if old else [])
                if not isinstance(screenshots, list) or not 1 <= len(screenshots) <= 6 or len(set(screenshots)) != len(screenshots):
                    raise ValueError('请上传 1–6 张软件界面截图')
                for fid, kind in [*[(p['id'],'installer') for p in packages], *[(fid,'image') for fid in screenshots]]:
                    file = db.execute('SELECT kind FROM software_files WHERE id=?', (fid,)).fetchone()
                    if not file or file['kind'] != kind:
                        raise ValueError('文件无效，请重新上传')
                now = int(time.time())
                if old:
                    db.execute('UPDATE software_releases SET name=?,version=?,platform=?,category=?,summary=?,description=?,requirements=?,changelog=?,published=?,installer_id=?,screenshots=?,updated_at=? WHERE id=?', (*values.values(),installer,json.dumps(screenshots),now,rid))
                else:
                    db.execute('INSERT INTO software_releases(id,name,version,platform,category,summary,description,requirements,changelog,published,installer_id,screenshots,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)', (rid,*values.values(),installer,json.dumps(screenshots),now,now))
                db.execute('DELETE FROM software_release_installers WHERE release_id=?',(rid,))
                db.executemany('INSERT INTO software_release_installers VALUES (?,?,?,?)',[(rid,p['id'],p['platform'],i) for i,p in enumerate(packages)])
                item = serialize(db.execute('SELECT * FROM software_releases WHERE id=?',(rid,)).fetchone(), db)
                db.commit()
                handler.send_json(200 if old else 201, {'item':item})
            except (ValueError, TypeError, sqlite3.Error) as exc:
                handler.send_json(400, {'error':str(exc)})
            return True
    handler.send_json(404, {'error':'not_found'})
    return True


def upload(handler, db_path, owner_id):
    if handler.headers.get('X-Upload-Id'):
        upload_chunk(handler, db_path, owner_id)
        return
    temp = None
    try:
        length = int(handler.headers.get('Content-Length','0'))
        filename = unquote(handler.headers.get('X-File-Name',''))
        if not filename or len(filename) > 180 or any(ord(c) < 32 for c in filename) or '/' in filename or '\\' in filename:
            raise ValueError('文件名无效')
        suffix = Path(filename).suffix.lower()
        kind = 'image' if suffix in IMAGES else 'installer'
        if kind == 'installer' and suffix not in INSTALLERS and not filename.lower().endswith('.tar.gz'):
            raise ValueError('不支持此安装包格式')
        limit = CHUNK_LIMIT if kind == 'image' else INSTALLER_LIMIT
        if length <= 0 or length > limit:
            handler.close_connection = True
            handler.send_json(413, {'error':'截图不超过 8 MB，安装包不超过 1 GB'})
            return
        root = storage_root(db_path)
        root.mkdir(parents=True, exist_ok=True)
        fid = uuid.uuid4().hex
        temp = root / (fid + '.partial')
        digest = hashlib.sha256()
        remaining = length
        head = b''
        with temp.open('xb') as stream:
            while remaining:
                chunk = handler.rfile.read(min(1024 * 1024, remaining))
                if not chunk:
                    raise ValueError('上传中断，请重试')
                if not head:
                    head = chunk[:16]
                digest.update(chunk)
                stream.write(chunk)
                remaining -= len(chunk)
        if kind == 'image':
            valid = (suffix == '.png' and head.startswith(b'\x89PNG\r\n\x1a\n')) or (suffix in ('.jpg','.jpeg') and head.startswith(b'\xff\xd8\xff')) or (suffix == '.webp' and head.startswith(b'RIFF') and head[8:12] == b'WEBP')
            if not valid:
                raise ValueError('截图格式与图片内容不匹配')
        final = root / fid
        temp.replace(final)
        try:
            with connection(db_path) as db:
                db.execute('INSERT INTO software_files VALUES (?,?,?,?,?,?,?,?)', (fid,owner_id,filename,kind,IMAGES.get(suffix,'application/octet-stream'),length,digest.hexdigest(),int(time.time())))
        except Exception:
            final.unlink(missing_ok=True)
            raise
        handler.send_json(201, {'id':fid,'filename':filename,'size':length,'sha256':digest.hexdigest()})
    except (ValueError, OSError) as exc:
        handler.close_connection = True
        handler.send_json(400, {'error':str(exc)})
    finally:
        if temp:
            temp.unlink(missing_ok=True)


def upload_chunk(handler, db_path, owner_id):
    """Verify every original byte range before assembling a private installer."""
    lock = None
    acquired = False
    try:
        fid = handler.headers['X-Upload-Id']
        filename = unquote(handler.headers.get('X-File-Name', ''))
        length = int(handler.headers.get('Content-Length', '0'))
        offset = int(handler.headers.get('X-Upload-Offset', '-1'))
        total = int(handler.headers.get('X-Upload-Total', '0'))
        expected = handler.headers.get('X-Chunk-SHA256', '')
        if not re.fullmatch(r'[a-f0-9]{32}', fid) or not re.fullmatch(r'[a-f0-9]{64}', expected):
            raise ValueError('上传标识或校验值无效')
        if not filename or len(filename) > 180 or any(ord(c) < 32 for c in filename) or '/' in filename or '\\' in filename:
            raise ValueError('文件名无效')
        if Path(filename).suffix.lower() not in INSTALLERS and not filename.lower().endswith('.tar.gz'):
            raise ValueError('不支持此安装包格式')
        if not 0 < total <= INSTALLER_LIMIT or not 0 < length <= CHUNK_LIMIT:
            handler.close_connection = True
            handler.send_json(413, {'error':'安装包不超过 1 GB，每片不超过 8 MB'})
            return
        if offset < 0 or offset + length > total:
            raise ValueError('分片位置无效')
        root = storage_root(db_path)
        root.mkdir(parents=True, exist_ok=True)
        lock = root / (fid + '.lock')
        try:
            lock.mkdir()
            acquired = True
        except FileExistsError:
            raise ValueError('文件正在上传，请重试')
        temp, meta = root / (fid + '.partial'), root / (fid + '.upload.json')
        if (root / fid).exists():
            raise ValueError('上传已经完成，请重新选择文件')
        state = json.loads(meta.read_text('utf-8')) if meta.exists() else {'owner':owner_id, 'filename':filename, 'total':total, 'offset':0, 'chunks':[]}
        if (state['owner'], state['filename'], state['total'], state['offset']) != (owner_id, filename, total, offset):
            raise ValueError('分片顺序或所属文件不匹配，请重新上传')
        if temp.exists() and temp.stat().st_size < offset:
            raise ValueError('上传文件不完整，请重新上传')
        if offset and not temp.exists():
            raise ValueError('上传文件不存在，请重新上传')
        # One bounded chunk in memory; never buffer the whole installer.
        body = bytearray()
        while len(body) < length:
            part = handler.rfile.read(min(1024 * 1024, length - len(body)))
            if not part:
                raise ValueError('上传中断，请重试')
            body.extend(part)
        if hashlib.sha256(body).hexdigest() != expected:
            raise ValueError('分片校验失败，请重新上传')
        with temp.open('r+b' if temp.exists() else 'xb') as stream:
            stream.truncate(offset)
            stream.seek(offset)
            stream.write(body)
        state['chunks'].append([length, expected])
        state['offset'] += length
        next_meta = root / (fid + '.upload.next')
        next_meta.write_text(json.dumps(state), encoding='utf-8')
        next_meta.replace(meta)
        if state['offset'] != total:
            handler.send_json(200, {'offset':state['offset']})
            return
        digest = hashlib.sha256()
        with temp.open('rb') as stream:
            for size, checksum in state['chunks']:
                chunk = stream.read(size)
                if len(chunk) != size or hashlib.sha256(chunk).hexdigest() != checksum:
                    raise ValueError('安装包完整性校验失败，请重新上传')
                digest.update(chunk)
        final = root / fid
        temp.replace(final)
        try:
            with connection(db_path) as db:
                db.execute('INSERT INTO software_files VALUES (?,?,?,?,?,?,?,?)', (fid,owner_id,filename,'installer','application/octet-stream',total,digest.hexdigest(),int(time.time())))
        except Exception:
            final.unlink(missing_ok=True)
            raise
        meta.unlink(missing_ok=True)
        handler.send_json(201, {'id':fid, 'offset':total, 'filename':filename, 'size':total, 'sha256':digest.hexdigest()})
    except (ValueError, OSError, KeyError, sqlite3.Error) as exc:
        handler.close_connection = True
        handler.send_json(400, {'error':str(exc)})
    finally:
        if acquired:
            lock.rmdir()
