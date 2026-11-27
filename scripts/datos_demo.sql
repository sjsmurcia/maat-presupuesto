-- Datos ficticios para la demo y para probar la API: una empresa con su catálogo.
-- Se corre con psql después de `alembic upgrade head`; se puede correr dos veces sin duplicar.
-- El id de la empresa es fijo para que el grupo lo use en las rutas /api/empresas/{id}/…

\set empresa '11111111-1111-1111-1111-111111111111'

-- Con FORCE ROW LEVEL SECURITY también el dueño de las tablas necesita decir su empresa.
SELECT set_config('app.empresa_id', :'empresa', false);

INSERT INTO empresas (id, nombre) VALUES (:'empresa', 'Empresa Demo')
ON CONFLICT DO NOTHING;

INSERT INTO areas (id, empresa_id, codigo, nombre, area_superior_id) VALUES
  ('a0000000-0000-0000-0000-000000000001', :'empresa', 'ADM', 'Administración', NULL),
  ('a0000000-0000-0000-0000-000000000002', :'empresa', 'COM', 'Comercial', NULL),
  ('a0000000-0000-0000-0000-000000000003', :'empresa', 'TI', 'Tecnología', NULL),
  ('a0000000-0000-0000-0000-000000000004', :'empresa', 'CON', 'Contabilidad', 'a0000000-0000-0000-0000-000000000001'),
  ('a0000000-0000-0000-0000-000000000005', :'empresa', 'VTA', 'Ventas', 'a0000000-0000-0000-0000-000000000002')
ON CONFLICT DO NOTHING;

-- Primero las cuentas de grupo, porque las de detalle apuntan a ellas.
INSERT INTO cuentas (empresa_id, codigo, nombre, codigo_superior, naturaleza, es_detalle, activa) VALUES
  (:'empresa', '1',    'Activo',                 NULL, 'ACTIVO',  false, true),
  (:'empresa', '2',    'Pasivo',                 NULL, 'PASIVO',  false, true),
  (:'empresa', '4',    'Ingresos',               NULL, 'INGRESO', false, true),
  (:'empresa', '5',    'Gastos',                 NULL, 'GASTO',   false, true),
  (:'empresa', '6',    'Costos',                 NULL, 'COSTO',   false, true),
  (:'empresa', '1101', 'Bancos',                 '1',  'ACTIVO',  true,  true),
  (:'empresa', '2101', 'Proveedores',            '2',  'PASIVO',  true,  true),
  (:'empresa', '4101', 'Ventas de contado',      '4',  'INGRESO', true,  true),
  (:'empresa', '5101', 'Sueldos y salarios',     '5',  'GASTO',   true,  true),
  (:'empresa', '5201', 'Energía eléctrica',      '5',  'GASTO',   true,  true),
  (:'empresa', '5202', 'Vigilancia',             '5',  'GASTO',   true,  true),
  (:'empresa', '5203', 'Alquiler',               '5',  'GASTO',   true,  true),
  (:'empresa', '5204', 'Servicios en la nube',   '5',  'GASTO',   true,  true),
  (:'empresa', '5299', 'Papelería (en desuso)',  '5',  'GASTO',   true,  false),
  (:'empresa', '6101', 'Costo de ventas',        '6',  'COSTO',   true,  true)
ON CONFLICT DO NOTHING;

INSERT INTO centros (empresa_id, codigo, nombre, codigo_superior, tipo, area_id) VALUES
  (:'empresa', 'CC-1000', 'Administración',       NULL,      'ESPECIFICO',    'a0000000-0000-0000-0000-000000000001'),
  (:'empresa', 'CC-1100', 'Contabilidad',         'CC-1000', 'ESPECIFICO',    'a0000000-0000-0000-0000-000000000004'),
  (:'empresa', 'CC-1600', 'Tecnología',           NULL,      'ESPECIFICO',    'a0000000-0000-0000-0000-000000000003'),
  (:'empresa', 'CC-1910', 'Servicios Generales',  NULL,      'GENERICO',      'a0000000-0000-0000-0000-000000000001'),
  (:'empresa', 'CC-1920', 'Nube compartida',      NULL,      'GENERICO',      'a0000000-0000-0000-0000-000000000003'),
  (:'empresa', 'CC-1990', 'Gerencia general',     NULL,      'INSTITUCIONAL', 'a0000000-0000-0000-0000-000000000001'),
  (:'empresa', 'CB-0100', 'Ventas',               NULL,      'CEBE',          'a0000000-0000-0000-0000-000000000005')
ON CONFLICT DO NOTHING;
