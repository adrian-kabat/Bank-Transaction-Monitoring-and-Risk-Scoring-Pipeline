# Kimball Dimensional Model

## Overview

The analytical layer follows the Kimball dimensional modeling approach. Transaction-level events are stored in the central fact table, while descriptive business context is separated into dimension tables.

The model supports transaction monitoring, risk analysis, KPI reporting, and Power BI dashboarding.

## Fact table

### `fact_transactions`

Grain: one row represents one bank transaction.

Main measures:

- `transaction_amount`
- `transaction_duration`
- `login_attempts`
- `account_balance`
- `minutes_since_previous_transaction`
- `transaction_count`
- `risk_score`
- `suspicious_flag`

Foreign keys:

- `account_key`
- `date_key`
- `merchant_key`
- `channel_key`
- `location_key`
- `device_key`
- `transaction_type_key`

## Dimension tables

### `dim_account`

Contains account-level and customer-related attributes:

- `account_key`
- `account_id`
- `customer_age`
- `customer_occupation`

### `dim_date`

Calendar dimension used for time-based analysis:

- `date_key`
- `date`
- `year`
- `quarter`
- `month`
- `month_name`
- `day`
- `day_of_week`
- `is_weekend`

### `dim_merchant`

Contains merchant identifiers.

### `dim_channel`

Contains transaction channels.

### `dim_location`

Contains transaction locations.

### `dim_device`

Contains device identifiers.

### `dim_transaction_type`

Contains transaction type categories.

## Model relationships

All relationships follow a one-to-many pattern from dimensions to the fact table:

```text
dim_account[account_key]              1 → * fact_transactions[account_key]
dim_date[date_key]                    1 → * fact_transactions[date_key]
dim_merchant[merchant_key]            1 → * fact_transactions[merchant_key]
dim_channel[channel_key]              1 → * fact_transactions[channel_key]
dim_location[location_key]            1 → * fact_transactions[location_key]
dim_device[device_key]                1 → * fact_transactions[device_key]
dim_transaction_type[transaction_type_key] 1 → * fact_transactions[transaction_type_key]