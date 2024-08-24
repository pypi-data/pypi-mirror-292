from enum import Enum


class ProvinceBe(Enum):
    antwerpen = "Antwerpen (BE)"
    vlaams_brabant = "Vlaams-Brabant (BE)"
    brabant_wallon = "Brabant-Wallon (BE)"
    bruxelles = "Bruxelles (BE)"
    west_vlaanderen = "West-Vlaanderen (BE)"
    oost_vlaanderen = "Oost-Vlaanderen (BE)"
    hainaut = "Hainaut (BE)"
    limbourg = "Limbourg (BE)"
    liege = "Liege (BE)"
    luxembourg = "Luxembourg (BE)"
    namur = "Namur (BE)"
    not_found = "NOT DECLARED"

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
    wallonia = "Wallonie (BE)"
    flanders = "Vlaanderen (BE)"
    bruxelles = "Bruxelles (BE)"
    not_found = "NOT DECLARED"

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
