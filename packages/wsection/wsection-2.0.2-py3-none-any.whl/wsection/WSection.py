from .Section import Section


class WSection(Section):
    section_type = 'W'

    def __init__(self, section: str, fy: float=None):
        """get section property with given section name 

        Args:
            section (str): section name
            fy (float, optional): yield strength (Dafault to None).

        Example:
            >>> section = WSection('W14x90', fy=345)
        """
        super().__init__(section, fy, 'W')