# Assignment Module (Round Robin + Load Balancing)
# Responsibilities:
#   - select_manager(eligible_managers: list[Manager], office_rr_state: dict) -> Manager | None
#       1. Sort eligible_managers by current workload (ascending)
#       2. Take the two managers with lowest workload
#       3. Round-robin between those two using a per-office counter stored in office_rr_state
#       4. Returns selected Manager, or None if eligible_managers is empty
#   - office_rr_state: dict[office_id, int] — tracks which of the two candidates is next
#     This state is maintained in memory across all ticket assignments within a single session
#   - After selecting a manager: increment manager.workload by 1 in DB
