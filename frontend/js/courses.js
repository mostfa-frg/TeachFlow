async function hydrateApiCourse(raw){
  const groups=(raw.groups||await groupApi.list(raw.id)).map(g=>({id:g.id,apiGroupId:g.id,courseId:raw.id,name:g.name,schedule:g.schedule_description||'',weekday:g.weekday,startTime:g.start_time,startDate:g.start_date,duration:g.session_duration_minutes||'',status:'active'}));
  const [materials,roadmap,history,approvals,groupFacts]=await Promise.all([
    courseApi.materials(raw.id),
    roadmapApi.approved(raw.id).catch(error=>{if(error.status===404)return null;throw error}),
    courseApi.history(raw.id), courseApi.approvals(raw.id),
    Promise.all(groups.map(async g=>{
      const [overview,progress]=await Promise.all([groupApi.overview(g.id),groupApi.savedProgress(g.id)]);
      return {id:g.id,overview,progress};
    }))
  ]);
  const overview=Object.fromEntries(groupFacts.map(g=>[g.id,g.overview]));
  const progressRows=groupFacts.map(g=>[g.id,g.progress]);
  const {topics,edges}=graphFromVersion(roadmap);
  const goalProgress={},progress={};
  const sessionByApiId=new Map(topics.map(t=>[t.sessionId,t]));
  for(const [groupId,rows] of progressRows){
    goalProgress[groupId]={};progress[groupId]=[];
    for(const row of rows){
      const session=sessionByApiId.get(row.session_id);
      if(!session)continue;
      const savedIndexes=[...(row.completed_objective_indexes||[])].sort((a,b)=>a-b);
      const indexes=row.state==='completed'?session.objectives.map((_,i)=>i):savedIndexes;
      goalProgress[groupId][session.id]=indexes;
      if(row.state==='completed'||(session.objectives.length>0&&indexes.length>=session.objectives.length))progress[groupId].push(session.id);
    }
  }
  return{history,approvals,pendingCount:approvals.length,overview,id:raw.id,apiCourseId:raw.id,name:raw.name,description:raw.description||'',learnerLevel:raw.learner_level||'',learningGoals:(raw.learning_goals||[]).join('\n'),status:roadmap?'active':'setup',groups,materials:materials.map(m=>({apiId:m.id,id:m.id,courseId:raw.id,filename:m.filename,name:m.filename,mimeType:m.media_type,sizeBytes:m.size_bytes,status:m.status,chunks:m.chunks||[],errorMessage:m.error_message})),topics,edges,progress,goalProgress,version:roadmap?.version_number||null,apiRoadmapId:roadmap?.id||null,attention:null,localOnly:false};
}

function coursePayload(draft) {
  return {
    name: draft.name,
    description: draft.description || null,
    learner_level: draft.learnerLevel?.toLowerCase().split('/')[0].trim() || null,
    learning_goals: draft.learningGoals.split(/[\n,]/).map(s => s.trim()).filter(Boolean)
  };
}

async function saveDraftGroups(draft) {
  const names = draft.groups.map(g => g.name.trim());
  if (new Set(names).size !== names.length) throw new Error('Give each group a distinct name before saving.');
  const current = await groupApi.list(draft.apiCourseId);
  for (const group of draft.groups) {
    const savedGroup = current.find(g => g.id === group.apiGroupId) || current.find(g => g.name === group.name);
    const saved = await groupApi.save(draft.apiCourseId, savedGroup?.id, {
      name: group.name, weekday: group.weekday || null, start_time: group.startTime || null,
      start_date: group.startDate || null, schedule_description: group.schedule || null,
      session_duration_minutes: group.duration ? Number(group.duration) : null
    });
    group.apiGroupId = saved.id;
  }
}
