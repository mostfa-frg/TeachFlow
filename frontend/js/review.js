function mountReview(root, route, escape, reportFailure, changed) {
  const status = document.createElement('p');
  status.setAttribute('role','status');
  const body = document.createElement('div');
  root.replaceChildren(status,body);
  let review, bundle, lastAction;
  async function perform(label, action) {
    lastAction = action;
    status.textContent = 'Working…';
    body.inert = true;
    try {
      await action();
      status.textContent = '';
    } catch (error) {
      status.textContent = reportFailure(label,error) + ' ';
      const retry = document.createElement('button');
      retry.textContent = 'Retry';
      retry.onclick = () => perform(label,lastAction);
      status.append(retry);
    } finally { body.inert = false; }
  }
  const modeLabel = mode => mode==='manual' ? 'Manual drafting · AI unavailable' : 'AI-generated proposal';
  async function list() {
    const rows = await reviewApi.list(route.group,route.session);
    body.innerHTML = `<h2>Session transcripts</h2><label>Synthetic transcript (TXT or MD, up to 100 KB)
      <input id="transcript-file" type="file" accept=".txt,.md"></label><button type="button" class="btn" id="upload-transcript">Review transcript</button>
      ${rows.map(r=>`<p><button class="btn" data-review="${escape(r.id)}">${escape(r.filename)} · ${escape(r.state)}</button></p>`).join('')||'<p>No transcript reviews yet.</p>'}`;
    body.querySelector('#upload-transcript').onclick = () => perform('Could not review the transcript', async()=>{
      const file = body.querySelector('input').files[0];
      if (!file) throw new Error('Choose a transcript first.');
      showReview(await reviewApi.upload(route.group,route.session,file));
      await changed();
    });
    body.querySelectorAll('[data-review]').forEach(b=>b.onclick=()=>perform('Could not open the transcript review', async()=>showReview(await reviewApi.read(b.dataset.review))));
  }

  function showReview(record) {
    review = record;
    body.dataset.record='review/'+record.id;
    const locked = review.state==='approved';
    body.innerHTML = `<h2>${escape(review.title)} · transcript review</h2><p>${modeLabel(review.mode)} · ${escape(review.state)}</p>
      <details><summary>Transcript · ${escape(review.filename)}</summary><pre style="white-space:pre-wrap">${escape(review.transcript)}</pre></details>
      ${review.findings.map(f=>`<fieldset class="group" data-index="${f.objective_index}" ${locked?'disabled':''}><legend>${escape(review.objectives[f.objective_index])}</legend>
      <label>Coverage<select name="status">${['covered','partial','not observed','unclear'].map(k=>`<option ${f.status===k?'selected':''}>${k}</option>`).join('')}</select></label>
      <label>Confidence (0–1)<input name="confidence" type="number" step="0.01" min="0" max="1" value="${f.confidence}"></label>
      <div>${f.evidence.length?f.evidence.map(e=>`<blockquote>${escape(e.snippet)} <small>(chars ${e.start}–${e.end})</small></blockquote>`).join(''):'No evidence found.'}</div>
      ${locked?'':`<label>Evidence ranges, one start:end per line<textarea name="ranges" placeholder="0:35">${f.evidence.map(e=>e.start+':'+e.end).join('\n')}</textarea></label>`}</fieldset>`).join('')}
      ${locked?'<button class="btn primary" id="package">Open follow-up package</button>':'<button class="btn" id="save-findings">Save findings</button> <button class="btn primary" id="approve-review">Approve findings</button>'}`;
    if(root.isConnected)restoreFields(body,mountedPage);
    async function save(approve) {
      const findings = [...body.querySelectorAll('fieldset')].map(field=>{
        const evidence=field.querySelector('[name=ranges]').value.split(/\n/).filter(s=>s.trim()).map(range=>{
          if (!/^\d+:\d+$/.test(range.trim())) throw new Error('Enter each evidence range as start:end.');
          const [start,end] = range.trim().split(':').map(Number);
          return {start,end,snippet:Array.from(review.transcript).slice(start,end).join('')};
        });
        return {objective_index:Number(field.dataset.index),status:field.querySelector('select').value,
          confidence:Number(field.querySelector('[name=confidence]').value),evidence};
      });
      const saved=await reviewApi.save(review.id,findings);
      showReview(approve ? await reviewApi.approve(saved.id) : saved);
      await changed();
    }
    if (locked) body.querySelector('#package').onclick=()=>perform('Could not open the follow-up package', async()=>{showPackage(await reviewApi.draft(review.id));await changed();});
    else {
      body.querySelector('#save-findings').onclick=()=>perform('Could not save the findings', ()=>save(false));
      body.querySelector('#approve-review').onclick=()=>perform('Could not approve the findings', ()=>save(true));
    }
  }

  function showPackage(record, unsaved={}) {
    bundle = record;
    body.dataset.record='package/'+record.id;
    body.innerHTML = `<h2>Follow-up package</h2><p>${modeLabel(bundle.mode)} · ${escape(bundle.state)}</p>`+
      Object.entries(bundle.items).map(([key,item])=>`<section class="group" data-item="${escape(key)}"><label>${escape(key.replace('_',' '))} · ${escape(item.state)}
        <textarea ${item.state==='approved'?'readonly':''}>${escape(unsaved[key]??item.text)}</textarea></label>
        ${item.state==='approved'?'<button class="btn" data-copy>Copy</button>':'<button class="btn" data-save>Save draft</button> <button class="btn primary" data-approve>Approve item</button>'}</section>`).join('');
    if(root.isConnected)restoreFields(body,mountedPage);
    body.querySelectorAll('[data-item] button').forEach(button=>button.onclick=()=>perform(button.hasAttribute('data-copy')?'Could not copy the item':button.hasAttribute('data-approve')?'Could not approve the item':'Could not save the item', async()=>{
      const section=button.closest('[data-item]'), key=section.dataset.item, text=section.querySelector('textarea').value;
      if (button.hasAttribute('data-copy')) { await navigator.clipboard.writeText(text); return; }
      const pending=Object.fromEntries([...body.querySelectorAll('[data-item]')].filter(s=>s!==section).map(s=>[s.dataset.item,s.querySelector('textarea').value]));
      showPackage(await reviewApi.item(bundle.id,key,text,button.hasAttribute('data-approve')),pending);
      await changed();
    }));
  }

  perform('Could not load '+(route.kind==='package'?'the follow-up package':'transcript reviews'), async()=>{
    if (route.kind==='review') showReview(await reviewApi.read(route.id));
    else if (route.kind==='package') showPackage(await reviewApi.package(route.id));
    else await list();
  });
}
