-- 장비 그룹 테이블 생성
CREATE TABLE IF NOT EXISTS equipment_groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 장비 속성 테이블 생성
CREATE TABLE IF NOT EXISTS equipment_attributes (
    id SERIAL PRIMARY KEY,
    group_id INTEGER NOT NULL REFERENCES equipment_groups(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    label VARCHAR(100) NOT NULL,
    field_type VARCHAR(50) NOT NULL,
    required BOOLEAN DEFAULT FALSE,
    options TEXT,
    "order" INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 장비 테이블 생성 (equipment_group 필드명 조정)
ALTER TABLE IF EXISTS equipment 
    ADD COLUMN IF NOT EXISTS equipment_group_id INTEGER REFERENCES equipment_groups(id),
    ADD COLUMN IF NOT EXISTS custom_attributes TEXT;

-- 기본 장비 그룹 데이터 추가
INSERT INTO equipment_groups (name, description) 
VALUES 
    ('PC/서버', 'PC, 서버 및 컴퓨팅 장비'),
    ('무전기', '송수신 무전기 장비'),
    ('환경장비', '환경 모니터링 및 측정 장비'),
    ('네트워크 장비', '라우터, 스위치 등 네트워크 인프라 장비'),
    ('기타장비', '기타 분류되지 않은 장비')
ON CONFLICT (name) DO NOTHING;

-- PC/서버 그룹에 속성 추가
INSERT INTO equipment_attributes (group_id, name, label, field_type, required, "order")
VALUES
    ((SELECT id FROM equipment_groups WHERE name = 'PC/서버'), 'cpu_model', 'CPU 모델', 'text', true, 10),
    ((SELECT id FROM equipment_groups WHERE name = 'PC/서버'), 'ram_size', 'RAM 용량 (GB)', 'number', true, 20),
    ((SELECT id FROM equipment_groups WHERE name = 'PC/서버'), 'storage_type', '저장장치 유형', 'select', true, 30),
    ((SELECT id FROM equipment_groups WHERE name = 'PC/서버'), 'storage_size', '저장장치 용량 (GB)', 'number', true, 40),
    ((SELECT id FROM equipment_groups WHERE name = 'PC/서버'), 'os_version', '운영체제 버전', 'text', false, 50);

-- 저장장치 유형 선택 옵션 추가
UPDATE equipment_attributes 
SET options = '["HDD", "SSD", "NVMe", "기타"]'
WHERE name = 'storage_type' AND group_id = (SELECT id FROM equipment_groups WHERE name = 'PC/서버');

-- 무전기 그룹에 속성 추가
INSERT INTO equipment_attributes (group_id, name, label, field_type, required, "order")
VALUES
    ((SELECT id FROM equipment_groups WHERE name = '무전기'), 'frequency_band', '주파수 대역', 'text', true, 10),
    ((SELECT id FROM equipment_groups WHERE name = '무전기'), 'output_power', '출력 (W)', 'number', false, 20),
    ((SELECT id FROM equipment_groups WHERE name = '무전기'), 'channel_count', '채널 수', 'number', false, 30),
    ((SELECT id FROM equipment_groups WHERE name = '무전기'), 'battery_type', '배터리 종류', 'select', false, 40),
    ((SELECT id FROM equipment_groups WHERE name = '무전기'), 'antenna_type', '안테나 유형', 'text', false, 50);

-- 배터리 종류 선택 옵션 추가
UPDATE equipment_attributes 
SET options = '["리튬이온", "니켈수소", "알카라인", "납축전지", "기타"]'
WHERE name = 'battery_type' AND group_id = (SELECT id FROM equipment_groups WHERE name = '무전기');

-- 네트워크 장비 그룹에 속성 추가
INSERT INTO equipment_attributes (group_id, name, label, field_type, required, "order")
VALUES
    ((SELECT id FROM equipment_groups WHERE name = '네트워크 장비'), 'port_count', '포트 수', 'number', false, 10),
    ((SELECT id FROM equipment_groups WHERE name = '네트워크 장비'), 'port_speed', '포트 속도', 'select', false, 20),
    ((SELECT id FROM equipment_groups WHERE name = '네트워크 장비'), 'managed', '관리형 여부', 'select', false, 30),
    ((SELECT id FROM equipment_groups WHERE name = '네트워크 장비'), 'poe_support', 'PoE 지원', 'select', false, 40),
    ((SELECT id FROM equipment_groups WHERE name = '네트워크 장비'), 'switching_capacity', '스위칭 용량', 'text', false, 50);

-- 네트워크 장비 선택 옵션 추가
UPDATE equipment_attributes 
SET options = '["10 Mbps", "100 Mbps", "1 Gbps", "10 Gbps", "25 Gbps", "40 Gbps", "100 Gbps"]'
WHERE name = 'port_speed' AND group_id = (SELECT id FROM equipment_groups WHERE name = '네트워크 장비');

UPDATE equipment_attributes 
SET options = '["관리형", "비관리형"]'
WHERE name = 'managed' AND group_id = (SELECT id FROM equipment_groups WHERE name = '네트워크 장비');

UPDATE equipment_attributes 
SET options = '["지원", "미지원"]'
WHERE name = 'poe_support' AND group_id = (SELECT id FROM equipment_groups WHERE name = '네트워크 장비');

-- 환경장비 그룹에 속성 추가
INSERT INTO equipment_attributes (group_id, name, label, field_type, required, "order")
VALUES
    ((SELECT id FROM equipment_groups WHERE name = '환경장비'), 'sensor_type', '센서 유형', 'select', true, 10),
    ((SELECT id FROM equipment_groups WHERE name = '환경장비'), 'measurement_range', '측정 범위', 'text', false, 20),
    ((SELECT id FROM equipment_groups WHERE name = '환경장비'), 'accuracy', '정확도', 'text', false, 30),
    ((SELECT id FROM equipment_groups WHERE name = '환경장비'), 'power_source', '전원 공급 방식', 'select', false, 40),
    ((SELECT id FROM equipment_groups WHERE name = '환경장비'), 'calibration_date', '보정 날짜', 'date', false, 50);

-- 환경장비 선택 옵션 추가
UPDATE equipment_attributes 
SET options = '["온도", "습도", "기압", "풍속", "풍향", "강수량", "복합센서", "기타"]'
WHERE name = 'sensor_type' AND group_id = (SELECT id FROM equipment_groups WHERE name = '환경장비');

UPDATE equipment_attributes 
SET options = '["배터리", "AC 전원", "태양광", "하이브리드"]'
WHERE name = 'power_source' AND group_id = (SELECT id FROM equipment_groups WHERE name = '환경장비');

-- 트리거 생성: 레코드 업데이트 시 updated_at 필드 자동 갱신
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- equipment_groups 테이블에 트리거 적용
DROP TRIGGER IF EXISTS update_equipment_groups_updated_at ON equipment_groups;
CREATE TRIGGER update_equipment_groups_updated_at
BEFORE UPDATE ON equipment_groups
FOR EACH ROW
EXECUTE FUNCTION update_modified_column();
