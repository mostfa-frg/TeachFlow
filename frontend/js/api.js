const apiEvents = new EventTarget();

async function apiRequest(path, options = {}) {
  const response = await fetch('/api/v1' + path, options);
  if (response.headers.get('X-TeachFlow-Demo') === 'recorded') {
    apiEvents.dispatchEvent(new Event('recorded-demo'));
  }
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

function askInstructor(course,group,question) {
  return jsonRequest('/courses/'+course+'/assistant','POST',{group_id:group,question});
}

const courseApi = {
  list: () => apiRequest('/courses'),
  save(id, course) {
    return id ? jsonRequest('/courses/'+id, 'PUT', course) : jsonRequest('/courses', 'POST', course);
  },
  remove: id => apiRequest('/courses/'+id, {method:'DELETE'}),
  materials: id => apiRequest(`/courses/${id}/materials`),
  upload(id, file) {
    const body = new FormData();
    body.append('file', file);
    return apiRequest(`/courses/${id}/materials`, {method:'POST', body});
  },
  deleteMaterial: (course, material) => apiRequest(`/courses/${course}/materials/${material}`, {method:'DELETE'}),
  approvals: id => apiRequest(`/courses/${id}/approvals`),
  history: id => apiRequest(`/courses/${id}/history`)
};

const groupApi = {
  list: course => apiRequest(`/courses/${course}/groups`),
  save(course, group, fields) {
    const path = `/courses/${course}/groups`;
    return group ? jsonRequest(path+'/'+group, 'PUT', fields) : jsonRequest(path, 'POST', fields);
  },
  remove: (course, group) => apiRequest(`/courses/${course}/groups/${group}`, {method:'DELETE'}),
  overview: id => apiRequest(`/groups/${id}/overview`),
  savedProgress: id => apiRequest(`/groups/${id}/progress`),
  progress: (group, session, value) => jsonRequest(`/groups/${group}/sessions/${session}/progress`, 'PUT', value)
};

const roadmapApi = {
  read: id => apiRequest('/roadmaps/'+id),
  approved: course => apiRequest(`/courses/${course}/roadmaps/approved`),
  copyApproved: course => apiRequest(`/courses/${course}/roadmaps/draft-from-approved`, {method:'POST'}),
  generate: (course, key) => apiRequest(`/courses/${course}/roadmaps/generate`, {method:'POST', headers:{'Idempotency-Key':key}}),
  edit: (id, proposal) => jsonRequest('/roadmaps/'+id, 'PUT', proposal),
  approve: id => apiRequest(`/roadmaps/${id}/approve`, {method:'POST'})
};
