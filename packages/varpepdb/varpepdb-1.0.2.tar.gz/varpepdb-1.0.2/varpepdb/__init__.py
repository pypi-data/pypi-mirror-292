import varpepdb.classes as vc
import varpepdb.core as vco
from rpg.enzyme import Enzyme
from varpepdb.core import generate, generate_single, \
    variant_containing_peptides, write, separate_nonunique


def setmiscleave(miscleave: bool) -> None:
    """Turns miscleavage on or off

    Args:
        miscleave: True or False
    """
    vco.miscleave = miscleave


def setenzyme(enzyme_obj: Enzyme) -> None:
    """Select enzyme(s) for cleavage

    Args:
        enzyme_obj: Single or list of enzymes from the ``rpg`` package
    """
    if not isinstance(enzyme_obj, list):
        enzyme_obj = [enzyme_obj]
    vc.Cleaver.enzyme = enzyme_obj
    vc.Variant.enzyme = enzyme_obj


def setpeptidelengths(min_length: int, max_length: int) -> None:
    """Set peptide length limits

    Args:
        min_length
        max_length
    """
    vc.Peptide.min_length = min_length
    vc.Peptide.max_length = max_length
