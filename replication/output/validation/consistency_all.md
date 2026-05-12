# Consistency checks — va_2022-23_vacancy

## Row count (expected 123-132)

| extract | rows | pass |
|---|---|---|
| A | 131 | PASS |
| B | 131 | PASS |
| C | 132 | PASS |
| CUR | 131 | PASS |

## Magnitude (values in plausible range)

### vacancy_rate_pct (expected 0.0-25.0)

| extract | n_values | min | max | n_outliers | pass |
|---|---|---|---|---|---|
| A | 120 | 0.10 | 20.80 | 0 | PASS |
| B | 120 | 0.10 | 20.80 | 0 | PASS |
| C | 131 | 0.00 | 20.80 | 0 | PASS |
| CUR | 120 | 0.10 | 20.80 | 0 | PASS |

---

# Consistency checks — va_2021-22_turnover

## Row count (expected 130-135)

| extract | rows | pass |
|---|---|---|
| A | 132 | PASS |
| B | 132 | PASS |
| C | 132 | PASS |
| CUR | 132 | PASS |

---

# Consistency checks — va_2023-24_vacancy

## Row count (expected 120-132)

| extract | rows | pass |
|---|---|---|
| A | 123 | PASS |
| B | 123 | PASS |
| C | 123 | PASS |
| CUR | 123 | PASS |

## Magnitude (values in plausible range)

### vacancy_rate_pct (expected 0.0-25.0)

| extract | n_values | min | max | n_outliers | pass |
|---|---|---|---|---|---|
| A | 123 | 0.00 | 21.50 | 0 | PASS |
| B | 123 | 0.00 | 21.50 | 0 | PASS |
| C | 123 | 0.00 | 21.50 | 0 | PASS |
| CUR | 123 | 0.00 | 21.50 | 0 | PASS |

## Stated totals (from PDF Total row)

| column | stated | A sum | B sum | C sum | CUR sum |
|---|---|---|---|---|---|
| total_unfilled_fte | 4104| 4104 | 4104 | 4104 | 4104 |
| total_fte_teacher_positions | 90466| 90465 | 90465 | 90465 | 90465 |

---

# Consistency checks — va_2021-22_vacancy

## Row count (expected 130-135)

| extract | rows | pass |
|---|---|---|
| A | 132 | PASS |
| B | 132 | PASS |
| C | 132 | PASS |
| CUR | 132 | PASS |

---

# Consistency checks — md_2020-21_to_2021-22_attrition

## Row count (expected 24-25)

| extract | rows | pass |
|---|---|---|
| A | 24 | PASS |
| B | 24 | PASS |
| C | 24 | PASS |
| CUR | 24 | PASS |

## Magnitude (values in plausible range)

### pct_teachers_2020-21_did_not_return_2021-22 (expected 0.0-30.0)

| extract | n_values | min | max | n_outliers | pass |
|---|---|---|---|---|---|
| A | 24 | 7.00 | 18.00 | 0 | PASS |
| B | 24 | 7.00 | 18.00 | 0 | PASS |
| C | 24 | 7.00 | 18.00 | 0 | PASS |
| CUR | 24 | 7.00 | 18.00 | 0 | PASS |

---

# Consistency checks — md_2022-23_to_2023-24_attrition

## Row count (expected 24-25)

| extract | rows | pass |
|---|---|---|
| A | 24 | PASS |
| B | 24 | PASS |
| C | 24 | PASS |
| CUR | 24 | PASS |

## Magnitude (values in plausible range)

### pct_teachers_2022-23_did_not_return_2023-24 (expected 0.0-30.0)

| extract | n_values | min | max | n_outliers | pass |
|---|---|---|---|---|---|
| A | 24 | 6.80 | 18.10 | 0 | PASS |
| B | 24 | 6.80 | 18.10 | 0 | PASS |
| C | 24 | 6.80 | 18.10 | 0 | PASS |
| CUR | 24 | 6.80 | 18.10 | 0 | PASS |

---
