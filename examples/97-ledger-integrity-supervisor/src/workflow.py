"""LangGraph supervisor for the period-close controls cycle.

TODO: run the close-cycle DAG by composing JV posting (44), bank
reconciliation (46), fixed-asset rollforward (50), and fraud/SAR screening
(55) as subagents, plus new segregation-of-duties (98) and audit-trail (99)
subagents; consolidate every exception into a ranked ControlsExceptionRegister;
route any exception above a materiality threshold through the approval-gate
pattern (id 90) before the close can be marked complete.
"""
