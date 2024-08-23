CREATE TABLE covid_symptom__study_period AS
WITH documented_encounter AS (
    SELECT DISTINCT
        ce.period_start_day,
        ce.period_start_week,
        ce.period_start_month,
        ce.period_end_day,
        ce.age_at_visit,
        cdr.author_day,
        cdr.author_week,
        cdr.author_month,
        cdr.author_year,
        cp.gender,
        cp.race_display,
        cp.ethnicity_display,
        cp.subject_ref,
        ce.encounter_ref,
        ce.status,
        cdr.documentreference_ref,
        date_diff(
            'day', ce.period_start_day, date(cdr.author_day)
        ) AS diff_enc_note_days,
        coalesce(ce.class_code, 'None') AS enc_class_code,
        coalesce(ce.class_display, 'None') AS enc_class_display,
        coalesce(cdr.type_code, 'None') AS doc_type_code,
        coalesce(cdr.type_display, 'None') AS doc_type_display
    FROM
        core__patient AS cp,
        core__encounter AS ce,
        core__documentreference AS cdr
    WHERE
        (cp.subject_ref = ce.subject_ref)
        AND (ce.encounter_ref = cdr.encounter_ref)
        AND (cdr.author_day BETWEEN date('2016-06-01') AND current_date)
        AND (ce.period_start_day BETWEEN date('2016-06-01') AND current_date)
        AND (ce.period_end_day BETWEEN date('2016-06-01') AND current_date)
),

encounter_with_note AS (
    SELECT
        de.period_start_day,
        de.period_start_week,
        de.period_start_month,
        de.period_end_day,
        de.age_at_visit,
        de.author_day,
        de.author_week,
        de.author_month,
        de.author_year,
        de.gender,
        de.race_display,
        de.ethnicity_display,
        de.subject_ref,
        de.encounter_ref,
        de.status,
        de.documentreference_ref,
        de.diff_enc_note_days,
        de.enc_class_code,
        de.enc_class_display,
        de.doc_type_code,
        de.doc_type_display,
        coalesce(ed.code IS NOT NULL, FALSE) AS ed_note
    FROM documented_encounter AS de
    LEFT JOIN core__ed_note AS ed
        ON de.doc_type_code = ed.from_code
)

SELECT DISTINCT
    v.variant_era,
    e.period_start_day AS start_date,
    e.period_start_week AS start_week,
    e.period_start_month AS start_month,
    e.period_end_day AS end_date,
    e.age_at_visit,
    e.author_day AS author_date,
    e.author_week,
    e.author_month,
    e.author_year,
    e.gender,
    e.race_display,
    e.subject_ref,
    e.encounter_ref,
    e.documentreference_ref,
    e.diff_enc_note_days,
    e.enc_class_code,
    e.enc_class_display,
    e.doc_type_code,
    e.doc_type_display,
    e.ed_note,
    a.age_group,
    e.status
FROM encounter_with_note AS e,
    covid_symptom__define_period AS v,
    covid_symptom__define_age AS a
WHERE
    e.age_at_visit = a.age
    AND e.gender IN ('female', 'male')
    AND e.author_day BETWEEN v.variant_start AND v.variant_end
    AND e.period_start_day BETWEEN v.variant_start AND v.variant_end
    AND e.diff_enc_note_days BETWEEN -30 AND 30;

CREATE TABLE covid_symptom__meta_date AS
SELECT
    min(start_date) AS min_date,
    max(end_date) AS max_date
FROM covid_symptom__study_period;
