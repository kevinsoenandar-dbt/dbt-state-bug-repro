select
    id,
    category
from {{ source('raw', 'src_3') }}
