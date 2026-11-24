// Keep live controls and event handlers when their rendered values have not changed.
const renderedAttributes = new WeakMap();
const regionMarkup = new WeakMap();

function sourceElement(node) {
  return node.classList?.contains('tf-select') ? node.querySelector('select') : node;
}

function nodeKey(node) {
  const el = sourceElement(node);
  if (!el.dataset) return '';
  return el.id || el.dataset.key || el.dataset.group ||
    [el.dataset.action, el.dataset.id, el.dataset.index, el.dataset.type].filter(Boolean).join('/');
}

function syncElement(current, next) {
  if (current.nodeType !== Node.ELEMENT_NODE) {
    if (current.nodeValue !== next.nodeValue) current.nodeValue = next.nodeValue;
    return;
  }
  const previous = renderedAttributes.get(current) || {};
  const attrs = Object.fromEntries(Array.from(next.attributes, a => [a.name, a.value]));
  for (const name of Object.keys(previous)) {
    if (!(name in attrs)) current.removeAttribute(name);
  }
  for (const [name, value] of Object.entries(attrs)) {
    if (previous[name] !== value) current.setAttribute(name, value);
  }
  renderedAttributes.set(current, attrs);
  syncChildren(current, next);
  if (current.matches('select') && current.parentElement?.matches('.tf-select')) {
    const label = current.parentElement.querySelector('.tf-select-value');
    if (label) label.textContent = current.selectedOptions[0]?.textContent || 'Choose an option';
  }
}

function syncChildren(parent, template) {
  const available = Array.from(parent.childNodes);
  const keyed = new Map(available.filter(nodeKey).map(n => [nodeKey(n), n]));
  let cursor = parent.firstChild;
  for (const next of template.childNodes) {
    const key = nodeKey(next);
    let live = key ? keyed.get(key) : cursor;
    if (!live || sourceElement(live).nodeName !== next.nodeName || nodeKey(live) !== key) {
      live = next.cloneNode(false);
    }
    if (live !== cursor) parent.insertBefore(live, cursor);
    syncElement(sourceElement(live), next);
    cursor = live.nextSibling;
  }
  while (cursor) {
    const removed = cursor;
    cursor = cursor.nextSibling;
    removed.remove();
  }
}

function patchRegion(root, markup, fresh = false) {
  if (!fresh && regionMarkup.get(root) === markup) return false;
  const template = document.createElement('template');
  template.innerHTML = markup;
  if (fresh) root.replaceChildren();
  syncChildren(root, template.content);
  regionMarkup.set(root, markup);
  return true;
}

const pagePositions = new Map();
let mountedPage = '';
function rememberPage(content, key) {
  const graph = content.querySelector('#roadmap-scroll');
  const inner = content.querySelector('#roadmap-inner');
  const position = pagePositions.get(key) || {};
  position.y = window.scrollY;
  if (graph) Object.assign(position, {x:graph.scrollLeft, top:graph.scrollTop, zoom:Number(inner.dataset.zoom || 1)});
  pagePositions.set(key, position);
}
