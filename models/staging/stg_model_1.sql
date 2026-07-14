with source as (
    select * from {{ source('raw', 'src_1') }}
)

select
    id,
    name,
    md5(id) as hash_key
from source
