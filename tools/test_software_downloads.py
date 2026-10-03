"""Software publishing, storage and download access checks with real HTTP."""
import gc
import hashlib
import http.client
import json
import sqlite3
import tempfile
import threading
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

import server
import software_downloads


class SoftwareTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(gc.collect)
        self.db_path = Path(self.temp.name) / 'test.sqlite3'
        self.patch = patch.object(server, 'DB_PATH', self.db_path)
        self.patch.start(); self.addCleanup(self.patch.stop)
        with patch.object(server,'DEFAULT_SUPER_ADMIN_PASSWORD','test-password'):
            server.init_db()
        with sqlite3.connect(self.db_path) as db:
            sid = db.execute("SELECT id FROM users WHERE role='super_admin'").fetchone()[0]
            for role in ('admin','user'):
                uid = db.execute("INSERT INTO users(username,email,password_hash,role,active,balance_micros,created_at) VALUES (?,'','test',?,1,0,?)",(role,role,server.now())).lastrowid
                db.execute('INSERT INTO sessions VALUES (?,?,?)',(role,uid,server.now()+3600))
            db.execute('INSERT INTO sessions VALUES (?,?,?)',('super',sid,server.now()+3600))
        self.app = server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
        self.thread = threading.Thread(target=self.app.serve_forever,daemon=True)
        self.thread.start()
        self.addCleanup(self.stop)

    def stop(self):
        self.app.shutdown(); self.app.server_close(); self.thread.join()

    def request(self, method, path, body=None, token=None, headers=None):
        connection = http.client.HTTPConnection('127.0.0.1',self.app.server_port,timeout=5)
        options = headers or {}
        if token: options['Authorization'] = 'Bearer '+token
        if isinstance(body,dict):
            body=json.dumps(body).encode();options['Content-Type']='application/json'
        try:
            connection.request(method,path,body,options)
            response=connection.getresponse()
            raw=response.read();status=response.status;response_headers=dict(response.getheaders())
            return status,json.loads(raw) if response_headers.get('Content-Type','').startswith('application/json') else raw,response_headers
        finally: connection.close()

    def upload(self, name, body):
        status,data,_=self.request('POST','/api/admin/software/files',body,'super',{'X-File-Name':name,'Content-Type':'application/octet-stream'})
        self.assertEqual(status,201)
        return data['id']

    def payload(self):
        binary=b'PK\x03\x04software-test-content'
        screenshot=b'\x89PNG\r\n\x1a\nimage-test-content'
        return dict(name='NB tool',version='1.0.0',platform='Windows',category='AI 创作',summary='Test tool',description='Install and run',requirements='Windows 11',changelog='First release',published=True,installerId=self.upload('tool.zip',binary),screenshotIds=[self.upload('screen.png',screenshot)]),binary

    def test_publish_download_range_edit_and_hide(self):
        payload,binary=self.payload()
        status,data,_=self.request('POST','/api/admin/software',payload,'super')
        self.assertEqual(status,201);item=data['item']
        self.assertEqual(item['sha256'],hashlib.sha256(binary).hexdigest())
        self.assertEqual(self.request('GET','/api/software')[1]['items'][0]['version'],'1.0.0')
        status,body,headers=self.request('GET',item['downloadUrl'])
        self.assertEqual((status,body),(200,binary));self.assertIn('attachment',headers['Content-Disposition'])
        self.assertEqual(self.request('GET',item['downloadUrl'],headers={'Range':'bytes=2-5'})[:2],(206,binary[2:6]))
        self.assertEqual(self.request('GET',item['downloadUrl'],headers={'Range':'bytes=-4'})[:2],(206,binary[-4:]))
        self.assertEqual(self.request('GET',item['downloadUrl'],headers={'Range':'bytes=9999-'})[0],416)
        self.assertEqual(self.request('GET',item['screenshots'][0])[0],200)
        payload.update(published=False,version='1.0.1')
        self.assertEqual(self.request('PUT','/api/admin/software/'+item['id'],payload,'super')[0],200)
        self.assertEqual(self.request('GET','/api/software')[1]['items'],[])
        self.assertEqual(self.request('GET',item['downloadUrl'])[0],404)
        self.assertEqual(self.request('GET',item['screenshots'][0])[0],404)
        self.assertEqual(len(self.request('GET','/api/admin/software',token='super')[1]['items']),1)

    def test_role_permissions_and_invalid_uploads(self):
        for token in (None,'user','admin'):
            expected=401 if token is None else 403
            self.assertEqual(self.request('POST','/api/admin/software',{},token)[0],expected)
            self.assertEqual(self.request('POST','/api/admin/software/files',b'test',token,{'X-File-Name':'tool.zip'})[0],expected)
            self.assertEqual(self.request('GET','/api/admin/software',token=token)[0],expected)
        for name in ('../tool.zip','tool.html','screen.svg','screen.png'):
            self.assertEqual(self.request('POST','/api/admin/software/files',b'not-an-image','super',{'X-File-Name':name})[0],400)
        self.assertEqual(self.request('POST','/api/admin/software/files',b'x','super',{'X-File-Name':'tool.zip','Content-Length':str(1024**3+1)})[0],413)
        with sqlite3.connect(self.db_path) as db: self.assertEqual(db.execute('SELECT COUNT(*) FROM software_files').fetchone()[0],0)
        self.assertEqual(list(software_downloads.storage_root(self.db_path).glob('*.partial')),[])

    def test_missing_file_metadata_and_drafts_never_expose_unpublished_uploads(self):
        payload,_=self.payload()
        self.assertEqual(self.request('GET','/api/software/'+payload['installerId']+'/download')[0],404)
        payload['screenshotIds']=[]
        self.assertEqual(self.request('POST','/api/admin/software',payload,'super')[0],400)
        payload['screenshotIds']=[payload['installerId']]
        self.assertEqual(self.request('POST','/api/admin/software',payload,'super')[0],400)

    def chunk(self, fid, body, offset, total, **overrides):
        headers={'X-File-Name':'large.zip','X-Upload-Id':fid,'X-Upload-Offset':str(offset),'X-Upload-Total':str(total),'X-Chunk-SHA256':hashlib.sha256(body).hexdigest()}
        headers.update(overrides)
        return self.request('POST','/api/admin/software/files',body,'super',headers)

    def test_chunk_integrity_order_limits_and_private_partial(self):
        fid=uuid.uuid4().hex
        first=b'first-original-bytes';last=b'last-original-bytes';total=len(first)+len(last)
        self.assertEqual(self.chunk(fid,first,0,total,**{'X-Chunk-SHA256':'0'*64})[0],400)
        self.assertEqual(self.chunk(fid,first,0,total)[:2],(200,{'offset':len(first)}))
        with sqlite3.connect(self.db_path) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM software_files').fetchone()[0],0)
        self.assertEqual(self.request('GET','/api/software/'+fid+'/download')[0],404)
        self.assertEqual(self.chunk(fid,last,0,total)[0],400)
        self.assertEqual(self.chunk(fid,last,len(first),total,**{'X-File-Name':'different.zip'})[0],400)
        self.assertEqual(self.chunk(fid,last,len(first),total,**{'X-Upload-Total':str(total+1)})[0],400)
        meta=software_downloads.storage_root(self.db_path)/(fid+'.upload.json')
        state=json.loads(meta.read_text());state['owner']+=100
        meta.write_text(json.dumps(state))
        self.assertEqual(self.chunk(fid,last,len(first),total)[0],400)
        state['owner']-=100;meta.write_text(json.dumps(state))
        status,data,_=self.chunk(fid,last,len(first),total)
        self.assertEqual(status,201)
        self.assertEqual(data['sha256'],hashlib.sha256(first+last).hexdigest())
        self.assertEqual((software_downloads.storage_root(self.db_path)/fid).read_bytes(),first+last)
        self.assertEqual(self.chunk(fid,last,len(first),total)[0],400)
        self.assertEqual(self.chunk(uuid.uuid4().hex,b'x',0,1024**3+1)[0],413)
        # Exact 1 GiB is accepted without allocating a GiB; larger chunks/images rejected.
        self.assertEqual(self.chunk(uuid.uuid4().hex,b'x',0,1024**3)[0],200)
        self.assertEqual(self.chunk(uuid.uuid4().hex,b'x',0,1024**3,**{'Content-Length':str(8*1048576+1)})[0],413)
        self.assertEqual(self.upload_limit_image(),413)

    def upload_limit_image(self):
        return self.request('POST','/api/admin/software/files',b'x','super',{'X-File-Name':'image.png','Content-Length':str(8*1048576+1)})[0]

    def test_assembly_detects_disk_corruption(self):
        fid=uuid.uuid4().hex
        self.assertEqual(self.chunk(fid,b'abc',0,6)[0],200)
        (software_downloads.storage_root(self.db_path)/(fid+'.partial')).write_bytes(b'xyz')
        self.assertEqual(self.chunk(fid,b'def',3,6)[0],400)
        with sqlite3.connect(self.db_path) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM software_files').fetchone()[0],0)

    def test_multi_platform_packages_share_release_and_edit(self):
        payload,binary=self.payload()
        mac=self.upload('mac.dmg',b'mac-original')
        unrelated=self.upload('other.zip',b'private')
        payload['installers']=[{'id':payload['installerId'],'platform':'Windows'},{'id':mac,'platform':'macOS'}]
        payload['platform']='跨平台'
        status,data,_=self.request('POST','/api/admin/software',payload,'super')
        self.assertEqual(status,201);item=data['item']
        self.assertEqual(len(self.request('GET','/api/software')[1]['items']),1)
        self.assertEqual([p['platform'] for p in item['installers']],['Windows','macOS'])
        self.assertEqual(self.request('GET',item['installers'][0]['downloadUrl'])[:2],(200,binary))
        self.assertEqual(self.request('GET',item['installers'][1]['downloadUrl'])[:2],(200,b'mac-original'))
        self.assertEqual(self.request('GET',item['installers'][1]['downloadUrl'],headers={'Range':'bytes=1-3'})[:2],(206,b'ac-'))
        self.assertEqual(self.request('GET','/api/software/'+item['id']+'/download/'+unrelated)[0],404)
        payload.pop('installers');payload.pop('installerId');payload['version']='2.0'
        updated=self.request('PUT','/api/admin/software/'+item['id'],payload,'super')[1]['item']
        self.assertEqual(len(updated['installers']),2)
        payload['installers']=[{'id':mac,'platform':'macOS'}]
        self.assertEqual(self.request('PUT','/api/admin/software/'+item['id'],payload,'super')[0],200)
        self.assertEqual(self.request('GET',item['installers'][0]['downloadUrl'])[0],404)
        payload['published']=False
        self.assertEqual(self.request('PUT','/api/admin/software/'+item['id'],payload,'super')[0],200)
        self.assertEqual(self.request('GET',item['installers'][1]['downloadUrl'])[0],404)

    def test_legacy_single_package_without_association_is_compatible(self):
        payload,binary=self.payload()
        item=self.request('POST','/api/admin/software',payload,'super')[1]['item']
        with sqlite3.connect(self.db_path) as db:
            db.execute('DELETE FROM software_release_installers WHERE release_id=?',(item['id'],))
        legacy=self.request('GET','/api/software')[1]['items'][0]
        self.assertEqual(len(legacy['installers']),1)
        self.assertEqual(self.request('GET',legacy['installers'][0]['downloadUrl'])[:2],(200,binary))
        self.assertEqual(self.request('GET',legacy['downloadUrl'])[:2],(200,binary))

    def test_large_installer_over_100mb_exact_hash(self):
        fid=uuid.uuid4().hex;total=112*1048576+19
        digest=hashlib.sha256()
        for offset in range(0,total,8*1048576):
            body=bytes([offset//(8*1048576)])*min(8*1048576,total-offset)
            digest.update(body)
            status,data,_=self.chunk(fid,body,offset,total)
            self.assertEqual(status,201 if offset+len(body)==total else 200)
        self.assertEqual(data['size'],total)
        self.assertEqual(data['sha256'],digest.hexdigest())
        with (software_downloads.storage_root(self.db_path)/fid).open('rb') as stream:
            self.assertEqual(hashlib.file_digest(stream,'sha256').hexdigest(),digest.hexdigest())


if __name__ == '__main__': unittest.main()
