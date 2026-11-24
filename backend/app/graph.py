"""Map stable public identifiers to version-local records in one transaction."""
from collections import defaultdict
from graphlib import CycleError, TopologicalSorter

from app.models import SessionEdge, SessionTopic, TeachingSession, Topic, TopicDependency
from app.schemas import DependencyProposal, RoadmapProposal, SessionEdgeProposal, SessionProposal, TopicProposal

HARD_EDGES = {"prerequisite", "depends_on"}


def session_edges(proposal):
    if proposal.session_edges is not None:
        return proposal.session_edges
    by_topic = defaultdict(list)
    for item in sorted(proposal.sessions, key=lambda s: s.sequence_index):
        by_topic[item.topic_id].append(item.id)
    pairs = [(a, b) for ids in by_topic.values() for a, b in zip(ids, ids[1:])]
    for edge in proposal.dependencies:
        first = by_topic[edge.prerequisite_topic_id]
        second = by_topic[edge.dependent_topic_id]
        if first and second:
            pairs.append((first[-1], second[0]))
    return [SessionEdgeProposal(from_session_id=a, to_session_id=b, edge_type="prerequisite") for a, b in pairs]


def validate_session_graph(proposal):
    topics = {t.id for t in proposal.topics}
    sessions = {s.id for s in proposal.sessions}
    used = set()
    for session in proposal.sessions:
        ids = session.topic_ids or [session.topic_id]
        if session.topic_id not in ids or len(ids) != len(set(ids)) or not set(ids) <= topics:
            raise ValueError("Check session topic membership and primary topic.")
        used.update(ids)
    if used != topics:
        raise ValueError("Every topic must contain at least one session.")
    seen = set()
    hard = TopologicalSorter()
    for edge in session_edges(proposal):
        a, b, kind = edge.from_session_id, edge.to_session_id, edge.edge_type
        if a == b or a not in sessions or b not in sessions:
            raise ValueError("Session links need two distinct existing endpoints.")
        if (a, b, kind) in seen:
            raise ValueError("Duplicate session link.")
        seen.add((a, b, kind))
        if kind in HARD_EDGES:
            hard.add(b, a)
    try:
        hard.prepare()
    except CycleError as exc:
        raise ValueError("Session prerequisites contain a cycle.") from exc


def write_graph(db, version, proposal):
    topics = {}
    for order, item in enumerate(proposal.topics):
        topic = Topic(roadmap_version_id=version.id, stable_id=item.id, sort_order=order,
                      **item.model_dump(exclude={"id"}))
        topics[item.id] = topic
        db.add(topic)
    db.flush()
    sessions = {}
    for order, item in enumerate(proposal.sessions):
        parent = topics[item.topic_id]
        session = TeachingSession(roadmap_version_id=version.id, stable_id=item.id,
                                  topic_id=parent.id, sort_order=order,
                                  learning_objectives=item.learning_objectives or parent.learning_objectives,
                                  **item.model_dump(exclude={"id", "topic_id", "topic_ids", "learning_objectives"}))
        sessions[item.id] = session
        db.add(session)
    db.flush()
    for item in proposal.sessions:
        for topic_id in item.topic_ids or [item.topic_id]:
            db.add(SessionTopic(session_id=sessions[item.id].id, topic_id=topics[topic_id].id))
    for edge in session_edges(proposal):
        db.add(SessionEdge(roadmap_version_id=version.id, from_session_id=sessions[edge.from_session_id].id,
                           to_session_id=sessions[edge.to_session_id].id, edge_type=edge.edge_type, note=edge.note))
    for edge in proposal.dependencies:
        db.add(TopicDependency(roadmap_version_id=version.id, prerequisite_topic_id=topics[edge.prerequisite_topic_id].id,
                               dependent_topic_id=topics[edge.dependent_topic_id].id))


def as_proposal(version):
    primary = {t.id: t.stable_id for t in version.topics}
    return RoadmapProposal(
        topics=[TopicProposal(id=t.stable_id, **t.model_dump(exclude={"id","stable_id","sort_order"})) for t in version.topics],
        sessions=[SessionProposal(id=s.stable_id, topic_id=primary[s.topic_id],
                                  **s.model_dump(exclude={"id","stable_id","topic_id","sort_order"})) for s in version.sessions],
        dependencies=[DependencyProposal(**e.model_dump()) for e in version.dependencies],
        session_edges=version.session_edges, warnings=version.warnings)
