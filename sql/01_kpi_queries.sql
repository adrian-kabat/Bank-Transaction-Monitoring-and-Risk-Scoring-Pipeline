-- ============================================================
-- Bank Transaction Monitoring and Risk Detection Pipeline
-- KPI queries for Kimball dimensional model
-- ============================================================


-- 1. Basic transaction KPIs
SELECT
    COUNT(*) AS transaction_count,
    ROUND(SUM(transaction_amount), 2) AS total_transaction_amount,
    ROUND(AVG(transaction_amount), 2) AS average_transaction_amount,
    ROUND(AVG(account_balance), 2) AS average_account_balance,
    ROUND(AVG(risk_score), 2) AS average_risk_score
FROM fact_transactions;


-- 2. Suspicious transaction KPIs
SELECT
    COUNT(*) AS transaction_count,
    SUM(suspicious_flag) AS suspicious_transaction_count,
    ROUND(
        100.0 * SUM(suspicious_flag) / COUNT(*),
        2
    ) AS suspicious_transaction_rate_pct,
    ROUND(
        SUM(CASE WHEN suspicious_flag = 1 THEN transaction_amount ELSE 0 END),
        2
    ) AS suspicious_transaction_amount
FROM fact_transactions;


-- 3. Transactions by risk level
SELECT
    risk_level,
    COUNT(*) AS transaction_count,
    ROUND(SUM(transaction_amount), 2) AS total_transaction_amount,
    ROUND(AVG(transaction_amount), 2) AS average_transaction_amount,
    ROUND(AVG(risk_score), 2) AS average_risk_score
FROM fact_transactions
GROUP BY risk_level
ORDER BY
    CASE risk_level
        WHEN 'High' THEN 1
        WHEN 'Medium' THEN 2
        WHEN 'Low' THEN 3
        ELSE 4
    END;


-- 4. Monthly transaction monitoring
SELECT
    d.year,
    d.month,
    d.month_name,
    COUNT(*) AS transaction_count,
    ROUND(SUM(f.transaction_amount), 2) AS total_transaction_amount,
    SUM(f.suspicious_flag) AS suspicious_transaction_count,
    ROUND(
        100.0 * SUM(f.suspicious_flag) / COUNT(*),
        2
    ) AS suspicious_transaction_rate_pct,
    ROUND(AVG(f.risk_score), 2) AS average_risk_score
FROM fact_transactions f
JOIN dim_date d
    ON f.date_key = d.date_key
GROUP BY
    d.year,
    d.month,
    d.month_name
ORDER BY
    d.year,
    d.month;


-- 5. Risk by transaction channel
SELECT
    c.channel,
    COUNT(*) AS transaction_count,
    ROUND(SUM(f.transaction_amount), 2) AS total_transaction_amount,
    SUM(f.suspicious_flag) AS suspicious_transaction_count,
    ROUND(
        100.0 * SUM(f.suspicious_flag) / COUNT(*),
        2
    ) AS suspicious_transaction_rate_pct,
    ROUND(AVG(f.risk_score), 2) AS average_risk_score
FROM fact_transactions f
JOIN dim_channel c
    ON f.channel_key = c.channel_key
GROUP BY c.channel
ORDER BY suspicious_transaction_rate_pct DESC;


-- 6. Risk by transaction type
SELECT
    tt.transaction_type,
    COUNT(*) AS transaction_count,
    ROUND(SUM(f.transaction_amount), 2) AS total_transaction_amount,
    SUM(f.suspicious_flag) AS suspicious_transaction_count,
    ROUND(
        100.0 * SUM(f.suspicious_flag) / COUNT(*),
        2
    ) AS suspicious_transaction_rate_pct,
    ROUND(AVG(f.risk_score), 2) AS average_risk_score
FROM fact_transactions f
JOIN dim_transaction_type tt
    ON f.transaction_type_key = tt.transaction_type_key
GROUP BY tt.transaction_type
ORDER BY suspicious_transaction_rate_pct DESC;


-- 7. Risk by location
SELECT
    l.location,
    COUNT(*) AS transaction_count,
    ROUND(SUM(f.transaction_amount), 2) AS total_transaction_amount,
    SUM(f.suspicious_flag) AS suspicious_transaction_count,
    ROUND(
        100.0 * SUM(f.suspicious_flag) / COUNT(*),
        2
    ) AS suspicious_transaction_rate_pct,
    ROUND(AVG(f.risk_score), 2) AS average_risk_score
FROM fact_transactions f
JOIN dim_location l
    ON f.location_key = l.location_key
GROUP BY l.location
ORDER BY suspicious_transaction_rate_pct DESC;


-- 8. Top 10 accounts by risk score
SELECT
    a.account_id,
    a.customer_age,
    a.customer_occupation,
    COUNT(*) AS transaction_count,
    ROUND(SUM(f.transaction_amount), 2) AS total_transaction_amount,
    SUM(f.suspicious_flag) AS suspicious_transaction_count,
    ROUND(AVG(f.risk_score), 2) AS average_risk_score,
    MAX(f.risk_score) AS max_risk_score
FROM fact_transactions f
JOIN dim_account a
    ON f.account_key = a.account_key
GROUP BY
    a.account_id,
    a.customer_age,
    a.customer_occupation
ORDER BY average_risk_score DESC
LIMIT 10;


-- 9. Top 10 suspicious transactions
SELECT
    f.transaction_id,
    f.transaction_date,
    a.account_id,
    m.merchant_id,
    c.channel,
    l.location,
    tt.transaction_type,
    ROUND(f.transaction_amount, 2) AS transaction_amount,
    f.login_attempts,
    f.transaction_duration,
    f.minutes_since_previous_transaction,
    f.account_balance,
    f.risk_score,
    f.risk_level,
    f.risk_reasons
FROM fact_transactions f
JOIN dim_account a
    ON f.account_key = a.account_key
JOIN dim_merchant m
    ON f.merchant_key = m.merchant_key
JOIN dim_channel c
    ON f.channel_key = c.channel_key
JOIN dim_location l
    ON f.location_key = l.location_key
JOIN dim_transaction_type tt
    ON f.transaction_type_key = tt.transaction_type_key
WHERE f.suspicious_flag = 1
ORDER BY
    f.risk_score DESC,
    f.transaction_amount DESC
LIMIT 10;


-- 10. Risk by hour of day
SELECT
    transaction_hour,
    COUNT(*) AS transaction_count,
    SUM(suspicious_flag) AS suspicious_transaction_count,
    ROUND(
        100.0 * SUM(suspicious_flag) / COUNT(*),
        2
    ) AS suspicious_transaction_rate_pct,
    ROUND(AVG(risk_score), 2) AS average_risk_score,
    ROUND(AVG(transaction_amount), 2) AS average_transaction_amount
FROM fact_transactions
GROUP BY transaction_hour
ORDER BY transaction_hour;