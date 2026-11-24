function graphFromVersion(version) {
  if (!version) return {topics: [], edges: []};
  const parents = new Map(version.topics.map(topic => [topic.id, topic]));
  const topics = version.sessions.map(session => {
    const parent = parents.get(session.topic_id);
    return {
      id: session.stable_id, sessionId: session.id, topicStableId: parent.stable_id,
      topicIds: session.topic_ids, topicTitle: parent.title, title: session.title,
      description: session.description, objectives: session.learning_objectives,
      minutes: session.duration_minutes, supportNote: parent.support_note,
      supportingMaterialIds: session.supporting_material_ids, sequenceIndex: session.sequence_index,
      chunkIds: session.supporting_chunk_ids || []
    };
  });
  const edges = version.session_edges.map(edge => [
    edge.from_session_id, edge.to_session_id, edge.edge_type, edge.note
  ]);
  return {topics, edges};
}

function proposalForSave(draft) {
  const original = draft.roadmapProposal;
  const sessions = draft.topics.map(item => ({
    id: item.id, topic_id: item.topicStableId, topic_ids: item.topicIds || [item.topicStableId],
    sequence_index: item.sequenceIndex || original.sessions.find(s => s.stable_id === item.id)?.sequence_index || 1,
    title: item.title, description: item.description || item.title,
    duration_minutes: Number(item.minutes), learning_objectives: item.objectives,
    supporting_material_ids: item.supportingMaterialIds || [], supporting_chunk_ids: item.chunkIds || []
  }));
  const used = new Set(sessions.flatMap(session => session.topic_ids));
  const topics = original.topics.filter(topic => used.has(topic.stable_id)).map(topic => ({
    id: topic.stable_id, title: topic.title, description: topic.description,
    learning_objectives: topic.learning_objectives, support_note: topic.support_note
  }));
  return {
    topics, sessions, warnings: original.warnings || [],
    dependencies: (original.dependencies || []).filter(e => used.has(e.prerequisite_topic_id) && used.has(e.dependent_topic_id)),
    session_edges: draft.edges.map(([from_session_id, to_session_id, edge_type = 'prerequisite', note = null]) =>
      ({from_session_id, to_session_id, edge_type, note}))
  };
}

function hardLink(edge) {
  return !edge[2] || ['prerequisite','depends_on'].includes(edge[2]);
}

function linkDescription(sessions,edge,endpoint) {
  const title=sessions.find(s=>s.id===edge[endpoint])?.title || edge[endpoint];
  return title+' ('+(edge[2]||'prerequisite')+')'+(edge[3]?' · '+edge[3]:'');
}

function citationPicker(materials, session, escape) {
  const choices=materials.flatMap(m=>(m.chunks||[]).map(chunk=>
    `<option value="${escape(chunk.id)}" data-material="${escape(m.apiId||m.id)}" ${(session.chunkIds||[]).includes(chunk.id)?'selected':''}>
    ${escape(m.name||m.filename)} · ${escape(chunk.locator)}</option>`));
  if (!choices.length) return '';
  return `<label>Supporting passages<select id="session-citations" multiple>${choices.join('')}</select></label>`;
}
