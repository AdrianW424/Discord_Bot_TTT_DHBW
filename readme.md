## Get started
tbd

## TODO
- create wrapper xoyondo class
    - reset poll
        - add new principle (consistency)
- efficiency issues:
    - xoyondo: get_votes_by_date -> for-loop calls get_date_for_index() for every index seperately
- errors:
    - too many request lead to HTTP-Error 429 (especially when using whole months) -> restrict parallel requests