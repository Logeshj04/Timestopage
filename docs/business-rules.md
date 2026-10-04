# Business rules

1. **Production date** is an operational date selected by the user. It is not automatically changed at midnight.
2. **Shift timings (Asia/Kolkata)**
   - Shift A: 06:00–14:00
   - Shift B: 14:00–22:00
   - Shift C: 22:00–06:00 (crosses midnight)
3. **Shift C midnight rule.** Shift C belongs to the production date on which it starts. Example: production date 28 Aug, Shift C runs 28 Aug 22:00 to 29 Aug 06:00. Records remain dated 28 Aug.
4. **Current shift display.** 06:00–13:59 = A, 14:00–21:59 = B, 22:00–05:59 = C. After midnight until 05:59, current production date is the previous calendar date.
5. **Downtime** is stored in minutes. This version accepts whole minutes greater than zero. The database column is numeric so decimal minutes can be added later.
6. **Multiple stoppage records are allowed** for the same machine, shift, day, and reason. The system never combines them.
7. **Supervisor ownership.** The stoppage record stores `supervisor_id` independently from `created_by` (login user). A shared Supervisor login may currently select any name from the supervisor list. When a user is linked to a supervisor, they may only edit/delete records for that supervisor. Admins may edit all records.
8. **Machine codes** P-01 through P-29 are seeded. Machines are deactivated rather than hard-deleted so history remains intact.
9. **Changeover fields.** “No of Changeover” and “No of Coil Changeover” are treated as duration in minutes until the client confirms otherwise.
10. **No machine-running monitoring.** Absence of a stoppage record means “no stoppage recorded”, not that the machine was running.
