const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

function load(name, globals = {}) {
  const context = vm.createContext(globals);
  const file = path.join(__dirname, '..', 'js', name + '.js');
  vm.runInContext(fs.readFileSync(file, 'utf8'), context, {filename: file});
  return context;
}

test('the API client signals recorded responses and sends distinct generation keys without a DOM', async () => {
  const requests = [];
  const context = load('api', {EventTarget, Event, fetch: async (url, options) => {
    requests.push({url, options});
    return new Response(JSON.stringify({id:'draft'}), {headers:{'X-TeachFlow-Demo':'recorded'}});
  }});
  const client = vm.runInContext('({roadmapApi, apiEvents})', context);
  let recorded = false;
  client.apiEvents.addEventListener('recorded-demo', () => { recorded = true; });
  await client.roadmapApi.generate('course', 'attempt-one');
  await client.roadmapApi.generate('course', 'attempt-two');
  assert.equal(recorded, true);
  assert.deepEqual(requests.map(r => r.url), Array(2).fill('/api/v1/courses/course/roadmaps/generate'));
  assert.deepEqual(requests.map(r => r.options.headers['Idempotency-Key']), ['attempt-one','attempt-two']);
});

test('an API validation failure preserves the server message and status for the editor', async () => {
  const error = {error:{details:[{msg:'Choose a supporting passage.'}]}};
  const context = load('api', {EventTarget, Event, fetch: async () => new Response(JSON.stringify(error), {status:422})});
  await assert.rejects(context.apiRequest('/roadmaps/id'), {message:'Choose a supporting passage.',status:422});
});

test('the selected course exposes a distinct open action for every pending proposal', () => {
  const context = load('workspace');
  const kinds = ['roadmap','review','package'];
  const course = {name:'Python', approvals:kinds.map(kind=>({id:kind+'-id',kind,title:kind})), history:[]};
  const html = context.workspaceView('approvals',course,null,String);
  for (const kind of kinds) {
    assert.match(html, new RegExp('data-kind="'+kind+'" data-id="'+kind+'-id"'));
  }
  assert.match(context.workspaceView('approvals',{...course,approvals:[]},null,String), /No records to show/);
});

test('benchmark inputs stay hidden until the saved targets finish loading', () => {
  const context = load('workspace');
  const course = {name:'Python', overview:{monday:{sessions:[{
    title:'Loops', session_id:'loops', state:'upcoming', status:'on track', target_date:'2026-12-07'
  }]}}};
  const view = status => context.workspaceView('roadmap-progress', course, {id:'monday'}, String, status);
  assert.match(view('loading'), /role="status"/);
  assert.doesNotMatch(view('loading'), /data-action="save-target"/);
  assert.doesNotMatch(view('error'), /data-action="save-target"/);
  assert.match(view('ready'), /value="2026-12-07"/);
});
