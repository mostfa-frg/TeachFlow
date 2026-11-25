const assistantThreads = new Map();
const assistantDrafts = new Map();

function mountAssistant(root,course,group,escape,reportFailure) {
  if (!course?.apiCourseId || !group) {
    root.textContent='Create a course and select a group to ask a question.';
    return;
  }
  const key=course.id+'/'+group.id;
  if (!assistantThreads.has(key)) assistantThreads.set(key,[]);
  const thread=assistantThreads.get(key);
  root.innerHTML=`<h1>Instructor Assistant</h1><p>${escape(course.name)} · ${escape(group.name)}</p>
    <div id="chat-log" role="log" aria-live="polite"></div><form><label>Question
    <textarea required maxlength="1500" name="question" placeholder="Which prerequisites does this group still need?"></textarea></label>
    <button class="btn primary">Ask</button></form><div role="status"></div>`;
  const log=root.querySelector('[role=log]'), form=root.querySelector('form'), status=root.querySelector('[role=status]');
  const questionField=form.elements.question;
  questionField.value=assistantDrafts.get(key) || '';
  questionField.oninput=()=>assistantDrafts.set(key,questionField.value);
  function paint() {
    log.innerHTML=thread.map(row=>`<article class="group"><h3>${escape(row.question)}</h3>
      <p style="white-space:pre-line">${escape(row.answer)}</p>
      ${row.references.length?`<ol>${row.references.map(ref=>`<li>${escape(ref.label)}<blockquote>${escape(ref.text)}</blockquote></li>`).join('')}</ol>`:'<p>No matching references.</p>'}</article>`).join('') ||
      '<p>Ask about approved sessions, materials, or group progress.</p>';
  }
  paint();
  form.onsubmit=async event=>{
    event.preventDefault();
    const question=form.elements.question.value.trim();
    if (!question) return;
    form.inert=true;
    status.textContent='Searching course evidence…';
    try {
      const response=await askInstructor(course.id,group.id,question);
      thread.push({question,...response}); paint();
      if (assistantDrafts.get(key)===questionField.value) assistantDrafts.delete(key);
      form.reset(); status.textContent='';
    } catch (error) {
      reportFailure('Could not answer your question',error);
      status.textContent=error.message+' Press Ask to retry.';
    } finally { form.inert=false; if(root.isConnected)questionField.focus(); }
  };
}
