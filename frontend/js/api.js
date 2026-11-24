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

const reviewApi = {
  list: (group, session) => apiRequest(`/groups/${group}/sessions/${session}/reviews`),
  upload(group, session, file) {
    const body = new FormData();
    body.append('file',file);
    return apiRequest(`/groups/${group}/sessions/${session}/reviews`,{method:'POST',body});
  },
  read: id => apiRequest('/reviews/'+id),
  save: (id,findings) => jsonRequest('/reviews/'+id,'PUT',{findings}),
  approve: id => apiRequest('/reviews/'+id+'/approve',{method:'POST'}),
  draft: id => apiRequest('/reviews/'+id+'/package',{method:'POST'}),
  package: id => apiRequest('/packages/'+id),
  item: (id,key,text,approve) => jsonRequest(`/packages/${id}/items/${key}`,'PUT',{text,approve})
};
function jsonRequest(path, method, value) {
  return apiRequest(path,{method,headers:{'Content-Type':'application/json'},body:JSON.stringify(value)});
}
