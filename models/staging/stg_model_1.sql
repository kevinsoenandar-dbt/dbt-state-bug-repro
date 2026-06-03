select
    id,
    name
from {{ source('raw', 'src_1') }}
