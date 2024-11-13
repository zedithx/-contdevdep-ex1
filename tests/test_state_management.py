"""
PUT /state (payload “INIT”, “PAUSED”, “RUNNING”, “SHUTDOWN”)
    PAUSED = the system does not response to requests
    RUNNING = the system responses to requests normally
    If the new state is equal to previous nothing happens.
    There are two special cases:
    INIT = everything (except log information for /run-log) is set to the initial state and
    login is needed get the system running again.
    SHUTDOWN = all containers are stopped
"""

"""
GET /state (as text/plain)
    get the value of state
"""

"""
GET /request
Similar function as REQUEST-button of the GUI (see instructions for nginx exercise),
but as a text/plain response to the requester.
"""

"""
GET /run-log (as text/plain)
Get information about state changes
Example response:
2023-11-01T06.35:01.380Z: INIT->RUNNING
2023-11-01T06:40:01.373Z: RUNNING->PAUSED
2023-11-01T06:40:01.373Z: PAUSET->RUNNING
"""

def test_add():
    assert 5 == 5
