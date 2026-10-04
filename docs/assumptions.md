# Assumptions

### Assumption 1
"No of Changeover" is temporarily treated as duration in minutes.

### Assumption 2
"No of Coil Changeover" is temporarily treated as duration in minutes.

### Assumption 3
A Supervisor account may initially be shared, so the selected supervisor name is stored separately from login identity. A user on the shared account can technically select another supervisor's name. This is not individual identity verification.

### Assumption 4
Downtime data is manually entered. There is no automatic machine-status detection.

### Assumption 5
Excel is the primary reporting/export format. PDF is provided as a printable summary.

### Assumption 6
Soft delete is used for stoppage records so they disappear from history, dashboards, and reports without destroying the row immediately. A full audit log is not implemented.

### Assumption 7
Detail fields for Equipment Failure, Tool Problem, and Adjustment / Minor Stoppage are optional in this version.

### Assumption 8
When a supervisor user is not linked to a specific supervisor row (shared login), edit/delete authorization falls back to `created_by` matching the logged-in user.
