"""Data models"""

from dataclasses import dataclass

from .helpers import strtobool

@dataclass
class KatObligation:
    """Single obligation model."""

    unit_group: int
    status: int
    amount: int
    discount_amount: int
    discount_percentage: int
    description: str
    is_served: bool | None
    vehicle_number: str
    date_breach: str
    date_issued: str
    document_series: str
    document_number: str
    breach_of_order: str

    def __init__(self, unit_group: int, obligation: any):
        """Parse the data."""

        self.unit_group = unit_group
        self.status = obligation["status"]
        self.amount = obligation["amount"]
        self.discount_amount = obligation["discountAmount"]
        self.discount_percentage = int(obligation["additionalData"]["discount"])
        self.description = obligation["paymentReason"]

        if "isServed" in obligation["additionalData"]:
            self.is_served = strtobool(obligation["additionalData"]["isServed"])
        else:
            self.is_served = False

        self.vehicle_number = obligation["additionalData"]["vehicleNumber"]
        self.date_breach = obligation["additionalData"]["breachDate"]
        self.date_issued = obligation["additionalData"]["issueDate"]
        self.document_series = obligation["additionalData"]["documentSeries"]
        self.document_number = obligation["additionalData"]["documentNumber"]
        self.breach_of_order = obligation["additionalData"]["breachOfOrder"]

@dataclass
class KatObligationUnitGroup:
    """Obligation unit group entry."""

    unit_group: int
    error_no_data_found: bool
    error_reading_data: bool
    obligations: list[KatObligation]

    def __init__(self, unitgroup: any):
        """Parse the data."""

        self.unit_group = unitgroup["unitGroup"]
        self.error_no_data_found = unitgroup["errorNoDataFound"]
        self.error_reading_data = unitgroup["errorReadingData"]

        self.obligations = []
        for ob in unitgroup["obligations"]:
            self.obligations.append(KatObligation(self.unit_group, ob))


@dataclass
class KatObligationApiResponse:
    """Full KAT API Response"""

    obligations_data: list[KatObligationUnitGroup]

    def __init__(self, data: any):
        """Parse the data."""

        self.obligations_data = []
        for od in data["obligationsData"]:
            self.obligations_data.append(KatObligationUnitGroup(od))
