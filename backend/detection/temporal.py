"""Temporal verification (Phase 3).

TODO: track regions across frames (IoU match on bbox). A region becomes an
incident only after it persists for config.PERSIST_SECONDS. Brief occlusion
(region hidden under a person mask) must NOT reset the timer.
For cleaning verification: once an incident's region has been absent for
config.CLEAR_SECONDS, move it to 'awaiting_verification'.
"""
