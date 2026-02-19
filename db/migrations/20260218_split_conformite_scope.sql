\set schema_name :DB_SCHEMA

-- Replace the legacy "conformite" scope with
-- "conformite_fiscale" and "conformite_sociale".
UPDATE :schema_name.group_service_provider_relations
SET scopes = BTRIM(
    REGEXP_REPLACE(
        REGEXP_REPLACE(
            scopes,
            '(^|[[:space:],])conformite($|[[:space:],])',
            '\1conformite_fiscale conformite_sociale\2',
            'g'
        ),
        '[[:space:]]+',
        ' ',
        'g'
    )
)
WHERE scopes ~ '(^|[[:space:],])conformite($|[[:space:],])';
