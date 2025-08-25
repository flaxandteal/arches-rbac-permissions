DELETE FROM tiles WHERE nodegroupid='2f94332c-9688-11ee-8782-0242ac140006' AND resourceinstanceid='006c35db-b52d-433f-bee7-9f28eeb37c58';
DELETE FROM inclusion_rules WHERE inclusionruleid='358c8112-81b9-11f0-8000-1cc10cec32b3';
INSERT INTO inclusion_rules (inclusionruleid, name, modulename, classname, definition, created, owner_id) VALUES (
    '358c8112-81b9-11f0-8000-1cc10cec32b3',
    'Books Authored by Ian McDonald',
    'search_rule',
    'SearchRule',
    '{"advanced-search": [{"op": "and", "4123e6fc-ac2c-4911-8d14-ef3b9cbabf76": {"op": "in_list_any", "val": ["44dd85c1-0132-44e3-b248-50f6b6d6f3d2"]}}]}',
    '2025-08-25 15:41:31.582488+00',
    1
)
