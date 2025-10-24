from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import json
from decimal import Decimal
from typing import List, Dict

currencies_json_path = str(Path.cwd() / "currencies.json")
print("This is the currencies JSON path:", currencies_json_path)


def load_currency_decimals(json_path: str) -> dict[str, int]:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return {item["code"].upper(): item.get("decimals", 2) for item in data}


CURRENCY_DECIMALS = load_currency_decimals(currencies_json_path)


def to_minor_units(amount: Decimal, currency: str) -> int:
    decimals = CURRENCY_DECIMALS.get(currency.upper(), 2)
    quantized = Decimal(str(amount)).quantize(
        Decimal(f"1.{ '0' * decimals }"), rounding=ROUND_HALF_UP
    )
    return int(quantized * (10**decimals))


def from_minor_units(amount_minor: Decimal, currency: str) -> Decimal:
    decimals = CURRENCY_DECIMALS.get(currency.upper(), 2)
    return Decimal(amount_minor) / (10**decimals)


def change_default_currency(
    user_currencies: List[Dict], new_default_code: str
) -> List[Dict]:

    new_default = next(
        (c for c in user_currencies if c["currency"]["code"] == new_default_code), None
    )
    if not new_default:
        raise ValueError(f"Currency {new_default_code} not found")

    # Get the exchange rate of the new default relative to the old base
    divisor = Decimal(new_default["exchange_rate"])

    if divisor == 0:
        raise ValueError("Invalid exchange rate: cannot divide by zero")

    updated = []
    for currency in user_currencies:
        # Recalculate each exchange_rate relative to new default
        new_rate = Decimal(currency["exchange_rate"]) / divisor

        # updated.append({"exchange_rate": new_rate})
        updated.append(
            {
                **currency,
                "exchange_rate": new_rate,
                "is_default": currency["currency"]["code"] == new_default_code,
            }
        )

    # print("Updated user currencies:", updated)
    return updated
