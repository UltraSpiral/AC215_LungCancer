const intFormat = new Intl.NumberFormat('en-GB');

/** 1234 → "1,234" */
export function formatInt(n: number): string {
  return intFormat.format(Math.round(n));
}

/** Optical-equivalent magnification: 40 → "40×", 2.5 → "2.5×", 0.62 → "0.6×". */
export function formatMagnification(m: number): string {
  if (!Number.isFinite(m) || m <= 0) return '—';
  const value = m >= 10 ? Math.round(m) : Math.round(m * 10) / 10;
  return `${value}×`;
}

/** 15654923 → "15.7 MB" */
export function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  const units = ['KB', 'MB', 'GB'];
  let v = bytes / 1024;
  let i = 0;
  while (v >= 1000 && i < units.length - 1) {
    v /= 1024;
    i++;
  }
  return `${v >= 100 ? Math.round(v) : v.toFixed(1)} ${units[i]}`;
}

const easternFormat = new Intl.DateTimeFormat('en-GB', {
  timeZone: 'America/New_York',
  day: 'numeric',
  month: 'short',
  hour: '2-digit',
  minute: '2-digit',
  hourCycle: 'h23',
});

/** US Eastern wall time, DST-aware: "19 Oct, 15:42 ET". */
export function formatEastern(ms: number): string {
  const p = Object.fromEntries(easternFormat.formatToParts(ms).map((x) => [x.type, x.value]));
  return `${p.day} ${p.month}, ${p.hour}:${p.minute} ET`;
}

/** 135_000 ms → "2:15" */
export function formatElapsed(ms: number): string {
  const total = Math.max(0, Math.floor(ms / 1000));
  const m = Math.floor(total / 60);
  const s = total % 60;
  return `${m}:${String(s).padStart(2, '0')}`;
}

/** Short job id for display: "job_7f3a9c21e0" → "7f3a9c21". */
export function shortJobId(id: string): string {
  return id.replace(/^job[_-]?/, '').slice(0, 8);
}
