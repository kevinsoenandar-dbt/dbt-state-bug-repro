select
    s1.id,
    s1.name,
    s2.amount
from {{ ref('stg_model_1') }} s1
left join {{ ref('stg_model_2') }} s2
    on s1.id = s2.id
