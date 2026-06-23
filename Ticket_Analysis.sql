USE DATABASE CUSTOMER_SUPPORT;
USE SCHEMA SUPPORT_ANALYZER;

--> Step 1: Sentiment Analysis using Cortex
CREATE OR REPLACE TABLE TICKET_SENTIMENT AS
SELECT
    TICKET_ID,
    CUSTOMER_NAME,
    CUSTOMER_EMAIL,
    PRODUCT_PURCHASED,
    TICKET_TYPE,
    TICKET_SUBJECT,
    TICKET_PRIORITY,
    TICKET_STATUS,
    TICKET_DESCRIPTION_CLEAN,
    SNOWFLAKE.CORTEX.SENTIMENT(TICKET_DESCRIPTION_CLEAN) AS SENTIMENT_SCORE,
    CASE
        WHEN SNOWFLAKE.CORTEX.SENTIMENT(TICKET_DESCRIPTION_CLEAN) >= 0.2 THEN 'Positive'
        when SNOWFLAKE.CORTEX.SENTIMENT(TICKET_DESCRIPTION_CLEAN) <= -0.2 THEN 'Negative'
        ELSE 'Neutral'
    END AS SENTIMENT_LABEL
FROM RAW_TICKETS_CLEANED
WHERE TICKET_DESCRIPTION_CLEAN IS NOT NULL;

--> Verify
SELECT * FROM TICKET_SENTIMENT LIMIT 5;

--> Quick distribution check
SELECT SENTIMENT_LABEL, COUNT(*) AS TOTAL
FROM TICKET_SENTIMENT
GROUP BY SENTIMENT_LABEL
ORDER BY TOTAL DESC;

--> Step 2: Classification using Cortex
CREATE OR REPLACE TABLE TICKET_CLASSIFICATION AS
SELECT
    TICKET_ID,
    CUSTOMER_NAME,
    PRODUCT_PURCHASED,
    TICKET_TYPE,
    TICKET_SUBJECT,
    TICKET_DESCRIPTION_CLEAN,
    SNOWFLAKE.CORTEX.CLASSIFY_TEXT( TICKET_DESCRIPTION_CLEAN,
    ARRAY_CONSTRUCT(
        'Billing',
            'Payment',
            'Login',
            'Account Management',
            'Technical Issue',
            'Product Defect',
            'Shipping',
            'Refund',
            'Subscription',
            'Feature Request',
            'Complaint',
            'General Inquiry',
            'Other'
    )
    )['label']::VARCHAR AS PREDICTED_CATEGORY
FROM RAW_TICKETS_CLEANED
WHERE TICKET_DESCRIPTION_CLEAN IS NOT NULL;

--> Verify
SELECT * FROM TICKET_CLASSIFICATION LIMIT 5;

--> Category distribution
SELECT PREDICTED_CATEGORY, COUNT(*) AS TOTAL
FROM TICKET_CLASSIFICATION
GROUP BY PREDICTED_CATEGORY
ORDER BY TOTAL DESC;

--> (Since COMPLETE() calls an LLM for every single row — 8,469 tickets is a lot and could be slow and costly)
--> Step 3: Create a table to store results first
CREATE OR REPLACE TABLE TICKET_COMPLETE_RAW (
    TICKET_ID            INT,
    CORTEX_ANALYSIS_RAW  VARIANT,
    PROCESSED_AT         TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

--> Then insert in batches of 500 at a time
--> Run each block separately, one after the other

-- Batch 1
INSERT INTO TICKET_COMPLETE_RAW (TICKET_ID, CORTEX_ANALYSIS_RAW)
SELECT
    TICKET_ID,
    PARSE_JSON(
        TRIM(
            REPLACE(
                REPLACE(
                    SNOWFLAKE.CORTEX.COMPLETE(
                        'mistral-large2',
                        CONCAT(
                            'You are an expert Customer Support Operations Analyst. ',
                            'Analyze the ticket and return ONLY a raw JSON object. ',
                            'No markdown, no backticks, no ```json, no explanation. Just the JSON. ',
                            'Use EXACTLY this schema with EXACTLY these allowed values: ',
                            '{"category":"","sentiment":"","urgency":"","business_impact_score":0,',
                            '"escalation_risk":"","churn_risk":"","resolution_complexity":"",',
                            '"recommended_team":"","summary":"","root_cause":"",',
                            '"customer_frustration_level":"","suggested_response":"","manager_alert_score":0} ',
                            'STRICT RULES - only use these exact values: ',
                            'category: Billing | Payment | Login | Account Management | Technical Issue | Product Defect | Shipping | Refund | Subscription | Feature Request | Complaint | General Inquiry | Other. ',
                            'sentiment: Positive | Neutral | Negative. ',
                            'urgency: Low | Medium | High | Critical. ',
                            'business_impact_score: integer 0-100. ',
                            'escalation_risk: Low | Medium | High. ',
                            'churn_risk: Low | Medium | High. ',
                            'resolution_complexity: Low | Medium | High. ',
                            'recommended_team: Billing Team | Payments Team | Customer Success | Tier 1 Support | Tier 2 Support | Engineering | Product Team | Security Team. ',
                            'customer_frustration_level: Low | Medium | High. ',
                            'manager_alert_score: integer 0-100. Above 80 = immediate manager attention needed. ',
                            'Product: ', PRODUCT_PURCHASED, '. ',
                            'Ticket Type: ', TICKET_TYPE, '. ',
                            'Subject: ', TICKET_SUBJECT, '. ',
                            'Priority: ', TICKET_PRIORITY, '. ',
                            'Status: ', TICKET_STATUS, '. ',
                            'Description: ', LEFT(TICKET_DESCRIPTION_CLEAN, 1500)
                        )
                    ),
                '```json', ''),
            '```', '')
        )
    ) AS CORTEX_ANALYSIS_RAW
FROM RAW_TICKETS_CLEANED
WHERE TICKET_ID BETWEEN 1 AND 500;

''' Then just change the BETWEEN range for each next batch:

Batch 2 → BETWEEN 501 AND 1000
Batch 3 → BETWEEN 1001 AND 1500
...and so on up to BETWEEN 8001 AND 8469

'''

--> Check progress after each batch
SELECT COUNT(*) AS PROCESSED FROM TICKET_COMPLETE_RAW;

--> Final Step: Join everything into one analytics table
CREATE OR REPLACE TABLE TICKET_ANALYSIS_FINAL AS
SELECT
    -- Raw ticket fields
    r.TICKET_ID,
    r.CUSTOMER_NAME,
    r.CUSTOMER_EMAIL,
    r.CUSTOMER_AGE,
    r.CUSTOMER_GENDER,
    r.PRODUCT_PURCHASED,
    r.DATE_OF_PURCHASE,
    r.TICKET_TYPE,
    r.TICKET_SUBJECT,
    r.TICKET_STATUS,
    r.TICKET_PRIORITY,
    r.TICKET_CHANNEL,
    r.TICKET_DESCRIPTION_CLEAN,

    -- From SENTIMENT table
    s.SENTIMENT_SCORE,
    s.SENTIMENT_LABEL,

    -- From CLASSIFICATION table
    c.PREDICTED_CATEGORY,

    -- From COMPLETE table — parsed JSON fields
    t.CORTEX_ANALYSIS_RAW:category::VARCHAR              AS AI_CATEGORY,
    t.CORTEX_ANALYSIS_RAW:sentiment::VARCHAR             AS AI_SENTIMENT,
    t.CORTEX_ANALYSIS_RAW:urgency::VARCHAR               AS AI_URGENCY,
    t.CORTEX_ANALYSIS_RAW:business_impact_score::INT     AS BUSINESS_IMPACT_SCORE,
    t.CORTEX_ANALYSIS_RAW:escalation_risk::VARCHAR       AS ESCALATION_RISK,
    t.CORTEX_ANALYSIS_RAW:churn_risk::VARCHAR            AS CHURN_RISK,
    t.CORTEX_ANALYSIS_RAW:resolution_complexity::VARCHAR AS RESOLUTION_COMPLEXITY,
    t.CORTEX_ANALYSIS_RAW:recommended_team::VARCHAR      AS RECOMMENDED_TEAM,
    t.CORTEX_ANALYSIS_RAW:summary::VARCHAR               AS AI_SUMMARY,
    t.CORTEX_ANALYSIS_RAW:root_cause::VARCHAR            AS ROOT_CAUSE,
    t.CORTEX_ANALYSIS_RAW:customer_frustration_level::VARCHAR AS CUSTOMER_FRUSTRATION_LEVEL,
    t.CORTEX_ANALYSIS_RAW:suggested_response::VARCHAR    AS SUGGESTED_RESPONSE,
    t.CORTEX_ANALYSIS_RAW:manager_alert_score::INT       AS MANAGER_ALERT_SCORE,

    -- Derived flag
    CASE
        WHEN t.CORTEX_ANALYSIS_RAW:manager_alert_score::INT > 80
        THEN TRUE ELSE FALSE
    END                                                  AS REQUIRES_MANAGER_ATTENTION,
    t.PROCESSED_AT                                       AS CORTEX_PROCESSED_AT

FROM RAW_TICKETS_CLEANED          r
LEFT JOIN TICKET_SENTIMENT        s ON r.TICKET_ID = s.TICKET_ID
LEFT JOIN TICKET_CLASSIFICATION   c ON r.TICKET_ID = c.TICKET_ID
LEFT JOIN TICKET_COMPLETE_RAW     t ON r.TICKET_ID = t.TICKET_ID
WHERE t.TICKET_ID IS NOT NULL;

--> Verify
SELECT * FROM TICKET_ANALYSIS_FINAL LIMIT 5;

--> Quick summary
SELECT
    COUNT(*)                                              AS TOTAL_TICKETS,
    SUM(CASE WHEN REQUIRES_MANAGER_ATTENTION THEN 1 END) AS NEEDS_MANAGER,
    SUM(CASE WHEN CHURN_RISK = 'High' THEN 1 END)        AS HIGH_CHURN_RISK,
    ROUND(AVG(BUSINESS_IMPACT_SCORE), 1)                 AS AVG_BUSINESS_IMPACT,
    ROUND(AVG(MANAGER_ALERT_SCORE), 1)                   AS AVG_ALERT_SCORE
FROM TICKET_ANALYSIS_FINAL;

