// Focused no-dependency UI regression tests: node --test frontend/tests/roadmap-layout.test.cjs
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)?.[1];
assert.ok(script, 'application script exists');
new vm.Script(script);
function getFunction(name) {
  const source = script.split('\n').find(line => line.startsWith('function ' + name + '('));
  assert.ok(source, name + ' is defined');
  return vm.runInNewContext('(' + source + ')');
}
const layout = getFunction('positionsFor');
const renderPaths = getFunction('roadmapSvg');
test('four sessions per row with alternating left-to-right/right-to-left order', () => {
  const sessions = Array.from({length: 13}, (_, i) => ({id: 's' + (i + 1)}));
  const {positions, width, height} = layout(sessions);
  assert.ok(positions.s1.x < positions.s2.x && positions.s2.x < positions.s3.x && positions.s3.x < positions.s4.x);
  assert.ok(positions.s5.x > positions.s6.x && positions.s6.x > positions.s7.x && positions.s7.x > positions.s8.x);
  assert.equal(positions.s4.x, positions.s5.x);
  assert.equal(positions.s8.x, positions.s9.x);
  assert.ok(height > positions.s13.y);
  assert.ok(width > positions.s4.x);
});
test('curved row transitions and additional graph links both remain visible', () => {
  const sessions = Array.from({length: 9}, (_, i) => ({id: 's' + (i + 1)}));
  const {positions, width, height} = layout(sessions);
  const svg = renderPaths(sessions, [['s1', 's9'], ['s4', 's5']], positions, width, height);
  assert.equal((svg.match(/class="edge roadmap-route"/g) || []).length, 8);
  assert.equal((svg.match(/class="edge dependency-edge"/g) || []).length, 1);
  assert.equal((svg.match(/ C /g) || []).length, 3);
});
test('notification has top-right placement and a timed shrinking progress bar', () => {
  assert.match(html, /\.toast\{position:fixed;top:18px;right:22px;bottom:auto/);
  assert.match(html, /@keyframes toast-countdown/);
  assert.match(html, /--toast-from:/);
  assert.match(html, /--toast-remaining:/);
  assert.match(script, /toastDeadline=Date\.now\(\)\+TOAST_DURATION/);
});
test('zoom scales the dynamic roadmap canvas rather than a fixed 660x460 view', () => {
  const source = script.split('\n').find(line => line.startsWith('function zoom('));
  assert.match(source, /baseWidth\*next/);
  assert.match(source, /baseHeight\*next/);
  assert.doesNotMatch(source, /660\*next/);
});

test('session click opens closed panel, then changes detail in place without full rerenders', () => {
  const source = script.split('\n').find(line => line.startsWith('function selectRoadmapNode('));
  assert.ok(source);
  const sessionA = {id: 's1', title: 'Intro'};
  const sessionB = {id: 's2', title: 'Next'};
  const state = {screen: 'roadmap', draft: null, selectedNode: 's1', selectedNodeManually: true, showDetail: false};
  let renders = 0, persists = 0, updates = 0;
  const panel = {outerHTML: ''};
  const buttons = [sessionA, sessionB].map(s => ({dataset: {id: s.id}, classList: {toggle(){}}, setAttribute(){}}));
  const select = vm.runInNewContext('(' + source + ')', {
    state, selectedCourse: () => ({topics: [sessionA, sessionB], edges: []}),
    persist: () => persists++, render: () => renders++, reviewEdit: () => {},
    document: {querySelectorAll: () => buttons, getElementById: () => panel},
    closeStyledSelect: () => {}, enhanceSelects: () => {},
    detailPanel: t => {updates++; return '<aside>' + t.title + '</aside>';}
  });
  select('s1'); // clicking current session still opens it when closed
  assert.equal(state.showDetail, true);
  assert.equal(renders, 1);
  select('s2');
  assert.equal(state.selectedNode, 's2');
  assert.equal(renders, 1, 'switching an open panel must not rerender the page');
  assert.equal(updates, 1);
  assert.match(panel.outerHTML, /Next/);
  assert.equal(persists, 2);
  select('s2');
  assert.equal(renders, 1);
  assert.equal(updates, 1, 'clicking an already active session does not recreate the sidebar');
  assert.match(script, /case'select-node':selectRoadmapNode\(b\.dataset\.id\);break/);
  assert.match(html, /\.reference-detail\.is-entering:not\(\.is-closed\)\{animation:detail-slide-in/);
});
test('roadmap header groups semantic action buttons with a larger toggle directly below', () => {
  const source = script.split('\n').find(line => line.startsWith('function roadmapPage('));
  assert.ok(source);
  const row = source.indexOf('class="roadmap-action-row"');
  const endRow = source.indexOf('</div><button class="btn roadmap-detail-toggle"', row);
  assert.ok(row > 0 && endRow > row, 'details toggle follows the action row');
  assert.match(source, /class="btn roadmap-edit-action"/);
  assert.match(source, /class="btn roadmap-delete-action"/);
  assert.match(source, /class="btn roadmap-new-action"/);
  assert.match(source, /aria-expanded="\$\{state\.showDetail\}"/);
  assert.match(html, /\.roadmap-header-actions \.roadmap-detail-toggle\{position:static/);
  assert.match(html, /width:48px;height:46px/);
  assert.match(html, /\.roadmap-edit-action\{background:var\(--blue-soft\)/);
  assert.match(html, /\.roadmap-delete-action\{background:var\(--terra-soft\)/);
  assert.match(html, /\.roadmap-new-action\{background:var\(--sage\)/);
});
test('custom dropdowns preserve native form values and support keyboard interaction', () => {
  assert.match(html, /\.tf-select-menu\{position:fixed/);
  assert.match(html, /\.tf-select-option\[aria-selected="true"\]/);
  assert.match(script, /function enhanceSelects\(root=document\)/);
  assert.match(script, /item\.setAttribute\('role','option'\)/);
  assert.match(script, /select\.dispatchEvent\(new Event\('change',\{bubbles:true\}\)\)/);
  assert.match(script, /event\.key==='Escape'/);
  assert.match(script, /enhanceSelects\(app\)/);
});

test('detail sidebar slides in only when becoming visible, not when switching sessions or rerendering', () => {
  assert.match(html, /@keyframes detail-slide-in/);
  assert.match(html, /\.reference-detail\{animation:none\}/);
  assert.match(html, /\.reference-detail\.is-entering:not\(\.is-closed\)\{animation:detail-slide-in/);
  assert.match(script, /let lastRenderedDetailVisible=false/);
  assert.match(script, /const entering=detailVisible&&!lastRenderedDetailVisible;lastRenderedDetailVisible=detailVisible/);
  assert.match(script, /if\(entering\)document\.getElementById\('session-detail-panel'\)\?\.classList\.add\('is-entering'\)/);
  const select = script.split('\n').find(line => line.startsWith('function selectRoadmapNode('));
  assert.doesNotMatch(select, /is-entering/);
  assert.match(html, /@media\(prefers-reduced-motion:reduce\)/);
});

test('labels are below the connector and long titles are clamped', () => {
  assert.match(html, /\.roadmap-card \.node strong\{/);
  assert.match(html, /-webkit-line-clamp:2/);
  assert.match(html, /translate\(-17px,-17px\)/);
  assert.match(html, /\.roadmap-card \.node \.nmeta>span:last-child\{/);
  assert.match(script, /title="\$\{escape\(t\.title\)\}"/);
});
test('route U-turns use separate outside gutters while keeping four nodes per row', () => {
  const sessions = Array.from({length: 28}, (_, i) => ({id:'s'+(i+1)}));
  const {positions,width,height} = layout(sessions);
  const svg = renderPaths(sessions,[],positions,width,height);
  assert.equal((svg.match(/class="edge roadmap-route"/g)||[]).length,27);
  assert.equal((svg.match(/ C /g)||[]).length,6);
  assert.match(svg, / H /);
  assert.ok(positions.s4.x + 160 < width);
  assert.ok(positions.s5.x === positions.s4.x);
  assert.ok(positions.s9.x === positions.s8.x);
  assert.ok(height > positions.s28.y + 100);
});
test('status-driven route highlighting is visual only and respects session order', () => {
  const sessions = Array.from({length: 4},(_,i)=>({id:'s'+(i+1)}));
  const {positions,width,height} = layout(sessions);
  const svg = renderPaths(sessions, [],positions,width,height,{s1:'done',s2:'done',s3:'active',s4:'upcoming'},'s3');
  assert.equal((svg.match(/data-state="completed"/g)||[]).length,1);
  assert.equal((svg.match(/data-state="active"/g)||[]).length,1);
  assert.equal((svg.match(/data-state="upcoming"/g)||[]).length,1);
  assert.match(html, /\.roadmap-card \.edge\.roadmap-route\[data-state="active"\]/);
  assert.match(script, /roadmapSvg\(topics,edges,positions,width,height,statuses,state\.selectedNode\)/);
});
test('small screens keep labels readable through minimum zoom and panning', () => {
  const source = script.split('\n').find(line => line.startsWith('function zoom('));
  assert.match(source,/minimumReadableZoom=wrap\.clientWidth<650\?\.78:\.72/);
  assert.match(html,/\.roadmap-scroll\{overscroll-behavior:contain/);
});
