JOB_STATUS_EXAMPLE = """\
$ anyscale job status -n my-job
id: prodjob_jurfnb5tebn76rtm1jiev1des7
name: my-job
state: SUCCEEDED
runs:
- name: raysubmit_igxeSmbQAtUY8qNf
  state: FAILED
- name: raysubmit_bKuhY2s2SrS9TYSz
  state: SUCCEEDED
"""
