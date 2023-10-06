## Get started
tbd

## TODO
- create anti-spam function for !tf_special and !tf_special_for_jannik
- create wrapper xoyondo class
    - reset poll
        - add new principle (consistency)
- efficiency issues:
    - xoyondo: get_votes_by_date -> for-loop calls get_date_for_index() for every index seperately
- errors:
    - too many request lead to HTTP-Error 429 (especially when using whole months) -> restrict parallel requests
    - Eingabe von 2023/40 usw. ergibt keinen Fehler -> direkte Eingabe von Wochen oder Monaten sollte nicht möglich sein