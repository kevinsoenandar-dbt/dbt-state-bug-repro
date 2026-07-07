with source as (
    select * from {{ source('raw', 'src_2') }}
)

select
    id,
    amount, 
    amount * 0.95 as ninety_fifth
from source
