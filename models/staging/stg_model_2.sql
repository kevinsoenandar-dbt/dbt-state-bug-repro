with source as (
    select * from {{ source('raw', 'src_2') }}
)

select
    id,
    amount
from source
