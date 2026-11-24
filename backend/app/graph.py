"""Map stable public identifiers to version-local records in one transaction."""

from collections import defaultdict
from graphlib import CycleError, TopologicalSorter

from app.models import (
    SessionEdge,
    SessionTopic,
    TeachingSession,
    Topic,
    TopicDependency,
)
from app.schemas import (
    DependencyProposal,
    RoadmapProposal,
    SessionEdgeProposal,
    SessionProposal,
    TopicProposal,
)

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
    return [
        SessionEdgeProposal(
            from_session_id=a, to_session_id=b, edge_type="prerequisite"
        )
        for a, b in pairs
    ]


def validate_session_graph(proposal):
    topics = {t.id for t in proposal.topics}
    sessions = {s.id for s in proposal.sessions}
    used = set()
    for session in proposal.sessions:
        ids = session.topic_ids or [session.topic_id]
        if (
            session.topic_id not in ids
            or len(ids) != len(set(ids))
            or not set(ids) <= topics
        ):
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
        topic = Topic(
            roadmap_version_id=version.id,
            stable_id=item.id,
            sort_order=order,
            **item.model_dump(exclude={"id"}),
        )
        topics[item.id] = topic
        db.add(topic)
    db.flush()
    sessions = {}
    for order, item in enumerate(proposal.sessions):
        parent = topics[item.topic_id]
        session = TeachingSession(
            roadmap_version_id=version.id,
            stable_id=item.id,
            topic_id=parent.id,
            sort_order=order,
            learning_objectives=item.learning_objectives or parent.learning_objectives,
            **item.model_dump(
                exclude={"id", "topic_id", "topic_ids", "learning_objectives"}
            ),
        )
        sessions[item.id] = session
        db.add(session)
    db.flush()
    for item in proposal.sessions:
        for topic_id in item.topic_ids or [item.topic_id]:
            db.add(
                SessionTopic(
                    session_id=sessions[item.id].id, topic_id=topics[topic_id].id
                )
            )
    for edge in session_edges(proposal):
        db.add(
            SessionEdge(
                roadmap_version_id=version.id,
                from_session_id=sessions[edge.from_session_id].id,
                to_session_id=sessions[edge.to_session_id].id,
                edge_type=edge.edge_type,
                note=edge.note,
            )
        )
    for edge in proposal.dependencies:
        db.add(
            TopicDependency(
                roadmap_version_id=version.id,
                prerequisite_topic_id=topics[edge.prerequisite_topic_id].id,
                dependent_topic_id=topics[edge.dependent_topic_id].id,
            )
        )


def as_proposal(version):
    primary = {t.id: t.stable_id for t in version.topics}
    return RoadmapProposal(
        topics=[
            TopicProposal(
                id=t.stable_id,
                **t.model_dump(exclude={"id", "stable_id", "sort_order"}),
            )
            for t in version.topics
        ],
        sessions=[
            SessionProposal(
                id=s.stable_id,
                topic_id=primary[s.topic_id],
                **s.model_dump(exclude={"id", "stable_id", "topic_id", "sort_order"}),
            )
            for s in version.sessions
        ],
        dependencies=[
            DependencyProposal(**e.model_dump()) for e in version.dependencies
        ],
        session_edges=version.session_edges,
        warnings=version.warnings,
    )


def preserve_legacy_fields(proposal, previous):
    """An older editor only sends primary topics and topic-level dependencies."""
    old_sessions = {s.id: s for s in previous.sessions}
    valid_topics = {t.id for t in proposal.topics}
    for s in proposal.sessions:
        old = old_sessions.get(s.id)
        if old and "topic_ids" not in s.model_fields_set:
            s.topic_ids = list(
                dict.fromkeys(
                    [
                        s.topic_id,
                        *(
                            t
                            for t in old.topic_ids
                            if t in valid_topics and t != old.topic_id
                        ),
                    ]
                )
            )
        if (
            old
            and "supporting_chunk_ids" not in s.model_fields_set
            and s.supporting_material_ids == old.supporting_material_ids
        ):
            s.supporting_chunk_ids = list(old.supporting_chunk_ids)
    if proposal.session_edges is not None:
        return

    def inferred(plan):
        return {
            (e.from_session_id, e.to_session_id, e.edge_type): e
            for e in session_edges(plan.model_copy(update={"session_edges": None}))
        }

    before, after = inferred(previous), inferred(proposal)
    remaining = {s.id for s in proposal.sessions}
    preserved = {
        (e.from_session_id, e.to_session_id, e.edge_type): e
        for e in previous.session_edges
        if e.from_session_id in remaining and e.to_session_id in remaining
    }
    for removed in before.keys() - after.keys():
        preserved.pop(removed, None)
    for added in after.keys() - before.keys():
        preserved.setdefault(added, after[added])
    proposal.session_edges = list(preserved.values())
