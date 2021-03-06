init_config:

instances:
  - url: http://localhost:9000/haproxy_stats
    username: {{ user }}
    password: {{ pass }}
    #
    # The (optional) status_check paramater will instruct the check to
    # send events on status changes in the backend. This is DEPRECATED in
    # favor creation a monitor on the service check status and will be
    # removed in a future version.
    # status_check: False
    #
    # The (optional) collect_aggregates_only parameter will instruct the
    # check to collect metrics only from the aggregate frontend/backend
    # status lines from the stats output instead of for each backend.
    # collect_aggregates_only: True
    #
    # The (optional) collect_status_metrics parameter will instruct the
    # check to collect metrics on status counts (e.g. haproxy.count_per_status)
    # collect_status_metrics: False
    #
    # The (optional) collect_status_metrics_by_host parameter will instruct
    # the check to collect status metrics per host instead of per service.
    # This only applies if collect_status_metrics is True.
    # collect_status_metrics_by_host: False
    #
    # The (optional) tag_service_check_by_host parameter will instruct the
    # check to tag the service check status by host on top of other tags.
    # The default case will only tag by backend and service.
    # tag_service_check_by_host: False
    #
    # optional, filter metrics by services
    # How it works: if a tag matches an exclude rule, it won't be included
    # unless it also matches an include rule.
    # e.g. include ONLY these two services
    # services_include:
    #   - "backend"
    #   - "test"
    # services_exclude:
    #   - ".*"
    #
    # OR include all EXCEPT this service
    # services_include: []
    # services_exclude:
    #   - "thisone"
