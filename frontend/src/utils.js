export function fmtVal(val) {
  if (val === null || val === undefined) return '';
  const parsed = parseFloat(val);
  if (!isNaN(parsed)) {
    return parsed.toFixed(2);
  }
  return String(val);
}

export function onPost(url, data) {
  if (!url) return;
  return fetch(`http://localhost:8000${url}`, {
    method: 'POST',
    headers: data ? { 'Content-Type': 'application/json' } : undefined,
    body: data ? JSON.stringify(data) : null,
  }).catch(e => console.error("API call failed", e));
}
