from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, constr, field_validator, model_validator


class MsItem(BaseModel):
    ms_id: str
    barcodes: str
    nm_id: int
    name: str
    value: int


class IdsValuesSchema(BaseModel):
    ms_ids: List[constr(strip_whitespace=True, min_length=1)]
    values: List[int]


class StatusesSchema(BaseModel):
    wb_order_ids: List[int]
    statuses: List[constr(strip_whitespace=True, min_length=1)]


class WarehouseIdsSchema(BaseModel):
    ms_ids: List[constr(strip_whitespace=True, min_length=1)]
    values: List[int]
    warehouse_ids: List[int]


class CollectorItem(BaseModel):
    ms_id: str
    product_id: Optional[str] = None
    offer_id: Optional[str] = None
    price: float
    sku: Optional[str] = None


class WbItem(BaseModel):
    ms_id: str
    wb_barcodes: str | None = None
    nm_id: str | None = None
    price: float
    market_discount: int | None = None
    market_price: float | None = None
    code: Optional[str] = None

    @model_validator(mode='before')
    def price(cls, source_dict):
        if 'sale_prices' in source_dict:
            sale_prices = source_dict['sale_prices']
            if isinstance(sale_prices, dict) and '93250d9f-47b2-11ec-0a80-087f00119493' in sale_prices:
                source_dict['price'] = (sale_prices['93250d9f-47b2-11ec-0a80-087f00119493']['value'] * 2) // 100
        return source_dict


class OzonItem(BaseModel):

    ms_id: str
    ozon_product_id: Optional[str] = None
    code: Optional[str] = None
    ozon_after_discount: float
    old_price: float | None = None
    ozon_sku: Optional[str] = None
    market_price: float | None = None
    min_price: float | None = None

    @model_validator(mode='after')
    def calculate_old_price(self):
        self.old_price = self.ozon_after_discount * 2
        return self

    @model_validator(mode='before')
    def set_min_and_current_price(cls, source_dict):
        if 'sale_prices' in source_dict:
            sale_prices = source_dict['sale_prices']
            if isinstance(sale_prices, dict) and 'd69043a4-0423-11ec-0a80-094a0034609b' in sale_prices:
                source_dict['min_price'] = sale_prices['d69043a4-0423-11ec-0a80-094a0034609b']['value'] // 100
                source_dict['ozon_after_discount'] = sale_prices['e71c12e6-6d63-11eb-0a80-07710012356e']['value'] // 100

        return source_dict


class YandexItem(BaseModel):

    ms_id: str
    offer_id: str | None = None
    code: Optional[str] = None
    yandex_barcodes: str | None = None
    price: float
    discount_base: float
    market_price: float | None = None
    min_price: float | None = None
    
    @model_validator(mode='before')
    def calc_price_and_base(cls, source_dict):
        if 'sale_prices' in source_dict:
            sale_prices = source_dict['sale_prices']
            if isinstance(sale_prices, dict) and '08698679-67d3-11ec-0a80-0ba400906288' in sale_prices:
                source_dict['price'] = sale_prices['08698679-67d3-11ec-0a80-0ba400906288']['value'] // 100
                source_dict['discount_base'] = (source_dict['price'] * 2)

        return source_dict

    @model_validator(mode='before')
    def set_min_price(cls, source_dict):
        if 'sale_prices' in source_dict:
            sale_prices = source_dict['sale_prices']
            if isinstance(sale_prices, dict) and 'd690459a-0423-11ec-0a80-094a0034609c' in sale_prices:
                source_dict['min_price'] = sale_prices['d690459a-0423-11ec-0a80-094a0034609c']['value'] // 100

        return source_dict


class YandexAccount(BaseModel):

    name: str
    token: str
    business_id: str
    campaign_id: str


class WbAccount(BaseModel):

    name: str
    common_token: str
    statistic_token: str
    warehouse_id: str
    x_supplier_id: str


class OzonAccount(BaseModel):

    name: str
    api_key: str
    client_id: str
    warehouse_id: str


class BarcodesName(str, Enum):
    OZON = "code"
    YANDEX = "yandex_barcodes"
    WB = "nm_id"

