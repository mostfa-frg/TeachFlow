const teachingDays = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'];

function timeFields(group, escape) {
  return `<label>Weekday<select data-gfield="weekday">
    <option value="">Unscheduled</option>${teachingDays.map(day =>
      `<option ${day === group.weekday ? 'selected' : ''}>${day}</option>`).join('')}</select></label>
    <label>Start time<input type="time" data-gfield="startTime" value="${escape(group.startTime || '')}"></label>`;
}

function calendarImportPanel(state, escape, groupCard) {
  const preview = state.calendarPreview;
  return `<section class="panel"><label>Import schedule (ICS or CSV)
    <input type="file" id="calendar-file" accept=".ics,.csv"></label>
    <p class="small">Times use the clock shown in the file. Check the weekday and time before confirming.</p>
    <div role="status">${escape(state.calendarMessage || '')}</div>
    ${preview ? `<h3>Review imported groups</h3>
    ${preview.errors.map(e=>`<p role="alert">Row ${e.row}: ${escape(e.message)}</p>`).join('')}
    ${preview.groups.map(groupCard).join('')}
    <button class="btn" data-action="confirm-calendar" ${preview.groups.length ? '' : 'disabled'}>Confirm groups</button>
    <button class="btn" data-action="dismiss-calendar">Dismiss preview</button>` : ''}</section>`;
}

function calendarGroup(row) {
  return {id: crypto.randomUUID(), name: row.name, schedule: row.schedule_description || '',
    duration: row.session_duration_minutes, weekday: row.weekday, startTime: row.start_time, startDate: row.start_date};
}
