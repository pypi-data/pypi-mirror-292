from .Section import Section


class GBSection(Section):
    section_type = 'GB'

    def __init__(self, section: str, fy: float=None):
        """get section property with given section name 

        Args:
            section (str): section name
            fy (float, optional): yield strength (Dafault to None).

        Example:
            >>> section = GBSection('HW100x100', fy=345)
        """
        super().__init__(section, fy, 'GB')