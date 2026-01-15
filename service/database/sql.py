from settings import org_id


##########################################
# карта донора
##########################################

donors_card_stmt = """
SELECT DISTINCT ON (d.id)
    d.id                                       AS "UnId",
    d.lastname                                 AS "LastName",
    d.firstname                                AS "FirstName",
    d.patrname                                 AS "MiddleName",
    d.birthday                                 AS "BirthDate",
    d.sex                                      AS "Gender",
    d.deleted                                  AS "IsDeleted",
    d."createDateTime"                         AS "CreateDate",
    d."modifyDateTime"                         AS "LastModifiedDate",
    d."createUserid"                           AS "CreateUserId",
    de.organisation                            AS "JobInfo",
    de.post                                    AS "JobPosition",
    substring(regexp_replace(dc.contact,
    '[^0-9]', '', 'g') from '([0-9]{10})$')    AS "PhoneMob",
    %s                                         AS "OrgId",
    true                                       AS "IsMessageAgree",
    CONCAT_WS(', ', da.locality, da.street,
              da.house, da.flat)               AS "PlaneAddress",
    dd.type                                    AS "DocType",
    dd.Number                                  AS "Number",
    dd.serial                                  AS "Serie",
    dd."startDate"                             AS "IssueDate",
    dd.origin                                  AS "IssuedBy"
FROM donor d
INNER JOIN donor_employment de ON d.id = de.donor_id AND NOT de.deleted
INNER JOIN donor_contact dc ON d.id = dc.donor_id AND NOT dc.deleted and dc.type = 1
INNER JOIN donor_address da ON d.id = da.donor_id and da.type = 1 AND NOT da.deleted
INNER JOIN donor_document dd ON d.id = dd.donor_id AND NOT dd.deleted
WHERE DATE(d."createDateTime") >= DATE(NOW() - INTERVAL '1 DAY') AND NOT d.deleted
ORDER BY 1 DESC;
""" % org_id

address_stmt = """
SELECT DISTINCT ON (d.id)
    d.id                                        AS "UnId",
    'false'                                     AS "RegAddressIsInactive",
    'false'                                     AS "FactAddressIsInactive",
    'false'                                     AS "TempAddressIsInactive",
    reg_adr.id                                  AS "RegId",
    reg_adr.house                               AS "RegHouse",
    reg_adr.flat                                AS "RegFlat",
    CONCAT_WS(', ', reg_adr.locality, reg_adr.street,
              reg_adr.house, reg_adr.flat)      AS "RegPlaneAddress",
    coalesce(reg_adr.locality_guid,
        '0c5b2444-70a0-4932-980c-b4dc0d3f02b5') AS "RegFiasRegionId",
    reg_adr.locality                            AS "RegRegion",
    coalesce(reg_adr.street_guid,
        '0c5b2444-70a0-4932-980c-b4dc0d3f02b5') AS "RegFiasStreetId",
    reg_adr.street                              AS "RegStreet",

    fact_adr.id                                 AS "FactId",
    fact_adr.house                              AS "FactHouse",
    fact_adr.flat                               AS "FactFlat",
    CONCAT_WS(', ', fact_adr.locality, fact_adr.street,
              fact_adr.house, fact_adr.flat)    AS "FactPlaneAddress",
    COALESCE(fact_adr.locality_guid,
        '0c5b2444-70a0-4932-980c-b4dc0d3f02b5') AS "FactFiasRegionId",
    fact_adr.locality                           AS "FactRegion",
    COALESCE(fact_adr.street_guid,
        '0c5b2444-70a0-4932-980c-b4dc0d3f02b5') AS "FactFiasStreetId",
    fact_adr.street                             AS "FactStreet"
FROM donor d
INNER JOIN donor_address reg_adr ON d.id = reg_adr.donor_id and reg_adr.type = 1
      AND NOT reg_adr.deleted
INNER JOIN donor_address fact_adr ON d.id = fact_adr.donor_id and fact_adr.type = 3
      AND NOT fact_adr.deleted
WHERE d.id = %s AND NOT d.deleted
ORDER BY 1 DESC;
"""

##########################################
# параметры крови
##########################################

blood_param_stmt = """
WITH donor_lab_history AS (SELECT v.donor_id       AS donor_id,
                                  db.type          AS blood_type_id,
                                  rhesus           AS rhesus_id,
                                  kell             AS kell_id,
                                  phenotype_id,
                                  db."setDateTime" AS setDateTime,
                                  antigen_cw_id,
                                  CASE
                                      WHEN l.donation_id IS NOT NULL THEN 1
                                      WHEN l.visit_id IS NOT NULL THEN 2
                                      END          AS priority
                           FROM donation d
                                    INNER JOIN visit v ON d.visit_id = v.id
                                    INNER JOIN donor don ON v.donor_id = don.id
                                    INNER JOIN donor_blood db ON don.id = db.donor_id
                                    INNER JOIN lab l ON db.lab_id = l.id
                           WHERE don.id = %s
                             AND d.deleted = false
                             AND d.deleted = false
                             AND v.deleted = false
                             AND db.deleted = false
                             AND l.deleted = false),
     actual_params AS (SELECT (SELECT blood_type_id
                               FROM donor_lab_history
                               WHERE blood_type_id IS NOT NULL
                               ORDER BY priority, setDateTime DESC
                               LIMIT 1) AS actual_blood_type_id,
                              (SELECT 
                                   case rhesus_id
                                   when 1 then 1
                                   when 2 then -1
                                   else rhesus_id end
                               FROM donor_lab_history
                               WHERE rhesus_id IS NOT NULL
                               ORDER BY priority, setDateTime DESC
                               LIMIT 1) AS actual_rhesus_id,
                              (SELECT 
                                   case kell_id
                                   when 1 then 1
                                   when 2 then 1
                                   when 3 then -1
                                   else kell_id end
                               FROM donor_lab_history
                               WHERE kell_id IS NOT NULL
                               ORDER BY priority, setDateTime DESC
                               LIMIT 1) AS actual_kell_id,
                              (SELECT phenotype_id
                               FROM donor_lab_history
                               WHERE phenotype_id IS NOT NULL
                               ORDER BY priority, setDateTime DESC
                               LIMIT 1) AS actual_phenotype_id,
                              (SELECT antigen_cw_id
                               FROM donor_lab_history
                               WHERE antigen_cw_id IS NOT NULL
                               ORDER BY priority, setDateTime DESC
                               LIMIT 1) AS actual_antigen_cw_id)
SELECT actual_blood_type_id AS "BloodGroup",
       actual_rhesus_id     AS "Rh",
       actual_kell_id       AS "Kell",
       actual_phenotype_id  AS "Phenotype",
       actual_antigen_cw_id AS "RbcAntibody"
FROM actual_params;
"""

##########################################
# врачебный осмотр
##########################################

docs_stmt = """
SELECT DISTINCT ON (V.id)
    v.id                                        AS "UnId",
    v."createUserid"                            AS "UserId",
    v."createDateTime"                          AS "CreateDate",
    %s                                          AS "OrgId",
    donor_id                                    AS "DonorId",
    v."setDate"                                 AS "ExamDate",
    v.deleted                                   AS "IsDeleted",
    'true'                                      AS "DeferralId"
FROM visit v
WHERE DATE(v."setDate") >= DATE(NOW() - INTERVAL '1 DAY')
AND NOT v.deleted;
""" % org_id

docs_tests_stmt = """
SELECT
    ipt.aist_id                                  AS "TestTypeId",
    ip.value                                     AS "Value",
    COALESCE(CASE d.sex
        WHEN 1 THEN REPLACE(ip.value, ',', '.')::float between
            coalesce(ipt.min_norm_male::float, 0) and coalesce(ipt.max_norm_male::float, 9999)
        WHEN 2 THEN REPLACE(ip.value, ',', '.')::float between
            coalesce(ipt.min_norm_female::float, 0) and coalesce(ipt.max_norm_female::float, 9999)
        END, false)                              AS "IsNorm"
FROM visit v
INNER JOIN inspect_prop ip ON v.id = ip.visit_id AND NOT ip.deleted
INNER JOIN inspect_prop_type ipt ON ip.type_id = ipt.id
   AND ipt.aist_id IS NOT NULL AND NOT ipt.deleted
INNER JOIN donor d ON v.donor_id = d.id AND NOT d.deleted
WHERE v.id = %s AND NOT v.deleted;
"""

##########################################
# предлаб
##########################################

prelab_stmt = """
SELECT
    lab.status_id                         AS "HematologyResultType",
    %s                                    AS "OrgId",
    v.donor_id                            AS "DonorId",
    lab.deleted                           AS "IsDeleted",
    lab."createDateTime"                  AS "CreateDate",
    lab."setDate"                         AS "ExamDate",
    lab.id                                AS "UnId",
    lab."createUserid"                    AS "UserId",
    lab."endDate"                         AS "ExamEndTime",
    'true'                                AS "DeferralId"
FROM lab
INNER JOIN visit v ON lab.visit_id = v.id AND NOT v.deleted
WHERE DATE(lab."setDate") >= DATE(NOW() - INTERVAL '1 DAY')
AND NOT lab.deleted;
""" % org_id

prelab_tests_stmt = """
SELECT
    lpt.aist_id         AS "TestTypeId",
    lp.value            AS "Value",
    COALESCE(CASE d.sex
        WHEN 1 THEN REPLACE(lp.value, ',', '.')::float between
            coalesce(lpt.min_norm_male::float, 0) and coalesce(lpt.max_norm_male::float, 9999)
        WHEN 2 THEN REPLACE(lp.value, ',', '.')::float between
            coalesce(lpt.min_norm_female::float, 0) and coalesce(lpt.max_norm_female::float, 9999)
    END, false)        AS "IsNorm"
FROM lab l
    INNER JOIN lab_prop lp on l.id = lp.lab_id
    INNER JOIN lab_prop_type lpt ON lp.type_id = lpt.id
        AND lpt.aist_id IS NOT NULL AND NOT lpt.deleted
    INNER JOIN visit v on l.visit_id = v.id
    INNER JOIN donor d on v.donor_id = d.id
WHERE l.id = %s AND NOT lp.deleted;
"""

##########################################
# донации
##########################################

donations_stmt = """
SELECT DISTINCT ON (lab.id)
       lab.status_id                                              AS "ResultStatus",
       dn.type_id                                                 AS "DonationTypeId",
       '100000012'                                                AS "DepartmentId",
       v.donor_id                                                 AS "UnId",
       %s                                                         AS "OrgId",
       lab."createDateTime"                                       AS "CreateDate",
       dn."setDate"                                               AS "DonationDate",
       left(concat(lab.prefix, lab.number, lab.suffix), 12)       AS "Barcode",
       lab.deleted                                                AS "IsDeleted",
       lab."createUserid"                                         AS "CreateUserId",
       p.volume                                                   AS "Volume",
       cast(anticoagulant.value AS INT)                           AS "ConsVol",
       cast(component_excluding_anticoag.value AS INT)            AS "ConsBloodVol",
       dn."modifyDateTime"                                        AS "LastModifiedDate",
       1                                                          AS "DataInputMethod",
       lab.donation_id                                            AS "DonationId"
FROM lab
         JOIN donation dn on lab.donation_id = dn.id
         JOIN visit v ON dn.visit_id = v.id
         JOIN action ON dn.id = action.donation_id
         JOIN action_package ap ON action.id = ap.action_id
         JOIN package p ON ap.package_id = p.id
         LEFT JOIN package_prop anticoagulant
                   ON p.id = anticoagulant.package_id
                       AND anticoagulant.type_id = (SELECT id
                                                    FROM package_prop_type
                                                    WHERE code = 'amount_of_anticoagulant'
                                                      AND p.tissue_type_id = tissue_type_id)
         LEFT JOIN package_prop component_excluding_anticoag
                   ON p.id = component_excluding_anticoag.package_id
                       AND component_excluding_anticoag.type_id =
                           (SELECT id
                            FROM package_prop_type
                            WHERE code = 'prepared_component_excluding_anticoag' AND p.tissue_type_id = tissue_type_id)
WHERE DATE(lab."setDate") >= DATE(NOW() - INTERVAL '1 DAY');
""" % org_id

donations_tests_stmt = """
SELECT
    lp."createDateTime"                     AS "CreateDate",
    lab."createUserid"                      AS "UserId",
    lpt.aist_id                             AS "TestTypeId",
    lp.value                                AS "Value"
FROM lab_prop lp
INNER JOIN lab_prop_type lpt on lp.type_id = lpt.id
      AND lpt.aist_id IS NOT NULL AND NOT lpt.deleted
INNER JOIN lab on lp.lab_id = lab.id AND NOT lab.deleted
WHERE lab_id = %s AND NOT lp.deleted;
"""

##########################################
# отводы
##########################################

exemption_stmt = """
SELECT
    db.id                                   AS "UnId",
    db.donor_id                             AS "DonorId",
    %s                                      AS "OrgId",
    db.reason                               AS "DefType",
    db."createDateTime"                     AS "CreateDate",
    db."createUserid"                       AS "CreateUserId",
    db."startDate"                          AS "StartDate",
    db."endDate"                            AS "StopDate",
    db."raiseDate"                          AS "RevokeDate",
    db."modifyDateTime"                     AS "LastModifiedDate",
    db."createUserid"                       AS "LastModifiedUserId"
FROM donor d
INNER JOIN donor_ban db ON d.id = db.donor_id AND NOT db.deleted
WHERE DATE(d."createDateTime") >= DATE(NOW() - INTERVAL '1 DAY')
AND NOT d.deleted;
""" % org_id
