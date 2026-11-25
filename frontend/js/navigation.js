// Keep live controls and event handlers when their rendered values have not changed.
const renderedAttributes = new WeakMap();
const regionMarkup = new WeakMap();

function sourceElement(node) {
  return node.classList?.contains('tf-select') ? node.querySelector('select') : node;
}

function nodeKey(node) {
  const el = sourceElement(node);
  if (!el.dataset) return '';
  return el.dataset.record || el.id || el.dataset.key || el.dataset.group ||
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
  if (next.hasAttribute('data-counter')) {
    if(current.dataset.target!==next.textContent)countTo(current,next.textContent);
    current.dataset.target=next.textContent;
  } else syncChildren(current, next);
  if (current.matches('select') && current.parentElement?.matches('.tf-select')) {
    const label = current.parentElement.querySelector('.tf-select-value');
    if (label) label.textContent = current.selectedOptions[0]?.textContent || 'Choose an option';
  }
}

function syncChildren(parent, template) {
  const before = measureList(parent, template);
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
  settleList(parent,before);
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

// Keep local edits while navigating. A changed server value takes precedence on return.
const fieldDrafts = new Map();
const editableFields = 'input:not([type=file]), textarea, select';
function fieldKey(field, page) {
  const row = field.closest('[data-group],[data-item],[data-key],fieldset[data-index]');
  const record = field.closest('[data-record]')?.dataset.record;
  return JSON.stringify([record || page, row && nodeKey(row), row?.dataset.item, row?.dataset.index,
    field.id || field.name || field.dataset.gfield || field.getAttribute('aria-label') || field.type]);
}

function fieldValue(field, initial) {
  if (field.tagName !== 'SELECT') return initial ? field.defaultValue : field.value;
  const values = Array.from(field.options).filter(o => initial ? o.defaultSelected : o.selected).map(o => o.value);
  if (initial && !values.length && !field.multiple && field.options.length) values.push(field.options[0].value);
  return JSON.stringify(values);
}

function rememberFields(root, page) {
  for (const field of root.querySelectorAll(editableFields)) {
    if (field.closest('#assistant-workspace') || field.matches(':disabled,[readonly]')) continue;
    const key = fieldKey(field,page), initial = fieldValue(field,true), value = fieldValue(field,false);
    if (initial === value) fieldDrafts.delete(key);
    else fieldDrafts.set(key,{initial,value});
  }
}

function restoreFields(root, page) {
  for (const field of root.querySelectorAll(editableFields)) {
    const key=fieldKey(field,page), draft=fieldDrafts.get(key);
    if (!draft) continue;
    fieldDrafts.delete(key);
    if (field.matches(':disabled,[readonly]') || draft.initial !== fieldValue(field,true)) continue;
    if (field.tagName === 'SELECT') {
      const values = JSON.parse(draft.value);
      for (const option of field.options) option.selected=values.includes(option.value);
      if(field.id==='session-citations')field.dataset.edited='true';
      const label=field.closest('.tf-select')?.querySelector('.tf-select-value');
      if(label)label.textContent=field.selectedOptions[0]?.textContent || 'Choose an option';
    } else if (field.value!==draft.value) field.value=draft.value;
  }
}

function rememberFocus(content, key) {
  const field=document.activeElement;
  if (!content.contains(field) || !field.matches(editableFields)) return;
  return {field, key:fieldKey(field,key), start:field.selectionStart, end:field.selectionEnd};
}

function restoreFocus(content, key, bookmark) {
  if (!bookmark || bookmark.field.isConnected) return;
  const field=[...content.querySelectorAll(editableFields)].find(el=>fieldKey(el,key)===bookmark.key);
  if (!field || field.disabled) return;
  field.focus({preventScroll:true});
  if (bookmark.start!=null) field.setSelectionRange(bookmark.start, bookmark.end);
}
