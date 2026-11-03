// Number formats used everywhere: Indian digit grouping, % with fixed dp, bp, rupees.
export function ind(x: number, dp = 0): string {
  const neg = x < 0; const v = Math.abs(x);
  const [w, f] = v.toFixed(dp).split('.');
  let out = w;
  if (w.length > 3) {
    const head = w.slice(0, -3).replace(/\B(?=(\d{2})+(?!\d))/g, ',');
    out = `${head},${w.slice(-3)}`;
  }
  out = f ? `${out}.${f}` : out;
  return neg ? `−${out}` : out;
}
export const pct = (x: number, dp = 1) => `${(x * 100).toFixed(dp)}%`;
export const bp = (x: number, dp = 0) => `${x >= 0 ? '+' : '−'}${Math.abs(x).toFixed(dp)} bp`;
export const rs = (x: number) => `₹${ind(x)}`;
export const cr = (x: number) => `₹${ind(x)} cr`;
export const signed = (x: number, dp = 1) => `${x >= 0 ? '+' : '−'}${Math.abs(x).toFixed(dp)}`;
