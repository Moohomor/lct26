"""Схемы запросов и ответов API.

Общие правила оформления:
* поля ответа — snake_case, даты и числа в ISO/числовом виде;
* `Decimal` в ответах преобразуется в float на уровне сериализации, чтобы
  JSON не содержал строк;
* обязательные поля описаны явно, необязательные имеют осмысленные значения
  по умолчанию, а не `None` там, где ноль и «нет данных» — разные вещи.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated, Any, Literal

from email_validator import EmailNotValidError, validate_email
from pydantic import BaseModel, ConfigDict, Field, field_validator

Role = Literal["user", "admin"]


def _check_email(value: str) -> str:
    """Проверка адреса без обращения к DNS.

    Стандартный `EmailStr` ходит в DNS-резолвер, из-за чего регистрация
    зависит от доступности сети и может висеть на таймауте. Кроме того, он
    отвергает зарезервированные RFC 6761 домены (`.local`, `.example`),
    а именно на них держатся демонстрационные учётные записи платформы.
    """
    try:
        validate_email(
            value, check_deliverability=False, globally_deliverable=False
        )
    except EmailNotValidError as exc:
        # Библиотека объясняет проблему по-английски, а сообщение видят
        # пользователи. У синтаксических ошибок (EmailSyntaxError) поля
        # reason нет, поэтому переводим по самому тексту.
        text = str(exc)
        raise ValueError(EMAIL_ERRORS.get(text, "Почта указана неверно")) from exc
    return value


#: Тексты отказа email_validator → русский.
EMAIL_ERRORS = {
    "An email address must have an @-sign.": "В почте должен быть знак @",
    "The part after the @-sign contains invalid characters: '@'.":
        "В почте указан недопустимый символ",
    "The part after the @-sign contains invalid characters: '.'.":
        "Домен в почте указан неверно",
    "The part after the @-sign contains a dot but no domain.":
        "В почте не указан домен",
    "The part after the @-sign contains invalid characters.":
        "Домен в почте указан неверно",
    "There must be something after the @-sign.": "В почте не указан домен",
    "The local part of the email address contains invalid characters.":
        "Имя пользователя в почте указано неверно",
    "The local part of the email address is missing.":
        "В почте не указано имя пользователя",
    "The local part of the email address contains a forbidden character.":
        "Имя пользователя в почте указано неверно",
    "The email address is too long": "Почта слишком длинная",
    "The email address contains non-ASCII characters.":
        "В почте недопустимы символы, отличные от латинских",
}


#: Адрес электронной почты: синтаксис проверен, реальный домен — нет.
Email = Annotated[str, Field(max_length=254), field_validator]


class ApiModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ─────────────────────────────────────────────────────────────────────────────
# Аутентификация
# ─────────────────────────────────────────────────────────────────────────────


class LoginRequest(BaseModel):
    email: Email
    password: str = Field(min_length=1, max_length=256)

    _email = field_validator("email")(_check_email)


class RegisterRequest(BaseModel):
    email: Email
    password: str = Field(min_length=8, max_length=256, description="Не менее 8 символов")
    full_name: str | None = Field(default=None, max_length=255)
    organization: str | None = Field(default=None, max_length=255)

    _email = field_validator("email")(_check_email)

    @field_validator("password")
    @classmethod
    def _password_not_trivial(cls, value: str) -> str:
        if value.isalpha() or value.isdigit():
            raise ValueError("пароль не должен состоять только из букв или только цифр")
        return value


class RefreshRequest(BaseModel):
    refresh_token: str


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8, max_length=256)


class UserOut(ApiModel):
    id: int
    email: str
    full_name: str | None
    organization: str | None
    role: Role
    is_active: bool
    created_at: datetime
    last_login_at: datetime | None


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserOut


# ─────────────────────────────────────────────────────────────────────────────
# Справочники
# ─────────────────────────────────────────────────────────────────────────────


class ProcessOut(ApiModel):
    id: int
    code: str
    name: str
    description: str | None
    metric_code: str | None
    order_index: int


class ObjectTypeOut(ApiModel):
    id: int
    code: str
    name: str
    description: str | None
    icon: str | None
    order_index: int
    is_active: bool = True
    process_count: int = 0
    parameter_count: int = 0


class ObjectTypeDetail(ObjectTypeOut):
    processes: list[ProcessOut] = Field(default_factory=list)
    parameter_groups: list["ParameterGroupOut"] = Field(default_factory=list)


class ParameterOut(ApiModel):
    id: int
    object_type_id: int
    group_id: int | None
    code: str
    name: str
    unit: str | None
    value_type: str
    default: Any | None = None
    min_value: Any | None = None
    max_value: Any | None = None
    step: Any | None = None
    options: list[str] | None = None
    required: bool = False
    is_affecting_economics: bool = False
    is_demo: bool = True
    order_index: int = 0
    help_text: str | None = None
    note: str | None = None
    group_code: str | None = None
    group_name: str | None = None


class ParameterGroupOut(ApiModel):
    code: str
    name: str
    order_index: int = 0
    parameters: list[ParameterOut] = Field(default_factory=list)


class SolutionTypeOut(ApiModel):
    id: int
    code: str
    name: str
    is_mobile: bool
    requires_passage: bool
    passage_margin_m: float | None
    # В списке каталога тип решения отдаётся короткой проекцией без описания
    # и порядка — они нужны только в справочнике.
    description: str | None = None
    order_index: int = 0
    solution_count: int = 0


class VendorOut(ApiModel):
    id: int
    name: str
    country: str | None
    region: str | None
    website: str | None
    solution_count: int = 0


class DataSourceOut(ApiModel):
    id: uuid.UUID
    name: str
    url: str | None
    kind: str
    retrieved_at: str | None = None
    is_verified: bool
    note: str | None = None


class SolutionOut(ApiModel):
    id: uuid.UUID
    name: str
    vendor: VendorOut | None
    solution_type: SolutionTypeOut | None
    status: str
    trl: int | None
    purpose: str | None
    description: str | None
    industry: str | None
    region: str | None
    applicable_object_types: list[str] | None
    process_codes: list[str] | None
    restrictions: list[str] | None
    infrastructure_requirements: str | None
    airside_certified: bool | None
    medical_sanitation_ready: bool | None
    unit_price_rub: float | None
    price_source: str | None
    completeness: float
    is_verified: bool
    is_variant_of_id: uuid.UUID | None
    variant_label: str | None
    data_source: DataSourceOut | None
    specs_updated_at: str | None
    #: Снимок из «Каталога внедрения» ФЦ БАС. Не у всех позиций он есть.
    photo_url: str | None = None


class SolutionVariant(BaseModel):
    """Комплектация одной позиции каталога."""

    id: uuid.UUID
    name: str
    variant_label: str | None = None
    unit_price_rub: float | None = None


class SolutionDetail(SolutionOut):
    payload_kg: float | None
    own_weight_kg: float | None
    length_m: float | None
    width_m: float | None
    height_m: float | None
    min_passage_width_m: float | None
    lift_height_m: float | None
    max_speed_mps: float | None
    throughput_per_hour: float | None
    throughput_unit: str | None
    autonomy_hours: float | None
    charge_time_min: float | None
    positioning_accuracy_mm: float | None
    navigation_types: list[str] | None
    min_temp_c: float | None
    max_temp_c: float | None
    max_noise_dba: float | None
    max_floor_roughness_mm: float | None
    charge_power_kw: float | None
    battery_capacity_kwh: float | None
    battery_lifetime_years: float | None
    lifetime_years: float | None
    software_price_rub: float | None
    implementation_price_rub: float | None
    service_rate_pct: float | None
    purchase_model: str
    raw: dict | None = None
    # Комплектации той же позиции. Маршрут их собирает, но без этого поля
    # схема ответа отбрасывала бы их, и различий между комплектациями
    # не было бы видно нигде — ни в интерфейсе, ни у потребителя API.
    variants: list[SolutionVariant] = Field(default_factory=list)


class SolutionListResponse(BaseModel):
    items: list[SolutionOut]
    total: int
    limit: int
    offset: int
    facets: dict[str, Any] = Field(default_factory=dict)


# ─────────────────────────────────────────────────────────────────────────────
# Проекты
# ─────────────────────────────────────────────────────────────────────────────


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    object_type: str = Field(description="warehouse | airport | medical")
    organization: str | None = Field(default=None, max_length=255)
    description: str | None = None
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="Значения параметров по кодам"
    )
    process_codes: list[str] = Field(default_factory=list)

    @field_validator("process_codes")
    @classmethod
    def _limit_processes(cls, value: list[str]) -> list[str]:
        if len(value) > 10:
            raise ValueError("выбирайте не более 10 процессов за раз")
        return list(dict.fromkeys(value))


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    organization: str | None = Field(default=None, max_length=255)
    description: str | None = None
    parameters: dict[str, Any] | None = None
    process_codes: list[str] | None = None


class ProjectOut(ApiModel):
    id: uuid.UUID
    name: str
    object_type: str
    object_type_name: str | None = None
    status: str
    organization: str | None
    description: str | None
    parameters: dict
    process_codes: list
    user_id: int | None = None
    is_demo: bool = False
    created_at: datetime
    updated_at: datetime


class ProjectDetail(ProjectOut):
    completion: dict[str, Any] = Field(default_factory=dict)
    scenarios: list["ScenarioOut"] = Field(default_factory=list)
    latest_calculations: list["CalculationOut"] = Field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
# Сценарии и расчёты
# ─────────────────────────────────────────────────────────────────────────────


class ScenarioCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    kind: Literal["baseline", "purchase", "raas"] = "purchase"
    items: list[ScenarioItem] = Field(default_factory=list, description="Состав оборудования")
    assumptions: dict[str, Any] = Field(default_factory=dict, description="Переопределение допущений")
    horizon_years: int = Field(default=5, ge=1, le=30)
    description: str | None = None


class ScenarioItem(BaseModel):
    solution_id: uuid.UUID
    quantity: int = Field(default=1, ge=1, le=1000)


class ScenarioUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    items: list[ScenarioItem] | None = None
    assumptions: dict[str, Any] | None = None
    horizon_years: int | None = Field(default=None, ge=1, le=30)
    description: str | None = None


class ScenarioSolutionOut(ApiModel):
    id: int
    scenario_id: int
    solution_id: uuid.UUID
    solution_name: str
    solution_type: str | None = None
    quantity: float
    is_locked: bool = False
    note: str | None = None


class ScenarioOut(ApiModel):
    id: int
    project_id: uuid.UUID
    name: str
    kind: str
    description: str | None = None
    assumptions: dict[str, Any] = Field(default_factory=dict)
    horizon_years: int
    order_index: int = 0
    created_at: datetime
    last_calculated_at: datetime | None = None
    items: list[ScenarioSolutionOut] = Field(default_factory=list)
    latest_calculation_id: int | None = None


class CalculationOut(ApiModel):
    id: int
    scenario_id: int
    kind: str
    model_version: str
    catalog_version: str | None
    params_version: str | None
    payback_years: float | None
    annual_effect: float | None
    capex_total: float | None
    duration_ms: int | None
    computed_at: datetime
    user_id: int | None


class CalculationSummary(BaseModel):
    """Краткая выжимка расчёта — то, что показывается в списках и карточках."""

    meta: dict[str, Any]
    capex: dict[str, Any]
    opex: dict[str, Any]
    effect: dict[str, Any]
    payback: dict[str, Any]
    roi_pct: float
    residual_labor_annual: float
    warnings: list[str] = Field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
# Подбор
# ─────────────────────────────────────────────────────────────────────────────


class MatchRequest(BaseModel):
    object_type: str
    process_code: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    limit: int = Field(default=20, ge=1, le=200)
    include_rejected: bool = Field(default=True, description="Показывать и отклонённые решения")
    solution_type_codes: list[str] | None = None
    vendor_id: int | None = None
    min_score: float | None = Field(default=None, ge=0, le=100)


class MatchResponse(BaseModel):
    object_type: str
    process: str
    requirements: list[dict[str, Any]]
    peak_demand: float | None
    demand_unit: str | None
    results: list[dict[str, Any]]
    summary: dict[str, Any]
    weights: dict[str, int]


# ─────────────────────────────────────────────────────────────────────────────
# Решения в подборке проекта
# ─────────────────────────────────────────────────────────────────────────────


class ProjectSolutionOut(ApiModel):
    id: uuid.UUID
    project_id: uuid.UUID
    solution_id: uuid.UUID
    added_manually: bool
    warning: str | None
    match_score: float | None
    match_reasons: dict[str, Any] | None
    solution: SolutionOut | None = None


class ProjectSolutionCreate(BaseModel):
    solution_id: uuid.UUID
    quantity: float = Field(default=1, ge=0.01, le=1000)
    added_manually: bool = Field(
        default=True,
        description="Ручное добавление допускается даже для неподходящего решения (ТЗ 3.4.4)",
    )
    warning: str | None = None
    match_score: float | None = Field(default=None, ge=0, le=100)
    match_reasons: dict[str, Any] | None = None


# ─────────────────────────────────────────────────────────────────────────────
# Имитация (ТЗ 3.6)
# ─────────────────────────────────────────────────────────────────────────────


class SimulationRequest(BaseModel):
    speed_factor: float = Field(default=1.0, ge=0.25, le=8.0)
    seed: int | None = Field(
        default=None, description="Фиксирует раскладку: повторный запуск даёт тот же результат"
    )
    include_schedule: bool = Field(default=True, description="Расписание задач для анимации")


class SimulationOut(ApiModel):
    id: int
    scenario_id: int
    status: str
    progress: int
    speed_factor: float
    layout: dict[str, Any] | None
    kpi: dict[str, Any] | None
    schedule: dict[str, Any] | None
    error_message: str | None
    duration_ms: int | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None


# ─────────────────────────────────────────────────────────────────────────────
# Нормативы и администрирование (ТЗ 3.5.8)
# ─────────────────────────────────────────────────────────────────────────────


class NormativeOut(ApiModel):
    id: int
    code: str
    name: str
    value: Any
    unit: str | None
    category: str
    value_type: str
    min_value: Any | None
    max_value: Any | None
    is_editable: bool
    source: str | None
    note: str | None
    model_version: str
    version: int = 1


class NormativeUpdate(BaseModel):
    value: Any
    note: str | None = None


class ParameterCreate(BaseModel):
    code: str = Field(min_length=1, max_length=64, pattern=r"^[a-z0-9_.]+$")
    name: str = Field(min_length=1, max_length=255)
    group_code: str | None = None
    value_type: Literal["number", "integer", "percent", "text", "enum", "bool"] = "number"
    unit: str | None = None
    default: Any | None = None
    min_value: Any | None = None
    max_value: Any | None = None
    step: Any | None = None
    options: list[str] | None = None
    required: bool = False
    is_affecting_economics: bool = False
    help_text: str | None = None


class ParameterUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    group_id: int | None = None
    unit: str | None = None
    default: Any | None = None
    min_value: Any | None = None
    max_value: Any | None = None
    step: Any | None = None
    options: list[str] | None = None
    required: bool | None = None
    is_affecting_economics: bool | None = None
    help_text: str | None = None


class UserAdminOut(UserOut):
    project_count: int = 0
    calculation_count: int = 0


class UserUpdateAdmin(BaseModel):
    role: Role | None = None
    is_active: bool | None = None
    full_name: str | None = Field(default=None, max_length=255)
    organization: str | None = Field(default=None, max_length=255)


class SeedRunOut(BaseModel):
    ok: bool
    forced: bool
    duration_ms: int
    summary: dict[str, Any]
    warnings: list[str] = Field(default_factory=list)


class PageMeta(BaseModel):
    total: int
    limit: int
    offset: int


ObjectTypeDetail.model_rebuild()
ProjectDetail.model_rebuild()
