with source as (
    select * from {{ source('raw', 'src_1') }}
)

select
    id,
    name
from source
