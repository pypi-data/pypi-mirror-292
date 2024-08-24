from enum import Enum


class ProvinceBe(Enum):
    antwerpen = "Antwerpen"
    vlaams_brabant = "Vlaams-Brabant"
    brabant_wallon = "Brabant-Wallon"
    bruxelles = "Bruxelles"
    west_vlaanderen = "West-Vlaanderen"
    oost_vlaanderen = "Oost-Vlaanderen"
    hainaut = "Hainaut"
    limbourg = "Limbourg"
    liege = "Liege"
    luxembourg = "Luxembourg"
    namur = "Namur"
    not_found = "NOT FOUND"

    @classmethod
    def get_all_values(cls):
        """Return all possible values for this enum as a list of enum."""
        return [v for v in cls.__dict__.values() if isinstance(v, cls)]

    @classmethod
    def get_all_values_str(cls) -> list[str]:
        """Return all possible values for this enum as a list of str."""
        return [v.value for v in cls.__dict__.values() if isinstance(v, cls)]


class ProvinceFr(Enum):
    @classmethod
    def __new__(cls, value):
        raise NotImplementedError("FR provinces not implemented yet")

    @classmethod
    def get_all_values(cls):
        """Return all possible values for this enum as a list of enum."""
        return [v for v in cls.__dict__.values() if isinstance(v, cls)]

    @classmethod
    def get_all_values_str(cls) -> list[str]:
        """Return all possible values for this enum as a list of str."""
        return [v.value for v in cls.__dict__.values() if isinstance(v, cls)]


class ProvinceNl(Enum):
    @classmethod
    def __new__(cls, value):
        raise NotImplementedError("NL provinces not implemented yet")

    @classmethod
    def get_all_values(cls):
        """Return all possible values for this enum as a list of enum."""
        return [v for v in cls.__dict__.values() if isinstance(v, cls)]

    @classmethod
    def get_all_values_str(cls) -> list[str]:
        """Return all possible values for this enum as a list of str."""
        return [v.value for v in cls.__dict__.values() if isinstance(v, cls)]


class RegionBe(Enum):
    wallonia = "Wallonia"
    flamande = "Flamande"
    bruxelles = "Bruxelles"
    not_found = "NOT FOUND"

    @classmethod
    def get_all_values(cls):
        """Return all possible values for this enum as a list of enum."""
        return [v for v in cls.__dict__.values() if isinstance(v, cls)]

    @classmethod
    def get_all_values_str(cls) -> list[str]:
        """Return all possible values for this enum as a list of str."""
        return [v.value for v in cls.__dict__.values() if isinstance(v, cls)]


class RegionFr(Enum):
    @classmethod
    def __new__(cls, value):
        raise NotImplementedError("FR regions not implemented yet")

    @classmethod
    def get_all_values(cls):
        """Return all possible values for this enum as a list of enum."""
        return [v for v in cls.__dict__.values() if isinstance(v, cls)]

    @classmethod
    def get_all_values_str(cls) -> list[str]:
        """Return all possible values for this enum as a list of str."""
        return [v.value for v in cls.__dict__.values() if isinstance(v, cls)]


class RegionNl(Enum):
    @classmethod
    def __new__(cls, value):
        raise NotImplementedError("NL regions not implemented yet")

    @classmethod
    def get_all_values(cls):
        """Return all possible values for this enum as a list of enum."""
        return [v for v in cls.__dict__.values() if isinstance(v, cls)]

    @classmethod
    def get_all_values_str(cls) -> list[str]:
        """Return all possible values for this enum as a list of str."""
        return [v.value for v in cls.__dict__.values() if isinstance(v, cls)]


class Country(Enum):
    belgium = "BE"
    france = "FR"
    netherlands = "NL"

    @classmethod
    def get_all_values(cls):
        """Return all possible values for this enum as a list of enum."""
        return [v for v in cls.__dict__.values() if isinstance(v, cls)]

    @classmethod
    def get_all_values_str(cls) -> list[str]:
        """Return all possible values for this enum as a list of str."""
        return [v.value for v in cls.__dict__.values() if isinstance(v, cls)]
