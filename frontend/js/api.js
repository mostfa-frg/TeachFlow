const apiEvents = new EventTarget();

async function apiRequest(path, options = {}) {
  let response;
  try {
    response = await fetch('/api/v1' + path, options);
  } catch (cause) {
    throw new Error('The browser could not reach TeachFlow. Check that the local server is running, then retry.', {cause});
  }
  if (response.headers.get('X-TeachFlow-Demo') === 'recorded') {
    apiEvents.dispatchEvent(new Event('recorded-demo'));
  }
  if (response.status === 204) return null;
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const problem = data?.error?.details?.[0];
    const field = problem?.loc?.filter(part => part !== 'body').join(' → ').replaceAll('_',' ');
    const detail = field ? field + ': ' + problem.msg : problem?.msg;
    const error = new Error(detail || data?.error?.message || (typeof data?.detail === 'string' && data.detail) || 'Request failed (' + response.status + ')');
    error.status = response.status;
    error.path = path;
    error.method = options.method || 'GET';
    throw error;
  }
  if (data === null) throw new Error('TeachFlow returned an unreadable response. Check the server terminal and retry.');
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

function explainFailure(action, error) {
  if (error.status === 404 && error.method === 'PUT' && /^\/courses\/[^/]+$/.test(error.path)) {
    return action + '. This draft points to a course missing from the current database. Open the original database or copy your fields into a new course in a private window.';
  }
  const guidance = {
    404: 'Refresh to see which records are still available.',
    409: 'Check the current record before trying again.',
    413: 'Choose a smaller file.',
    415: 'Choose a supported file format.',
    422: 'Correct the indicated value and try again.',
    429: 'Wait a moment before retrying.',
    500: 'Check the TeachFlow server terminal for details before retrying.',
    502: 'A service TeachFlow called failed. Check the server terminal for details and retry.',
    503: 'Check the local server and any provider configuration mentioned above, then retry.',
    504: 'The service timed out. Check its status and retry.'
  };
  const reason = error.name === 'NotAllowedError'
    ? 'Clipboard access was denied. Allow clipboard access or select and copy the text manually.'
    : error.message || 'TeachFlow did not provide a reason.';
  return [action + '.', /[.!?]$/.test(reason) ? reason : reason + '.', guidance[error.status]].filter(Boolean).join(' ');
}
