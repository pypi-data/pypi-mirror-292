import pandas as pd
from pathlib import Path


class Section:
    cwd = Path(__file__).parent
    E = 206000
    section_type = 'Undefined'  # 'W' or 'GB'
    __doc__ = """This progarm can get properties of w-section steel beam
    Axis Definition:
                 ↑y
                 |
           ============
                 ‖
                 ‖        x
         --------‖--------→
                 ‖
                 ‖
           ============
                 |
    d: Depth
    bf: Top width
    tf: Flange thickness
    tw: Web thickness
    r: Fillet radius
    A: Area
    J: Torsion constant
    Iy: Moment of inertia about y-axis
    Ix: Moment of inertia about x-axis
    Alpha: Principal axis angle
    Iw: Warping constant
    Zy: Plastic modulars about y-axis
    Zx: Plastic modulars about x-axis
    (All units are in "mm" or "N")

    Update: 2024-03-14
    """


    def __init__(self, section: str, fy: float=None, section_type: str='Undefined'):
        """get section property with given section name 

        Args:
            section (str): section name
            fy (float, optional): yield strength (Dafault to None).

        Example:
            >>> section = WSection('W14x90', fy=345)
        """
        self.section = section
        self.section_type = section_type
        try:
            self.section_data = pd.read_csv(self.cwd / f'{self.section_type}-section.csv')
        except:
            raise FileNotFoundError(f'"{self.section_type}-section.csv" not found!')
        data = self._find_section(section)
        self.name, self.d, self.bf, self.tf, self._bf_bottom, self._tf_bottom, self.tw, self.r, self.A,\
            self.J, self.Iy, self.Ix, self.Alpha, self.Cy, self.Cx, self.Iw, self.Zy, self.Zx = data
        self.h = self.d - 2 * self.tf - 2 * self.r
        self.ry = (self.Iy / self.A) ** 0.5
        self.rx = (self.Ix / self.A) ** 0.5
        self.Wy = self.Iy / (self.d / 2)
        self.Wx = self.Ix / (self.d / 2)
        if fy:
            self.fy = fy
            # self.My = self.fy * self.Wx * 1.1
            self.My = self.fy * self.Zx  #　This line is added to calculate My based on Zx instead of Wx.
        
    def __getattr__(self, name):
        if name == 'My' or name == 'fy':
            raise AttributeError('Please define parameter `fy` first.')

    def set_fy(self, fy: int):
        """set yield strength of steel to calculate My.

        Args:
            fy (int): yield strength
        """
        self.fy = fy
        # self.My = self.fy * self.Wx * 1.1
        self.My = self.fy * self.Zx

    @classmethod
    def list_all_sections(cls) -> list:
        """list all sections

        Returns:
            list: a list includes all section names
        """
        try:
            section_data = pd.read_csv(cls.cwd / f'{cls.section_type}-section.csv')
        except:
            raise FileNotFoundError(f'"{cls.section_type}-section.csv" not found!')
        section_list = section_data['section'].to_list()
        print(f'Total {cls.section_type}-sections:', len(section_list))
        print(section_list)
        return section_list

    def _find_section(self, section: str):
        section1 = section.replace('h', 'H')
        section1 = section1.replace('m', 'M')
        section1 = section1.replace('n', 'N')
        section1 = section1.replace('w', 'W')
        section1 = section1.replace('X', 'x')
        section1 = section1.replace('w', 'W')
        try:
            data = self.section_data.loc[self.section_data['section'] == section1].iloc[0].tolist()
        except IndexError:
            raise ValueError(f'"{section}" not found!')
        return data
    
    def __repr__(self) -> str:
        return f'{self.section_type}-section: {self.name}'
