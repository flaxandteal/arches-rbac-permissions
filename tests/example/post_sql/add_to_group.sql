DELETE FROM tiles WHERE nodegroupid='bb2f7e1c-7029-11ee-885f-0242ac140008' AND resourceinstanceid='d2368123-9628-49a2-b3dd-78ac6ee3e911';

INSERT INTO resource_x_resource (
  resourcexid,
  notes,
  relationshiptype,
  resourceinstanceidfrom,
  resourceinstanceidto,
  modified,
  created,
  inverserelationshiptype,
  tileid,
  nodeid,
  resourceinstancefrom_graphid,
  resourceinstanceto_graphid
) VALUES (
  'd090fa59-2cdf-4d6d-9ad6-21373300e459',
  '',
  NULL,
  'd2368123-9628-49a2-b3dd-78ac6ee3e911',
  'eba96b33-603b-4c4e-aaba-8e964a3b6d57',
  '2025-08-11 12:50:06.843786+00',
  '2025-08-11 12:50:06.843786+00',
  NULL,
  '4a0d2a52-d457-4616-a5ea-fa11453814a3',
  'bb2f7e1c-7029-11ee-885f-0242ac140008',
  '07883c9e-b25c-11e9-975a-a4d18cec433a',
  '07883c9e-b25c-11e9-975a-a4d18cec433a'
) ON CONFLICT DO NOTHING;

INSERT INTO resource_x_resource (
  resourcexid,
  notes,
  relationshiptype,
  resourceinstanceidfrom,
  resourceinstanceidto,
  modified,
  created,
  inverserelationshiptype,
  tileid,
  nodeid,
  resourceinstancefrom_graphid,
  resourceinstanceto_graphid
) VALUES (
  '3f52e2a2-4b52-47f6-a90f-d2fb09f5c716',
  '',
  NULL,
  'd2368123-9628-49a2-b3dd-78ac6ee3e911',
  '62833a14-fa6e-484c-bed2-06ca737bfaf9',
  '2025-08-11 12:50:06.843786+00',
  '2025-08-11 12:50:06.843786+00',
  NULL,
  '4a0d2a52-d457-4616-a5ea-fa11453814a3',
  'bb2f7e1c-7029-11ee-885f-0242ac140008',
  '07883c9e-b25c-11e9-975a-a4d18cec433a',
  '07883c9e-b25c-11e9-975a-a4d18cec433a'
) ON CONFLICT DO NOTHING;

INSERT INTO tiles (tileid, tiledata, nodegroupid, parenttileid, resourceinstanceid, sortorder, provisionaledits) VALUES (
  '4a0d2a52-d457-4616-a5ea-fa11453814a3', '{"bb2f7e1c-7029-11ee-885f-0242ac140008": [{"resourceId": "eba96b33-603b-4c4e-aaba-8e964a3b6d57", "ontologyProperty": "", "resourceXresourceId": "d090fa59-2cdf-4d6d-9ad6-21373300e459", "inverseOntologyProperty": ""}, {"resourceId": "62833a14-fa6e-484c-bed2-06ca737bfaf9", "ontologyProperty": "", "resourceXresourceId": "3f52e2a2-4b52-47f6-a90f-d2fb09f5c716", "inverseOntologyProperty": ""}]}', 'bb2f7e1c-7029-11ee-885f-0242ac140008', NULL, 'd2368123-9628-49a2-b3dd-78ac6ee3e911', 0, NULL
) ON CONFLICT DO NOTHING;
