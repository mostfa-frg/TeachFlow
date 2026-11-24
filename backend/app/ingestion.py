"""Local previews and source locations for instructor-supplied files."""
import csv
import io
import re
from datetime import date, datetime, time

from pydantic import ValidationError
from app.schemas import GroupCreate

CODE_TYPES = {".py", ".js", ".ts", ".java", ".json"}
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
DAY_CODES = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]


def document_chunks(text, extension, size=1600):
    if extension == ".pdf":
        for page, body in enumerate(text.split("\f"), 1):
            for start in range(0, len(body), size):
                part = body[start:start + size]
                if part.strip():
                    yield f"Page {page}, chars {start}–{start+len(part)}", part
    elif extension == ".md":
        heading, buffer, first = "Document", "", 1
        for line_number, line in enumerate(text.splitlines(keepends=True), 1):
            if line.startswith("#") or len(buffer) + len(line) > size:
                if buffer.strip():
                    yield f"{heading}, lines {first}–{line_number-1}", buffer
                buffer, first = "", line_number
            if line.startswith("#"):
                heading = line.strip("# \r\n")[:120] or "Document"
            while len(line) > size:
                yield f"{heading}, line {line_number}", line[:size]
                line = line[size:]
            buffer += line
        if buffer.strip():
            yield f"{heading}, lines {first}–{line_number}", buffer
    else:
        for start in range(0, len(text), size):
            part = text[start:start + size]
            if part.strip():
                yield f"Chars {start}–{start+len(part)}", part


def csv_rows(body):
    reader = csv.DictReader(io.StringIO(body.lstrip("\ufeff")))
    required = {"name", "weekday", "start_time", "duration_minutes", "start_date"}
    if not required <= set(reader.fieldnames or []):
        raise ValueError("CSV header must include " + ", ".join(sorted(required)))
    for line, row in enumerate(reader, 2):
        try:
            group = GroupCreate(name=row["name"], weekday=row["weekday"].strip().title(),
                                start_time=row["start_time"], start_date=row["start_date"],
                                session_duration_minutes=row["duration_minutes"])
            yield line, group, None
        except (ValidationError, ValueError, AttributeError) as exc:
            yield line, None, str(exc).split(" [type=")[0][:300]


def calendar_stamp(value):
    for fmt in ("%Y%m%dT%H%M%S", "%Y%m%dT%H%M"):
        try:
            return datetime.strptime(value.removesuffix("Z"), fmt)
        except ValueError:
            continue
    raise ValueError("Expected a timed DTSTART and DTEND.")


def parse_event(fields):
    name = fields.get("SUMMARY", "").replace("\\,", ",")
    start, end = (calendar_stamp(fields.get(k, "")) for k in ("DTSTART", "DTEND"))
    duration = int((end - start).total_seconds() / 60)
    rule = dict(item.split("=", 1) for item in fields["RRULE"].split(";")) if fields.get("RRULE") else {}
    if rule and (rule.get("FREQ") != "WEEKLY" or rule.get("INTERVAL","1") != "1" or set(rule)-{"FREQ","BYDAY","INTERVAL"}):
        raise ValueError("Only unbounded weekly recurrences with optional BYDAY are supported. Enter other schedules manually.")
    weekdays = rule.get("BYDAY", DAY_CODES[start.weekday()]).split(",")
    for day in weekdays:
        if day not in DAY_CODES:
            raise ValueError("Invalid weekly BYDAY.")
        from datetime import timedelta
        begins = start.date() + timedelta(days=(DAY_CODES.index(day) - start.weekday()) % 7)
        yield GroupCreate(name=name if len(weekdays)==1 else f"{name} · {day}", weekday=DAYS[DAY_CODES.index(day)],
                          start_time=start.time().strftime("%H:%M"), start_date=begins,
                          session_duration_minutes=duration,
                          schedule_description="Weekly" if rule else "One-time event")


def calendar_preview(body, extension):
    groups, errors = [], []
    if extension == ".csv":
        for line, group, error in csv_rows(body):
            if error:
                errors.append(dict(row=line, message=error))
            else:
                groups.append(group)
    elif extension == ".ics":
        fields = None
        for line, raw in enumerate(re.sub(r"\r?\n[ \t]", "", body).splitlines(), 1):
            if raw == "BEGIN:VEVENT":
                fields, first = {}, line
            elif raw == "END:VEVENT" and fields is not None:
                try:
                    groups.extend(list(parse_event(fields)))
                except ValueError as exc:
                    errors.append(dict(row=first, message=str(exc)[:300]))
                fields = None
            elif fields is not None and ":" in raw:
                key, value = raw.split(":", 1)
                fields[key.split(";")[0]] = value
        if fields is not None:
            errors.append(dict(row=first, message="Missing END:VEVENT."))
        if not groups and not errors:
            raise ValueError("No VEVENT records found.")
    else:
        raise ValueError("Choose an ICS or CSV file.")
    return dict(groups=groups, errors=errors)
