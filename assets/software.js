(() => {
  const $ = (id) => document.getElementById(id);
  const escape = (value) => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const session = () => localStorage.getItem('nbapi-session-token') || '';
  let items = [], superAdmin = false, editing = null, previews = [], generation = 0, packages = [];
  const fields = ['name','version','platform','category','summary','description','requirements','changelog'];
  const bytes = n => n >= 1024**3 ? (n / 1024**3).toFixed(2) + ' GB' : n >= 1048576 ? (n / 1048576).toFixed(1) + ' MB' : n >= 1024 ? (n / 1024).toFixed(1) + ' KB' : n + ' B';
  const date = n => new Date(n * 1000).toLocaleDateString('zh-CN');
  const packagePlatform = p => p.platform !== '跨平台' ? p.platform : /(?:windows|win32|win64|win[-_.])|\.(exe|msi)$/i.test(p.filename) ? 'Windows' : /(?:macos|mac[-_.]|darwin)|\.(dmg|pkg)$/i.test(p.filename) ? 'macOS' : /(?:linux)|\.(deb|rpm|appimage)$/i.test(p.filename) ? 'Linux' : p.platform;
  const downloadLinks = x => x.published ? x.installers.map((p,i) => `<a class="btn primary" href="${escape(p.downloadUrl)}" title="${escape(p.filename)}">下载 ${escape(packagePlatform(p))}${x.installers.filter(q=>packagePlatform(q)===packagePlatform(p)).length>1 ? ' · 安装包 '+(i+1) : ''}<span>（${bytes(p.size)}）</span></a>`).join('') : '';
  async function api(path, options = {}) {
    const response = await fetch(path, {...options, headers: {'Authorization':'Bearer ' + session(), ...(options.body ? {'Content-Type':'application/json'} : {}), ...options.headers}});
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || '请求失败');
    return data;
  }
  function render() {
    const search = $('softwareSearch').value.trim().toLowerCase(), platform = $('softwarePlatform').value;
    const visible = items.filter(x => (!platform || x.platform === platform || x.installers.some(p=>packagePlatform(p)===platform)) && [x.name,x.version,x.summary,x.category].join(' ').toLowerCase().includes(search));
    $('softwareCount').textContent = visible.length + ' 个版本';
    $('softwareGrid').innerHTML = visible.length ? visible.map(x => `<article class="panel software-card">${x.screenshots.length && x.published ? `<img src="${escape(x.screenshots[0])}" alt="${escape(x.name)} 软件界面" loading="lazy" />` : '<div class="software-cover">NB</div>'}<div class="software-card-body"><div class="software-heading"><span class="tag blue">${escape(x.category)}</span>${!x.published ? '<span class="tag gray">未发布</span>' : ''}</div><h2>${escape(x.name)}</h2><p class="muted">${escape(x.summary)}</p><div class="software-meta"><span>${escape(x.platform)}</span><span>v${escape(x.version)}</span><span>${x.installers.length} 个安装包</span></div><small class="muted">更新于 ${date(x.updated_at)}</small><div class="auth-actions"><button class="btn" data-detail="${x.id}">查看说明</button>${downloadLinks(x)}${superAdmin ? `<button class="btn" data-edit="${x.id}">管理</button>` : ''}</div></div></article>`).join('') : '<div class="panel software-empty"><h2>暂无软件</h2><p class="muted">软件发布后会显示在这里。也可以调整搜索或系统筛选。</p></div>';
    $('softwareGrid').querySelectorAll('[data-detail]').forEach(b => b.onclick = () => detail(items.find(x => x.id === b.dataset.detail)));
    $('softwareGrid').querySelectorAll('[data-edit]').forEach(b => b.onclick = () => editor(items.find(x => x.id === b.dataset.edit)));
  }
  function detail(x) {
    const section = $('softwareDetail');
    section.hidden = false;
    section.innerHTML = `<div class="software-heading"><div><span class="tag blue">${escape(x.platform)} · v${escape(x.version)}</span><h2>${escape(x.name)}</h2></div><button class="btn" id="softwareDetailClose">关闭</button></div><p>${escape(x.summary)}</p><div class="software-gallery">${x.published ? x.screenshots.map(url => `<a href="${escape(url)}" target="_blank" rel="noopener"><img src="${escape(url)}" alt="${escape(x.name)} 界面截图" loading="lazy" /></a>`).join('') : '<p class="muted">草稿截图在发布后可查看。</p>'}</div><h3>功能说明与安装方法</h3><p class="software-text">${escape(x.description)}</p>${x.requirements ? `<h3>系统要求</h3><p class="software-text">${escape(x.requirements)}</p>` : ''}${x.changelog ? `<h3>版本更新</h3><p class="software-text">${escape(x.changelog)}</p>` : ''}${x.installers.map(p=>`<div class="software-file-info"><strong>${escape(p.platform)} · v${escape(x.version)} · ${bytes(p.size)}</strong><span>文件：${escape(p.filename)}</span><small>SHA-256：${escape(p.sha256)}</small></div>`).join('')}<div class="auth-actions">${downloadLinks(x)}</div>`;
    $('softwareDetailClose').onclick = () => section.hidden = true;
    section.scrollIntoView({behavior:'smooth',block:'start'});
  }
  function clearPreviews() { previews.forEach(URL.revokeObjectURL); previews = []; }
  function packageEditor() {
    $('softwareInstaller').required = !packages.length;
    $('softwarePackages').innerHTML = packages.map((p,i)=>`<div class="software-package-row"><span>${escape(p.filename)} · ${bytes(p.size)}${p.id?'（已上传）':''}</span><select class="auth-input" aria-label="${escape(p.filename)} 的系统" data-package="${i}">${['Windows','macOS','Linux','跨平台'].map(s=>`<option${s===p.platform?' selected':''}>${s}</option>`).join('')}</select><button type="button" class="btn" data-remove-package="${i}">移除</button></div>`).join('');
    $('softwarePackages').querySelectorAll('[data-package]').forEach(s=>s.onchange=()=>packages[Number(s.dataset.package)].platform=s.value);
    $('softwarePackages').querySelectorAll('[data-remove-package]').forEach(b=>b.onclick=()=>{ if($('softwareSubmit').disabled)return; packages.splice(Number(b.dataset.removePackage),1);packageEditor(); });
  }
  function editor(item = null) {
    if (!superAdmin) return;
    editing = item;
    $('softwareForm').reset();
    clearPreviews(); $('softwarePreview').innerHTML = '';
    packages = item ? item.installers.map(p=>({...p})) : [];
    packageEditor();
    fields.forEach(key => { if(item) $('softwareForm').elements.namedItem(key).value = item[key]; });
    $('softwarePublished').checked = item ? item.published : true;
    $('softwareScreenshots').required = !item;
    $('softwareEditorTitle').textContent = item ? '管理 ' + item.name + ' v' + item.version : '上传软件';
    $('softwareUploadStatus').textContent = item ? '现有安装包可保留、移除，或选择文件追加安装包。' : '';
    $('softwareEditor').hidden = false;
    $('softwareEditor').scrollIntoView({behavior:'smooth',block:'start'});
  }
  async function load() {
    if (!location.hash.startsWith('#downloads')) return;
    const version = ++generation;
    $('softwareStatus').textContent = '正在加载软件...';
    try {
      let me = null;
      if(session()) { try { me = await api('/api/me'); } catch {} }
      const allowed = me?.role === 'super_admin';
      const result = await api(allowed ? '/api/admin/software' : '/api/software');
      if(version !== generation) return;
      superAdmin = allowed; items = result.items;
      $('softwareNew').hidden = !allowed;
      if(!allowed) $('softwareEditor').hidden = true;
      $('softwareStatus').textContent = ''; render();
    } catch (e) { $('softwareStatus').textContent = '加载失败：' + e.message; }
  }
  function uploadRequest(file, index, total, body = file, headers = {}, offset = 0) {
    return new Promise((resolve,reject) => {
      const xhr = new XMLHttpRequest();
      xhr.open('POST','/api/admin/software/files');
      xhr.setRequestHeader('Authorization','Bearer ' + session());
      xhr.setRequestHeader('X-File-Name',encodeURIComponent(file.name));
      xhr.setRequestHeader('Content-Type','application/octet-stream');
      Object.entries(headers).forEach(([key,value]) => xhr.setRequestHeader(key,value));
      xhr.timeout = 300000;
      xhr.upload.onprogress = e => { $('softwareUploadStatus').textContent = `上传 ${index}/${total}：${file.name} ${e.lengthComputable ? Math.round((offset+e.loaded)/file.size*100)+'%' : ''}（正在校验）`; };
      xhr.onload = () => { try { const data=JSON.parse(xhr.responseText); if(xhr.status>=200&&xhr.status<300) resolve(data); else reject(new Error(data.error || '上传失败')); } catch { reject(new Error('上传失败，请检查文件大小和服务器连接')); } };
      xhr.onerror = xhr.ontimeout = () => reject(new Error('上传中断，请重试'));
      xhr.send(body);
    });
  }
  async function upload(file, index, total) {
    if (/\.(png|jpe?g|webp)$/i.test(file.name)) return (await uploadRequest(file,index,total)).id;
    const id = crypto.randomUUID().replaceAll('-',''), original = session();
    let result;
    for (let offset = 0; offset < file.size; offset += 8*1048576) {
      if (session() !== original) throw new Error('登录状态已变化，请重新登录');
      const chunk = file.slice(offset,offset+8*1048576);
      const hash = Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',await chunk.arrayBuffer())),b=>b.toString(16).padStart(2,'0')).join('');
      result = await uploadRequest(file,index,total,chunk,{'X-Upload-Id':id,'X-Upload-Offset':String(offset),'X-Upload-Total':String(file.size),'X-Chunk-SHA256':hash},offset);
      if (result.offset !== offset+chunk.size) throw new Error('分片确认失败，请重新上传');
    }
    if (!result?.id) throw new Error('安装包校验未完成，请重新上传');
    return result.id;
  }
  $('softwareForm').onsubmit = async e => {
    e.preventDefault();
    if (!superAdmin || $('softwareSubmit').disabled) return;
    const selected = packages.map(p=>({...p})), screenshots = Array.from($('softwareScreenshots').files);
    if(!selected.length || selected.some(p=>!p.size || p.size > 1024**3)) { $('softwareUploadStatus').textContent='请选择非空安装包，每个不能超过 1 GB（1024 MB）。'; return; }
    if(screenshots.length > 6 || screenshots.some(x => x.size > 8*1048576)) { $('softwareUploadStatus').textContent='最多 6 张截图，每张不超过 8 MB。'; return; }
    $('softwareSubmit').disabled = true; $('softwareCancel').disabled = true;
    const original = session();
    try {
      const payload = Object.fromEntries(fields.map(key => [key,$('softwareForm').elements.namedItem(key).value.trim()]));
      payload.published = $('softwarePublished').checked;
      const total = screenshots.length + selected.filter(p=>p.file).length; let index=0;
      payload.installers = [];
      for (const p of selected) payload.installers.push({id:p.file ? await upload(p.file,++index,total) : p.id,platform:p.platform});
      payload.platform = new Set(selected.map(p=>p.platform)).size > 1 ? '跨平台' : selected[0].platform;
      if(screenshots.length) { payload.screenshotIds = []; for(const image of screenshots) payload.screenshotIds.push(await upload(image,++index,total)); }
      if(session() !== original) throw new Error('登录状态已变化，请重新登录');
      await api(editing ? '/api/admin/software/' + editing.id : '/api/admin/software', {method:editing?'PUT':'POST',body:JSON.stringify(payload)});
      $('softwareUploadStatus').textContent = '保存成功。';
      $('softwareEditor').hidden = true; $('softwareDetail').hidden = true; clearPreviews();
      await load();
    } catch(error) { $('softwareUploadStatus').textContent='保存失败：'+error.message; }
    finally { $('softwareSubmit').disabled=false; $('softwareCancel').disabled=false; }
  };
  $('softwareScreenshots').onchange = () => {
    clearPreviews();
    previews=Array.from($('softwareScreenshots').files).slice(0,6).filter(x => ['image/png','image/jpeg','image/webp'].includes(x.type)).map(URL.createObjectURL);
    $('softwarePreview').innerHTML=previews.map(url=>`<img src="${url}" alt="待上传的软件截图" />`).join('');
  };
  $('softwareInstaller').onchange = () => {
    for (const file of $('softwareInstaller').files) {
      if (!packages.some(p=>p.filename===file.name && p.size===file.size)) packages.push({file,filename:file.name,size:file.size,platform:/\.(dmg|pkg)$/i.test(file.name)?'macOS':/\.(deb|rpm|appimage)$/i.test(file.name)?'Linux':$('softwareSystem').value});
    }
    $('softwareInstaller').value = '';
    packageEditor();
  };
  $('softwareNew').onclick=()=>editor();
  $('softwareCancel').onclick=()=>{ $('softwareEditor').hidden=true; clearPreviews(); };
  $('softwareSearch').oninput=render; $('softwarePlatform').onchange=render;
  window.addEventListener('hashchange',load);
  $('authLogout').addEventListener('click',()=>{ ++generation;superAdmin=false;items=[];$('softwareNew').hidden=true;$('softwareEditor').hidden=true;$('softwareDetail').hidden=true;render(); });
  load();
})();
