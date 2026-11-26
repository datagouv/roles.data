\set schema_name :DB_SCHEMA

UPDATE :schema_name.group_service_provider_relations
SET scopes = REGEXP_REPLACE(
    scopes,
    '(^|[[:space:],])jour_naissance_dirigeants(?=$|[[:space:],])',
    '\1identite_restreinte_dirigeants',
    'g'
)
WHERE scopes ~ '(^|[[:space:],])jour_naissance_dirigeants(?=$|[[:space:],])';
