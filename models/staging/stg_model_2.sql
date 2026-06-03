select
    id,
    amount
from {{ source('raw', 'src_2') }}
