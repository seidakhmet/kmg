select *
from field_data t
where t.field_id = 1
  and t.start_datetime >= '2020-07-01 08:24:00'::timestamp
  and t.start_datetime <= '2020-07-01 23:59:59'::timestamp


select null                      as id,
       start_datetime::timestamp as start_datetime,
       0                         as value,
       '00:00:00'::time          as duration,
       1                         as field_id
from generate_series(
             '2020-07-01 08:24:00'::timestamp,
             '2020-07-01 23:59:59'::timestamp,
             '1 second'
         ) as gs(start_datetime)
where start_datetime not in (select start_datetime
                             from field_data t
                             where t.field_id = 1
                               and t.start_datetime >= to_timestamp('2020-07-01 08:24:00', 'YYYY-MM-DD hh24:mi:ss')::timestamp
                               and t.start_datetime <= '2020-07-01 23:59:59'::timestamp)



