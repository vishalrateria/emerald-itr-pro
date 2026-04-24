from dataclasses import dataclass


@dataclass
class TaxCalculation:
    slab_tax: float = 0.0
    rebate_87a: float = 0.0
    surcharge: float = 0.0
    cess: float = 0.0
    interest_234a: float = 0.0
    interest_234b: float = 0.0
    interest_234c: float = 0.0
    fee_234f: float = 0.0
    fee_234i: float = 0.0
    total_tax: float = 0.0
    tax_paid: float = 0.0
    net_payable: float = 0.0
