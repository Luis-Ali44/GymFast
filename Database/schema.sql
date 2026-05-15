-- =============================================
-- SCHEMA: TABLAS + ÍNDICES + SEED DATA
-- =============================================


-- 1. GIMNASIOS
CREATE TABLE gyms (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name        TEXT NOT NULL,
  slug        TEXT NOT NULL UNIQUE,
  address     TEXT,
  phone       TEXT,
  is_active   BOOLEAN NOT NULL DEFAULT true,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

INSERT INTO gyms (name, slug) VALUES
  ('Gym One',    'gym-one'),
  ('MOA',        'moa'),
  ('San Carlos', 'san-carlos'),
  ('Extrava',    'extrava');


-- 2. ROLES (catálogo)
CREATE TABLE roles (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name        TEXT NOT NULL UNIQUE,
  description TEXT
);

INSERT INTO roles (name, description) VALUES
  ('admin',      'Dueño o administrador general del gimnasio'),
  ('supervisor', 'Supervisor asignado a uno o más gimnasios'),
  ('user',       'Usuario/miembro regular');


-- 3. USUARIOS
CREATE TABLE users (
  id          UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  gym_id      UUID NOT NULL REFERENCES gyms(id) ON DELETE CASCADE,
  role_id     UUID NOT NULL REFERENCES roles(id),
  full_name   TEXT NOT NULL,
  email       TEXT NOT NULL,
  phone       TEXT,
  is_active   BOOLEAN NOT NULL DEFAULT true,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_users_gym_id  ON users(gym_id);
CREATE INDEX idx_users_role_id ON users(role_id);


-- 4. SUPERVISORES
CREATE TABLE supervisors (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  gym_id      UUID NOT NULL REFERENCES gyms(id) ON DELETE CASCADE,
  assigned_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(user_id, gym_id)
);

CREATE INDEX idx_supervisors_gym_id ON supervisors(gym_id);


-- TIPOS DE MÁQUINA (catálogo compartido)
CREATE TABLE machine_types (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  nombre      TEXT NOT NULL UNIQUE,
  categoria   TEXT,
  descripcion TEXT,
  creado_en   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- MÁQUINAS POR GYM (tabla pivote)
CREATE TABLE gym_machines (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  gym_id          UUID NOT NULL REFERENCES gyms(id) ON DELETE CASCADE,
  machine_type_id UUID NOT NULL REFERENCES machine_types(id) ON DELETE CASCADE,
  cantidad        INT NOT NULL DEFAULT 1,
  estado          TEXT NOT NULL DEFAULT 'active'CHECK (estado IN ('activo', 'descompuesto')),
  creado_en       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_gym_machines_gym_id          ON gym_machines(gym_id);
CREATE INDEX idx_gym_machines_machine_type_id ON gym_machines(machine_type_id);



-- 6. PLANES DE MEMBRESÍA (catálogo)
CREATE TABLE membership_plans (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name        TEXT NOT NULL UNIQUE,
  max_members INT NOT NULL,
  price       NUMERIC(10,2) NOT NULL,
  description TEXT,
  is_active   BOOLEAN NOT NULL DEFAULT true
);

INSERT INTO membership_plans (name, max_members, price, description) VALUES
  ('individual', 1, 300.00, 'Plan personal, 1 miembro'),
  ('duo',        2, 600.00, 'Plan para 2 personas'),
  ('trio',       3, 750.00, 'Plan para 3 personas'),
  ('squad',      4, 1000.00, 'Plan para 4 personas');


-- 7. MEMBRESÍAS
CREATE TABLE memberships (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  gym_id     UUID NOT NULL REFERENCES gyms(id) ON DELETE CASCADE,
  plan_id    UUID NOT NULL REFERENCES membership_plans(id),
  status     TEXT NOT NULL DEFAULT 'active'
             CHECK (status IN ('active', 'expired', 'cancelled', 'pending')),
  start_date DATE NOT NULL DEFAULT CURRENT_DATE,
  end_date   DATE NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_memberships_gym_id ON memberships(gym_id);
CREATE INDEX idx_memberships_status ON memberships(status);


-- 8. MIEMBROS DE MEMBRESÍA
CREATE TABLE membership_members (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  membership_id UUID NOT NULL REFERENCES memberships(id) ON DELETE CASCADE,
  user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  joined_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(membership_id, user_id)
);

CREATE INDEX idx_membership_members_user_id ON membership_members(user_id);