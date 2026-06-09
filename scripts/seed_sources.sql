-- Seed script for dbt-state-bug-repro source tables.
-- Run in Snowflake against the ANALYTICS database.

create schema if not exists ANALYTICS.dbt_ksoenandar_raw;

use schema ANALYTICS.dbt_ksoenandar_raw;

-- src_1
create or replace table src_1 (
    id     number,
    name   varchar
);

insert into src_1 (id, name) values
    (1, 'alice'),
    (2, 'bob'),
    (3, 'carol');

-- src_2
create or replace table src_2 (
    id      number,
    amount  number(10, 2)
);

insert into src_2 (id, amount) values
    (1, 10.50),
    (2, 22.00),
    (3, 7.75);

-- src_3
create or replace table src_3 (
    id        number,
    category  varchar
);

insert into src_3 (id, category) values
    (1, 'gold'),
    (2, 'silver'),
    (3, 'bronze');

-- Scenario 1
-- insert into src_1 (id, name) values
--     (4, 'john');

-- Scenario 2
-- insert into src_1 (id, name) values
--     (5, 'cecillia');

-- insert into src_3 (id, category) values
--     (5, 'gold');

-- Scenario 3
-- insert into src_1 (id, name) values
--     (6, 'bryan');

-- insert into src_2 (id, amount) values
--     (6, 5.87);

-- insert into src_3 (id, category) values
--     (6, 'silver');
