import numpy as np
from easychem.ecfortran import easychem_fortran_source as ecf
import os

HOME_PATH = os.path.expanduser("~")
MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATAFILE = 'thermo_easy_chem_simp_own.inp'

def _find_thermofpath():
    return os.path.join(MODULE_PATH, DEFAULT_DATAFILE)

class ExoAtmos:
    """
    This is a class that allows to compute the abundances of chemical species in an exoplanet atmosphere.

    Constant attributes:
        ATOM_STR_LEN = 2    Length of the strings for atom names
        REAC_STR_LEN = 15   Length of the strings for reactant names
    """

    ATOM_STR_LEN = 2
    REAC_STR_LEN = 15

    def __init__(self, atoms=None, reactants=None, atomAbunds=None, thermofpath=None, metallicity=None, co=None, atmFunc=None, atmArgs=None):
        """
        Constructor method

        :param atoms: Names of the atoms present in the considered atmosphere.
        :type atoms: np.ndarray(str), optional

        :param reactants: Names of the reactants present in the considered atmosphere.
        :type reactants: np.ndarray(str), optional

        :param atomAbunds: Atom abundances in the considered atmosphere (default: stellar abundances).
        :type atomAbunds: np.ndarray(float) with same size as `atoms`, optional

        :param thermofpath: Path of the file containing all the thermodynamic data (default: path contained in a '.easychem' file in the home directory).
        :type thermofpath: str, optional

        :param metallicity: Global metallicity of the considered atmosphere. If set, will update the atom abundances accordingly.
        :type metallicity: float, optional

        :param co: The overall carbon-to-oxygen ratio in the considered atmosphere. If set, will update the oxygen abundance accordingly.
        :type co: float, optional

        :param atmFunc: Custom function taking `self._atoms` and `self._atomAbundsOrig` as parameters to compute updated atom abundances stored in `self._atomAbunds`.
        :type atmFunc: function taking at least two parameters (np.ndarray(str) and np.ndarray(float) with same size) and returning a np.ndarray(float) of the same size, optional

        :param atmArgs: Additional arguments to provide to `atmFunc`. If provided, `atmFunc` must also be provided.
        :type atmArgs: iterative, optional
        """

        self._initialized = False
        self._solved = False
        self._valid = True
        if atoms is None :
            self._atoms = np.array(['H', 'He', 'C', 'N', 'O', 'Na', 'Mg', 'Al', 'Si', 'P',
                                    'S', 'Cl', 'K', 'Ca', 'Ti', 'V', 'Fe', 'Ni'])
        else:
            self._atoms = np.array(atoms)

        if reactants is None :
            self._reactants = np.array(['H', 'H2', 'He', 'O', 'C', 'N', 'Mg', 'Si', 'Fe', 'S', 'Al', 'Ca', 'Na', 'Ni',
                                        'P', 'K', 'Ti', 'CO', 'OH', 'SH', 'N2', 'O2', 'SiO', 'TiO', 'SiS', 'H2O', 'C2',
                                        'CH', 'CN', 'CS', 'SiC', 'NH', 'SiH', 'NO', 'SN', 'SiN', 'SO', 'S2', 'C2H',
                                        'HCN', 'C2H2,acetylene', 'CH4', 'AlH', 'AlOH', 'Al2O', 'CaOH', 'MgH', 'MgOH',
                                        'PH3', 'CO2', 'TiO2', 'Si2C', 'SiO2', 'FeO', 'NH2', 'NH3', 'CH2', 'CH3', 'H2S',
                                        'VO', 'VO2', 'NaCl', 'KCl', 'e-', 'H+', 'H-', 'Na+', 'K+', 'PH2', 'P2', 'PS',
                                        'PO', 'P4O6', 'PH', 'V', 'FeH', 'VO(c)','VO(L)','MgSiO3(c)','SiC(c)',
                                        'Fe(c)','Al2O3(c)','Na2S(c)','KCl(c)','Fe(L)','SiC(L)',
                                        'MgSiO3(L)','H2O(L)','H2O(c)','TiO(c)','TiO(L)',
                                        'TiO2(c)','TiO2(L)','H3PO4(c)','H3PO4(L)'])
        else:
            self._reactants = np.array(reactants)

        if atomAbunds is None:
            self._atomAbundsOrig = np.array([0.9207539305, 0.0783688694, 0.0002478241, 6.22506056949881E-05, 0.0004509658, 1.60008694353205E-06, 3.66558742055362E-05, 0.000002595, 0.000029795, 2.36670201997668E-07, 1.2137900734604E-05, 2.91167958499589E-07, 9.86605611925677E-08, 2.01439011429255E-06, 8.20622804366359E-08, 7.83688694089992E-09, 2.91167958499589E-05, 1.52807116806281E-06])
        else:
            self._atomAbundsOrig = atomAbunds
        self._atomAbunds = self._atomAbundsOrig.copy()

        assert self._atoms.size == self._atomAbunds.size, 'The arrays containing the atoms names and abundances should have the same size.'

        if thermofpath is None :
            self._thermofpath = _find_thermofpath()
        else:
            self._thermofpath = thermofpath

        if atmFunc is None:
            if metallicity is not None:
                self._metallicity = metallicity
                self._updatemetallicity()
            if co is not None:
                self._co = co
                self._updateCO()
        else:
            self._atmFunc = atmFunc
            self._atmArgs = atmArgs
            self._updadeWithFunc()

        self._normAbunds()

    ############################################################
    ####################### PROPERTIES #########################
    ############################################################

    # ATOMS : array of atoms present in the atmosphere
    @property
    def atoms(self):
        """
        Type: array of strings. Names of the atoms present in the considered atmosphere.
        """
        return list(self._atoms)

    @atoms.setter
    def atoms(self, input):
        """
        Setter method for the `atoms` property

        :param input: strings representing the atoms present in the atmosphere.
        :type input: iterative of strings (list or np.ndarray for example)
        """
        tab = np.array(input) if type(input) != np.ndarray else input
        if len(tab) != len(self._atoms) or np.any(tab != self._atoms):
            self._initialized = False
            self._solved = False
            self._atoms = tab

    def updateAtoms(self, input):
        """
        Method to set the `atoms` property to `input`

        :param input: strings representing the atoms present in the atmosphere.
        :type input: iterative of strings (list or np.ndarray for example)
        """
        self.atoms = input

    # REACTANTS : array of reactants present in the atmosphere
    @property
    def reactants(self):
        """
        Type: array of strings. Names of the reactants present in the considered atmosphere.
        """
        return list(self._reactants)

    @reactants.setter
    def reactants(self, input):
        """
        Setter method for the `reactants` property

        :param input: strings representing the reactants present in the atmosphere.
        :type input: iterative of strings (list or np.ndarray for example)
        """
        tab = np.array(input) if type(input) != np.ndarray else input
        if len(tab) != len(self._reactants) or np.any(tab != self._reactants):
            self._initialized = False
            self._solved = False
            self._reactants = tab

    def updateReactants(self, input):
        """
        Method to set the `reactants` property

        :param input: strings representing the reactants present in the atmosphere.
        :type input: iterative of strings (list or np.ndarray for example)
        """
        self.reactants = input

    # THERMOFPATH : string containing the path to the thermodynamic data file
    @property
    def thermofpath(self):
        """
        Type: string. Path of the file containing all the thermodynamic data (default: path contained in a '.easychem' file in the home directory)
        """
        return self._thermofpath

    @thermofpath.setter
    def thermofpath(self, string):
        """
        Setter method for the `thermofpath` property

        :param string: path to the new thermodynamic data file.
        :type string: string
        """
        if self._thermofpath != string:
            self._initialized = False
            self._solved = False
            self._thermofpath = string

    def updateThermofpath(self, string):
        """
        Method to set the `thermofpath` property

        :param string: path to the new thermodynamic data file.
        :type string: string
        """
        self.thermofpath = string

    # ATOM ABUNDS ORIG : array of floats corresponding to the elemental abundances for each atom in "atoms", usually the stellar abundances
    @property
    def atomAbundsOrig(self):
        '''Array of floats => elemental abundances of the considered atmosphere, usually the stellar abundances ; base array used to generate atomAbunds by adjusting to metallicity, co and/or atmFunc'''
        return self._atomAbundsOrig

    @atomAbundsOrig.setter
    def atomAbundsOrig(self, tab):
        assert self._atoms.size == tab.size, 'The arrays containing the atoms names and abundances should have the same size.'
        self._solved = False
        self._atomAbundsOrig = tab
        self._atomAbunds = tab.copy()
        self._updateAtomAbunds()

    def updateAtomAbundsOrig(self, tab):
        self.atomAbundsOrig = tab

    # ATOM ABUNDS : array of floats, elemental abundances ; array used in computation
    @property
    def atomAbunds(self):
        '''Array of floats => elemental abundances of the considered atmosphere ; array used in chemistry computation'''
        return self._atomAbunds

    @atomAbunds.setter
    def atomAbunds(self, tab):
        assert self._atoms.size == tab.size, 'The arrays containing the atoms names and abundances should have the same size.'
        self._solved = False
        self._atomAbundsOrig = tab
        self._atomAbunds = tab.copy()
        self._normAbunds()

    def updateAtomAbunds(self, tab):
        self.atomAbunds = tab

    # metallicity : global metallicity of atmosphere, computation considers that atomAbundsOrig represents the stellar abundances
    @property
    def metallicity(self):
        '''Float => atmosphere's metallicity ; automatically updates atomAbunds considering atomAbundsOrig as the stellar abundances (incompatible with atmFunc, if atmFunc is set, priority is given to atmFunc)'''
        return self._metallicity

    @metallicity.setter
    def metallicity(self, value):
        self._solved = False
        self._metallicity = value
        self._atomAbunds = self._atomAbundsOrig.copy()
        self._updateAtomAbunds()

    def updatemetallicity(self, value):
        self.metallicity = value

    @metallicity.deleter
    def metallicity(self):
        self._solved = False
        del self._metallicity
        self._atomAbunds = self._atomAbundsOrig.copy()
        self._updateAtomAbunds()

    # CO : C/O ratio
    @property
    def co(self):
        '''Float => C/O ratio ; automatically updates atomAbunds (if atmFunc is set, atmFunc will be applied first)'''
        return self._co

    @co.setter
    def co(self, value):
        self._solved = False
        self._co = value
        self._atomAbunds = self._atomAbundsOrig.copy()
        self._updateAtomAbunds()

    def updateCo(self, value):
        self.co = value

    @co.deleter
    def co(self):
        self._solved = False
        del self._co
        self._atomAbunds = self._atomAbundsOrig.copy()
        self._updateAtomAbunds()

    # ATMFUNC : custom function provided by user to tinker the elemental abundances in any way they like
    @property
    def atmFunc(self):
        '''Function used on atomAbundsOrig to generate atomAbunds, automatically computed'''
        return self._atmFunc

    def updateAtmFunc(self, func, args=None):
        self._solved = False
        self._atmFunc = func
        self._atmArgs = args
        self._atomAbunds = self._atomAbundsOrig.copy()
        self._updateAtomAbunds()

    @property
    def atmArgs(self):
        '''None or Tuple => arguments to pass to atmFunc'''
        return self._atmArgs

    @atmArgs.setter
    def atmArgs(self, args):
        self._solved = False
        self._atmArgs = args
        self._atomAbunds = self._atomAbundsOrig.copy()
        self._updadeWithFunc()
        self._normAbunds()

    def updateAtmArgs(self, args):
        self.atmArgs = args

    def delAtmFunc(self):
        self._solved = False
        del self._atmFunc
        self._atmArgs = None
        self._atomAbunds = self._atomAbundsOrig.copy()
        self._updateAtomAbunds()

    # INITIALIZED : flag indicating if the Fortran side was initialized
    @property
    def initialized(self):
        return self._initialized

    # SOLVED : flag indicating if the system with the current given parameters is already solved, ie. if the object already contains the chemical abundances
    @property
    def solved(self):
        return self._solved

    # VALID : flag indicating if during at least one run some error occured in Fortran
    @property
    def valid(self):
        return self._valid

    # REACMOLS : result => reactants' molecular fractions
    @property
    def reacMols(self):
        return self._getterResults('_reacMols', "reactants' molecular abundances")

    def getReacMols(self):
        """Returns self.reacMols as a dictionary with self.reactants as keys"""
        if self.reacMols.ndim >= 2:
            return dict(zip(self._reactants, self.reacMols.T))
        else:
            return dict(zip(self._reactants, self.reacMols))

    # REACMASS : result => reactants' mass fractions
    @property
    def reacMass(self):
        return self._getterResults('_reacMass', "reactants' mass fractions")

    def getReacMass(self):
        """Returns self.reacMass as a dictionary with self.reactants as keys"""
        if self.reacMass.ndim >= 2:
            return dict(zip(self._reactants, self.reacMass.T))
        else:
            return dict(zip(self._reactants, self.reacMass))

    # ADIABATIC GRAD : result => adiabatic gradient
    @property
    def adiabaticGrad(self):
        return self._getterResults('_adiabaticGrad', "adiabatic gradient")

    # GAMMA2 : result => ? gamma squared ?
    @ property
    def gamma2(self):
        return self._getterResults('_gamma2', '')

    # MMW : result => mean molecular weight
    @property
    def mmw(self):
        return self._getterResults('_mmw', 'mean molecular weight')

    # DENSITY : result => mean? density
    @property
    def density(self):
        return self._getterResults('_density', 'mean density')

    # C_PE : result => ?
    @property
    def c_pe(self):
        return self._getterResults('_c_pe', '')

    ############################################################
    ###################### USER METHODS ########################
    ############################################################

    def solve(self, pressure, temperature):
        if not self._initialized:
            atoms = ExoAtmos.strArr_to_bytArr(self._atoms, ExoAtmos.ATOM_STR_LEN)
            react = ExoAtmos.strArr_to_bytArr(self._reactants, ExoAtmos.REAC_STR_LEN)
            ecf.set_data(atoms, react, self.thermofpath)
            self._initialized = True

            gotError = bool(ecf.error)
            if gotError:
                msg = bytes(ecf.err_msg).decode()
                raise ValueError(msg.rstrip())

        self._valid = True
        n_reac = len(self._reactants)

        try:
            n_prof = len(pressure)
            isProfile = True
        except TypeError:
            isProfile = False

        if isProfile:
            if len(pressure) != len(temperature):
                raise ValueError("Pressure and temperature arrays aren't of the same size")
            if not self._solved or self._reacMols.shape!=(n_prof,n_reac):
                self._reacMols = np.empty((n_prof,n_reac))
                self._reacMass = np.empty((n_prof,n_reac))
                self._adiabaticGrad = np.empty(n_prof)
                self._gamma2 = np.empty(n_prof)
                self._mmw = np.empty(n_prof)
                self._density = np.empty(n_prof)
                self._c_pe = np.empty(n_prof)
            for i in range(n_prof):
                mol, mass, nabla_ad, gamma2, mmw, rho, c_pe = ecf.easychem('q', '', n_reac, self._atomAbunds, temperature[i], pressure[i])

                gotError = bool(ecf.error)
                if gotError:
                    msg = bytes(ecf.err_msg).decode()
                    print('T={:.2e} ; P={:.2e}\t'.format(temperature[i], pressure[i]), msg.rstrip())
                    mol, mass, nabla_ad, gamma2, mmw, rho, c_pe = np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan
                    self._valid = False

                self._reacMols[i] = mol
                self._reacMass[i] = mass
                self._adiabaticGrad[i] = nabla_ad
                self._gamma2[i] = gamma2
                self._mmw[i] = mmw
                self._density[i] = rho
                self._c_pe[i] = c_pe

        else:
            mol, mass, nabla_ad,gamma2,mmw,rho,c_pe = ecf.easychem('q', '', n_reac, self._atomAbunds, temperature, pressure)

            gotError = bool(ecf.error)
            if gotError:
                msg = bytes(ecf.err_msg).decode()
                print(msg)
                mol, mass, nabla_ad, gamma2, mmw, rho, c_pe = np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan
                self._valid = False

            self._reacMols = mol
            self._reacMass = mass
            self._adiabaticGrad = nabla_ad
            self._gamma2 = gamma2
            self._mmw = mmw
            self._density = rho
            self._c_pe = c_pe

        self._solved = True

    def result_mol(self):
        if self.reacMols.ndim >= 2:
            return dict(zip(self._reactants, self.reacMols.T))
        else:
            return dict(zip(self._reactants, self.reacMols))

    def result_mass(self):
        if self.reacMass.ndim >= 2:
            return dict(zip(self._reactants, self.reacMass.T))
        else:
            return dict(zip(self._reactants, self.reacMass))

    ############################################################
    ################### INTERNAL METHODS #######################
    ############################################################

    def _updatemetallicity(self):
        for i in range(self._atomAbunds.size):
            if self._atoms[i].upper() != 'H' and self._atoms[i].upper() != 'HE':
                self._atomAbunds[i] = self._atomAbundsOrig[i] * 10**self._metallicity

    def _updateCO(self):
        atomsUp = np.char.upper(self._atoms)
        iC = np.nonzero(atomsUp=='C')[0][0]
        iO = np.nonzero(atomsUp=='O')[0][0]
        self._atomAbunds[iO] = self._atomAbunds[iC] / self._co

    def _updadeWithFunc(self):
        if self._atmArgs is None :
            self._atomAbunds = self._atmFunc(self._atoms, self._atomAbundsOrig)
        else:
            self._atomAbunds = self._atmFunc(self._atoms, self._atomAbundsOrig, *self._atmArgs)

    def _normAbunds(self):
        self._atomAbunds /= self._atomAbunds.sum()

    def _updateAtomAbunds(self):
        if hasattr(self, '_metallicity'):
            self._updatemetallicity()
        if hasattr(self, '_atmFunc'):
            self._updadeWithFunc()
        if hasattr(self, '_co'):
            self._updateCO()
        self._normAbunds()

    def _getterResults(self, attName, fullName):
        if hasattr(self, attName):
            return getattr(self, attName)
        else:
            if fullName=='':
                raise AttributeError("The wanted quantity hasn't been computed yet... Please run the 'solve' method.")
            else:
                raise AttributeError("The wanted quantity ({}) hasn't been computed yet... Please run the 'solve' method.".format(fullName))

    @staticmethod
    def strToBytes(a: str):
        return np.array([*a])

    @staticmethod
    def strArr_to_bytArr(a,m):
        # m = np.amax(np.char.str_len(a))
        res = np.empty((len(a), m), dtype='S1', order='F')
        for i, c in enumerate(a):
            res[i] = ExoAtmos.strToBytes(c.ljust(m, ' '))
        return res