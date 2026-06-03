select
    m1.id,
    m1.name,
    m1.amount,
    s3.category
from {{ ref('mart_model_1') }} m1
left join {{ ref('stg_model_3') }} s3
    on m1.id = s3.id
