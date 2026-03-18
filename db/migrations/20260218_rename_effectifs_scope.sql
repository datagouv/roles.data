\set schema_name :DB_SCHEMA

-- Replace the legacy "effectifs_annuels" scope with
-- "effectifs".
UPDATE :schema_name.group_service_provider_relations
SET scopes = BTRIM(
    REGEXP_REPLACE(
        REGEXP_REPLACE(
            scopes,
            '(^|[[:space:],])effectifs_annuels($|[[:space:],])',
            '\1effectifs\2',
            'g'
        ),
        '[[:space:]]+',
        ' ',
        'g'
    )
)
WHERE scopes ~ '(^|[[:space:],])effectifs_annuels($|[[:space:],])';
