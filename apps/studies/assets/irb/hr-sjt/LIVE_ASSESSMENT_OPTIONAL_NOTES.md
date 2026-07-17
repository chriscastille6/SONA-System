# Live assessment follow-up — optional per-scenario decision notes

The IRB interactive packet in this repo already shows an optional notes box at the end of each situation.

**Label / copy to use in `hr-sjt-assessment`:**

> **Optional notes for your instructor**  
> Anything you’d like the instructor to know about how you’re thinking through this decision? Leave blank if you prefer.

**Implementation checklist (live app + API):**

1. Add an optional `<textarea>` after the tactics / Skip controls on each situation screen.
2. Do **not** mark the field required.
3. Persist notes with the situation response payload (e.g. `decision_notes` or `instructor_notes` on the incident/session response).
4. Skipping a situation should clear or omit notes for that situation.
5. Instructor export/view should surface notes per situation for MNGT 425 teaching review.

Until the live assessment is updated, reviewers can confirm the intended UX at:

https://bayoupal.nicholls.edu/hsirb/studies/hr-sjt/run/
