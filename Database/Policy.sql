-- =============================================
-- POLÍTICAS RLS
-- Corre DESPUÉS de 20240101000001_schema.sql
-- =============================================


-- ---------------------------------------------
-- HABILITAR RLS EN TODAS LAS TABLAS
-- (roles y membership_plans son catálogos
--  públicos de solo lectura, sin RLS)
-- ---------------------------------------------
ALTER TABLE gyms               ENABLE ROW LEVEL SECURITY;
ALTER TABLE users              ENABLE ROW LEVEL SECURITY;
ALTER TABLE supervisors        ENABLE ROW LEVEL SECURITY;
ALTER TABLE memberships        ENABLE ROW LEVEL SECURITY;
ALTER TABLE membership_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE machine_types ENABLE ROW LEVEL SECURITY;
ALTER TABLE gym_machines  ENABLE ROW LEVEL SECURITY;


-- ---------------------------------------------
-- FUNCIONES HELPER
-- Leen el JWT del usuario autenticado.
-- SECURITY DEFINER: corren con permisos del
-- sistema, no del usuario, para evitar
-- recursión en las políticas.
-- ---------------------------------------------
CREATE OR REPLACE FUNCTION get_my_gym_id()
RETURNS UUID AS $$
  SELECT gym_id FROM users WHERE id = auth.uid();
$$ LANGUAGE sql SECURITY DEFINER STABLE;

CREATE OR REPLACE FUNCTION get_my_role()
RETURNS TEXT AS $$
  SELECT r.name
  FROM users u
  JOIN roles r ON r.id = u.role_id
  WHERE u.id = auth.uid();
$$ LANGUAGE sql SECURITY DEFINER STABLE;


-- ---------------------------------------------
-- POLÍTICAS: gyms
-- ---------------------------------------------
CREATE POLICY "admin: all gyms"
  ON gyms FOR ALL
  USING (get_my_role() = 'admin');

CREATE POLICY "supervisor/user: view own gym"
  ON gyms FOR SELECT
  USING (id = get_my_gym_id());


-- ---------------------------------------------
-- POLÍTICAS: users
-- ---------------------------------------------
CREATE POLICY "admin: all users"
  ON users FOR ALL
  USING (get_my_role() = 'admin');

CREATE POLICY "supervisor: view users in own gym"
  ON users FOR SELECT
  USING (
    get_my_role() = 'supervisor'
    AND gym_id = get_my_gym_id()
  );




-- ---------------------------------------------
-- POLÍTICAS: supervisors
-- ---------------------------------------------
CREATE POLICY "admin: all supervisors"
  ON supervisors FOR ALL
  USING (get_my_role() = 'admin');

CREATE POLICY "supervisor: view own record"
  ON supervisors FOR SELECT
  USING (user_id = auth.uid());


-- ---------------------------------------------
-- POLÍTICAS: machines
-- ---------------------------------------------
CREATE POLICY "admin: all machine_types"
  ON machine_types FOR ALL
  USING (get_my_role() = 'admin');

CREATE POLICY "admin: all gym_machines"
  ON gym_machines FOR ALL
  USING (get_my_role() = 'admin');

CREATE POLICY "supervisor: manage own gym machines"
  ON gym_machines FOR ALL
  USING (
    get_my_role() = 'supervisor'
    AND gym_id = get_my_gym_id()
  );

CREATE POLICY "todos: ver machine_types"
  ON machine_types FOR SELECT
  USING (true);

  

-- ---------------------------------------------
-- POLÍTICAS: memberships
-- ---------------------------------------------
CREATE POLICY "admin: all memberships"
  ON memberships FOR ALL
  USING (get_my_role() = 'admin');

CREATE POLICY "supervisor: manage own gym memberships"
  ON memberships FOR ALL
  USING (
    get_my_role() = 'supervisor'
    AND gym_id = get_my_gym_id()
  );



-- ---------------------------------------------
-- POLÍTICAS: membership_members
-- ---------------------------------------------
CREATE POLICY "admin: all membership_members"
  ON membership_members FOR ALL
  USING (get_my_role() = 'admin');

CREATE POLICY "supervisor: manage members in own gym"
  ON membership_members FOR ALL
  USING (
    get_my_role() = 'supervisor'
    AND EXISTS (
      SELECT 1 FROM memberships m
      WHERE m.id = membership_id
        AND m.gym_id = get_my_gym_id()
    )
  );
