function remindersView(facts, escape) {
  if (!facts?.reminders?.length) return '';
  return `<section class="panel"><h2>Prerequisites to review</h2>${facts.reminders.map(row=>
    `<p>${escape(row.session)} requires ${escape(row.missing)}.
    <button class="btn" data-action="open-session" data-id="${escape(row.missing_id)}">Open ${escape(row.missing)}</button></p>`).join('')}</section>`;
}

function skeletonView(title) {
  return `<section aria-busy="true"><h1>${title}</h1><span class="sr-loading" role="status">Loading saved records…</span>
    <div class="skeleton-list" aria-hidden="true">${'<div class="skeleton skeleton-row"></div>'.repeat(3)}</div></section>`;
}

function workspaceView(screen, course, group, escape, loadStatus = 'ready') {
  const titles = {'materials':'Materials','approvals':'Pending approvals','roadmap-list':'Session list','roadmap-progress':'Group benchmarks'};
  if (!titles[screen]) return null;
  if (loadStatus === 'loading') {
    return skeletonView(titles[screen]);
  }
  // The shared page alert supplies the error and retry button.
  if (loadStatus === 'error') return `<section><h1>${titles[screen]}</h1></section>`;
  const facts = course?.overview?.[group?.id];
  let rows = [];
  if (screen === 'materials') {
    rows = (course?.materials || []).map(m=>`<article class="group" data-key="${escape(m.id)}"><h3>${escape(m.name)}</h3><p>${escape(m.status)} · ${escape(m.errorMessage || '')}</p>
      <ul>${(m.chunks||[]).map(c=>`<li>${escape(c.locator)}</li>`).join('')}</ul></article>`);
  } else if (screen === 'approvals') {
    rows = (course?.approvals || []).map(item=>`<button class="btn" data-action="review-pending" data-kind="${escape(item.kind)}" data-id="${escape(item.id)}">Review ${escape(item.title)}</button>`);
  } else if (screen === 'roadmap-list') {
    rows = (course?.topics || []).map((s,i)=>`<article class="group" data-key="${escape(s.id)}"><button class="btn" data-action="open-session" data-id="${escape(s.id)}">${i+1}. ${escape(s.title)}</button>
    <p>${escape(s.description)}</p><ul>${(course.edges||[]).filter(e=>e[1]===s.id).map(e=>`<li>${escape(e[2]||'prerequisite')} from ${escape(course.topics.find(t=>t.id===e[0])?.title || e[0])}</li>`).join('')}</ul></article>`);
  } else {
    rows = (facts?.sessions || []).map(s=>`<article class="group" data-key="${escape(s.session_id)}"><h3>${escape(s.title)}</h3><p>${escape(s.state)} · ${escape(s.status)}</p>
      <label>Target date<input type="date" value="${escape(s.target_date || '')}"></label>
      <button class="btn" data-action="save-target" data-id="${escape(s.session_id)}">Save target</button></article>`);
  }
  return `<section><h1>${titles[screen]}</h1><p>${escape(course?.name || 'Choose a course')}${group ? ' · '+escape(group.name) : ''}</p>
    ${screen==='roadmap-progress'?remindersView(facts,escape):''}<div class="groups">${rows.join('')||'<p>No records to show.</p>'}</div>
    ${screen==='approvals'?`<h2>Approval history</h2><ul>${(course?.history||[]).map(e=>`<li>${escape(e.timestamp)} · ${escape(e.item)} · ${escape(e.state)}</li>`).join('')||'<li>No changes yet.</li>'}</ul>`:''}</section>`;
}

function showFixtureBanner() {
  const banner = document.createElement('p');
  banner.id = 'fixture-mode';
  banner.textContent = 'Synthetic demonstration · recorded provider responses';
  document.body.prepend(banner);
}
