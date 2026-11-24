async function apiRequest(path, options = {}) {
  const response = await fetch('/api/v1' + path, options);
  if (response.status === 204) return null;
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = data?.error?.details?.[0]?.msg;
    const error = new Error(detail || data?.error?.message || 'Request failed (' + response.status + ')');
    error.status = response.status;
    throw error;
  }
  return data;
}

function previewSchedule(file) {
  const data = new FormData();
  data.append('file', file);
  return apiRequest('/calendar/preview', {method:'POST', body:data});
}

function saveTarget(group, session, date) {
  return apiRequest('/groups/'+group+'/sessions/'+session+'/benchmark', {
    method:'PUT', headers:{'Content-Type':'application/json'}, body:JSON.stringify({target_date:date || null})
  });
}
