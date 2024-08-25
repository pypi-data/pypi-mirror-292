import numbers


def dipdir_str_to_float(
    azimuth: str
) -> numbers.Real:

    return float(azimuth) % 360.0


def strikerhr_str_to_dipdir_float(
    azimuth: str
) -> numbers.Real:

    return (float(azimuth) + 90.0) % 360.0
