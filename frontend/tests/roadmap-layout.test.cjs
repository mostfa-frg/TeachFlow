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
