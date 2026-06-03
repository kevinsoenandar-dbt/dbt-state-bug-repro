with source as (
    select * from {{ source('raw', 'src_3') }}
)

select
    id,
    category
from source
