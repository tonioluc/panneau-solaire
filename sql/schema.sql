CREATE TABLE analyses (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(150) NOT NULL,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE TABLE calculation_parameters (
    id INT IDENTITY(1,1) PRIMARY KEY,
    analysis_id INT NOT NULL UNIQUE,
    panel_efficiency DECIMAL(5,2) NOT NULL CONSTRAINT df_calculation_parameters_panel_efficiency DEFAULT 0.40,
    evening_panel_factor DECIMAL(5,2) NOT NULL CONSTRAINT df_calculation_parameters_evening_panel_factor DEFAULT 0.50,
    battery_margin DECIMAL(5,2) NOT NULL CONSTRAINT df_calculation_parameters_battery_margin DEFAULT 0.50,
    CONSTRAINT fk_calculation_parameters_analysis
        FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
);

CREATE TABLE appliance_usages (
    id INT IDENTITY(1,1) PRIMARY KEY,
    analysis_id INT NOT NULL,
    name NVARCHAR(150) NOT NULL,
    power_watt DECIMAL(18,2) NOT NULL,
    duration_hours DECIMAL(18,2) NOT NULL,
    tranche NVARCHAR(20) NOT NULL,
    CONSTRAINT fk_appliance_usages_analysis
        FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE,
    CONSTRAINT ck_appliance_usages_power CHECK (power_watt > 0),
    CONSTRAINT ck_appliance_usages_duration CHECK (duration_hours > 0),
    CONSTRAINT ck_appliance_usages_tranche CHECK (tranche IN ('morning', 'evening', 'night'))
);

CREATE TABLE calculation_results (
    id INT IDENTITY(1,1) PRIMARY KEY,
    analysis_id INT NOT NULL UNIQUE,
    total_energy_wh DECIMAL(18,2) NOT NULL,
    total_energy_kwh DECIMAL(18,2) NOT NULL,
    morning_energy_wh DECIMAL(18,2) NOT NULL,
    evening_energy_wh DECIMAL(18,2) NOT NULL,
    night_energy_wh DECIMAL(18,2) NOT NULL,
    theoretical_panel_watt DECIMAL(18,2) NOT NULL,
    practical_panel_watt DECIMAL(18,2) NOT NULL,
    theoretical_battery_kwh DECIMAL(18,2) NOT NULL,
    practical_battery_kwh DECIMAL(18,2) NOT NULL,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT fk_calculation_results_analysis
        FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
);
