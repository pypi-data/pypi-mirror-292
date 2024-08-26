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


def get_all_regions(countries: list[Country] | list[str]) -> list[RegionBe | RegionFr | RegionNl]:
    """Get all regions for a list of countries. Countires can be a list of Country enums or a list of str."""
    all_regions = []
    if not countries:
        return all_regions

    if isinstance(countries[0], str):
        countries = [Country(country) for country in countries]

    if Country.belgium in countries:
        all_regions.extend(RegionBe.get_all_values())
    if Country.france in countries:
        all_regions.extend(RegionFr.get_all_values())
    if Country.netherlands in countries:
        all_regions.extend(RegionNl.get_all_values())
    return all_regions


def get_all_regions_str(countries: list[Country] | list[str]) -> list[str]:
    """Get all regions for a list of countries. Countries can be a list of Country enums or a list of str."""
    all_regions = []
    if not countries:
        return all_regions

    if isinstance(countries[0], str):
        countries = [Country(country) for country in countries]

    for country in countries:
        if country == Country.belgium:
            all_regions.extend(RegionBe.get_all_values_str())
        elif country == Country.france:
            all_regions.extend(RegionFr.get_all_values_str())
        elif country == Country.netherlands:
            all_regions.extend(RegionNl.get_all_values_str())
        else:
            raise ValueError(f"Unknown country: `{country}`")

    return all_regions


def get_all_provinces(countries: list[Country] | list[str]) -> list[ProvinceBe | ProvinceFr | ProvinceNl]:
    """Get all provinces for a list of countries. Countries can be a list of Country enums or a list of str."""
    all_provinces = []
    if not countries:
        return all_provinces

    if isinstance(countries[0], str):
        countries = [Country(country) for country in countries]

    if Country.belgium in countries:
        all_provinces.extend(ProvinceBe.get_all_values())
    if Country.france in countries:
        all_provinces.extend(ProvinceFr.get_all_values())
    if Country.netherlands in countries:
        all_provinces.extend(ProvinceNl.get_all_values())

    return all_provinces


def get_all_provinces_str(countries: list[Country] | list[str]) -> list[str]:
    """Get all provinces for a list of countries. Countries can be a list of Country enums or a list of str."""
    all_provinces = []
    if not countries:
        return all_provinces

    if isinstance(countries[0], str):
        countries = [Country(country) for country in countries]

    for country in countries:
        if country == Country.belgium:
            all_provinces.extend(ProvinceBe.get_all_values_str())
        elif country == Country.france:
            all_provinces.extend(ProvinceFr.get_all_values_str())
        elif country == Country.netherlands:
            all_provinces.extend(ProvinceNl.get_all_values_str())
        else:
            raise ValueError(f"Unknown country: `{country}`")

    return all_provinces


def coutries_to_enums(coutry_list: list[str]) -> list[Country]:
    """Format a list of countries as a string to a list of Country enums."""
    return [Country(country) for country in coutry_list]


def provinces_to_enums(province_list: list[str]) -> list[ProvinceBe | ProvinceFr | ProvinceNl]:
    """Format a list of provinces as a string to a list of Province enums."""
    new_list = []
    for province in province_list:
        if province in ProvinceBe.get_all_values_str():
            province_enum = ProvinceBe(province)
        elif province in ProvinceFr.get_all_values_str():
            province_enum = ProvinceFr(province)
        elif province in ProvinceNl.get_all_values_str():
            province_enum = ProvinceNl(province)
        else:
            raise ValueError(f"Unknown province: `{province}`")
        new_list.append(province_enum)
    return new_list


def regions_to_enums(region_list: list[str]) -> list[RegionBe | RegionFr | RegionNl]:
    """Format a list of regions as a string to a list of Region enums."""
    new_list = []
    for region in region_list:
        if region in RegionBe.get_all_values_str():
            region_enum = RegionBe(region)
        elif region in RegionFr.get_all_values_str():
            region_enum = RegionFr(region)
        elif region in RegionNl.get_all_values_str():
            region_enum = RegionNl(region)
        else:
            raise ValueError(f"Unknown region: `{region}`")
        new_list.append(region_enum)
    return new_list
