# Data model

- **Course** owns instructor groups, material metadata, and immutable roadmap versions.
- **InstructorGroup** represents an offering of a course. It does not own a separate roadmap.
- **Material** stores relational metadata and processing outcome; original bytes and extracted-text sidecars live separately under server-generated filenames.
- **RoadmapVersion** tracks a per-course version number and `draft`, `approved`, or `superseded` review state.
- **Topic** is a learning unit within one roadmap version. Its stable ID is scoped to the roadmap version.
- **TeachingSession** belongs to one topic and roadmap version. A topic can have multiple sessions.
- **TopicDependency** is a directed prerequisite edge between topics within one version. Proposal validation rejects dangling, self-referential, duplicate, and cyclic edges.
- **GroupSessionProgress** records a session state for one group, unique per group/session pair. It is separate from course roadmap approval and other groups' progress.

Courses and their dependent records are deleted with cascade behavior. A draft proposal is stored separately and never overwrites an approved roadmap. Approval changes the new version to approved and the previous approved version to superseded.
