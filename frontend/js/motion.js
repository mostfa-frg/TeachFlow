const motionPreference = matchMedia('(prefers-reduced-motion: reduce)');
const easeOut = {duration:190, easing:'ease-out'};
let pendingTransition;
let transitionSerial = 0;

function switchScreen(key, direction, paint) {
  if (pendingTransition?.key === key) return;
  const serial = ++transitionSerial;
  pendingTransition?.transition.skipTransition();
  pendingTransition = null;
  if (!direction || motionPreference.matches) { paint(); return; }
  document.documentElement.style.setProperty('--slide', direction * 9 + 'px');
  if (document.startViewTransition) {
    const transition = document.startViewTransition(() => {
      if (serial !== transitionSerial) return;
      pendingTransition = null;
      paint();
    });
    pendingTransition = {key, transition};
    transition.ready.catch(() => {}); // A newer navigation can skip this snapshot.
  } else {
    paint();
    document.querySelector('.content').animate([
      {opacity:0, transform:'translateX(' + direction * 9 + 'px)'},
      {opacity:1, transform:'none'}
    ], easeOut);
  }
}

function fadeAway(element, transform, remove = true) {
  if (!element) return;
  if (motionPreference.matches) { if (remove) element.remove(); return; }
  element.inert = true;
  element.setAttribute('aria-hidden', 'true');
  const animation = element.animate([{opacity:1}, {opacity:0, transform}], easeOut);
  if (remove) animation.onfinish = () => element.remove();
}

// Withdraw a row from layout immediately and fade its visual copy over the gap.
function retiringCopy(element, bounds, transform) {
  if (!bounds.width || motionPreference.matches) return;
  const copy = element.cloneNode(true);
  for (const el of [copy, ...copy.querySelectorAll('[id]')]) el.removeAttribute('id');
  Object.assign(copy.style, {position:'fixed', margin:'0', inset:'auto', left:bounds.left+'px',
    top:bounds.top+'px', width:bounds.width+'px', height:bounds.height+'px', pointerEvents:'none', zIndex:'8'});
  document.body.append(copy);
  fadeAway(copy, transform);
}

function measureList(parent, nextKeys) {
  if (motionPreference.matches || !parent.isConnected || !parent.matches?.('.groups,.files,.goal-editor')) return;
  const children = [...parent.children];
  if (children.map(nodeKey).join('|') === nextKeys.join('|')) return;
  return new Map(children.map(el => [el, el.getBoundingClientRect()]));
}

function settleList(parent, before) {
  if (!before) return;
  const after = [...parent.children].map(el => [el, el.getBoundingClientRect()]);
  for (const [el, rect] of before) {
    if (!el.isConnected) retiringCopy(el, rect, 'translateY(-5px) scaleY(.95)');
  }
  for (const [el, rect] of after) {
    const old = before.get(el);
    const dy = old ? old.top - rect.top : 8;
    if (dy || !old) el.animate([{transform:'translateY('+dy+'px)',opacity:old?1:0}, {transform:'none',opacity:1}], easeOut);
  }
}

const counters = new WeakMap();
function countTo(el, value) {
  const old = Number(el.textContent);
  cancelAnimationFrame(counters.get(el));
  if (!el.textContent || !value || !Number.isFinite(old) || motionPreference.matches || old===Number(value)) {
    el.textContent=value; return;
  }
  const start=performance.now();
  function frame(now) {
    const t=Math.min(1,(now-start)/180);
    el.textContent=String(Math.round(old+(Number(value)-old)*t));
    if(t<1 && el.isConnected && !motionPreference.matches)counters.set(el,requestAnimationFrame(frame));
    else el.textContent=value;
  }
  counters.set(el,requestAnimationFrame(frame));
}
