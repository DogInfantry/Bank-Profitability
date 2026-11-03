// One shared tooltip for every chart: position follows the pointer, content is plain HTML built from data.
let el: HTMLDivElement | null = null;
function node() {
  if (!el) { el = document.createElement('div'); el.className = 'tooltip'; el.setAttribute('role', 'status'); el.style.display = 'none'; document.body.appendChild(el); }
  return el;
}
export function showTip(ev: { clientX: number; clientY: number }, html: string) {
  const t = node(); t.innerHTML = html; t.style.display = 'block';
  const w = t.offsetWidth, h = t.offsetHeight;
  let x = ev.clientX + 14, y = ev.clientY + 14;
  if (x + w > window.innerWidth - 8) x = ev.clientX - w - 14;
  if (y + h > window.innerHeight - 8) y = ev.clientY - h - 14;
  t.style.left = `${Math.max(8, x)}px`; t.style.top = `${Math.max(8, y)}px`;
}
export function hideTip() { if (el) el.style.display = 'none'; }
