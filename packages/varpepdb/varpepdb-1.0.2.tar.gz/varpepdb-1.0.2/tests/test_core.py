import rpg
import rpg.RapidPeptidesGenerator
import varpepdb.classes as vc
import varpepdb
import varpepdb.core as vco
import unittest
import Bio.SeqUtils

enzyme_obj = rpg.RapidPeptidesGenerator.ALL_ENZYMES[26]


def setUpModule():
    varpepdb.setenzyme(enzyme_obj)


def generatevariant(peptide, pos, target):
    converter = Bio.SeqUtils.IUPACData.protein_letters_1to3
    target_3 = converter[target]
    source = converter[str(peptide)[pos]]
    start = peptide.start
    return f"{peptide.identifier}:p.{source}{start+pos+1}{target_3}"


class TestGenerateBreakerPeptides(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.peptide = vc.Peptide("FNGIYADPSGHCNFFWPSLFSHYKALMPAGNCI", 'identifier', 'gene')

    def test_novariant(self):
        variants = vc.Variant([], enzyme_obj)
        testres = vco._generate_breaker_peptides(variants=variants, peptide=self.peptide)
        self.assertEqual(str(testres[0]), 'FNGIYADPSGHCNFFW')
        self.assertEqual(str(testres[1]), 'PSLFSHYKALMPAGNCI')

    def test_exclude_enzymevariantsite(self):
        variants = vc.Variant([generatevariant(self.peptide, 15, 'K')], enzyme_obj)
        testres = vco._generate_breaker_peptides(variants=variants, peptide=self.peptide)
        self.assertEqual(str(testres[0]), 'FNGIYADPSGHCNFFWPSLFSHYKALMPAGNCI')


class TestAllocateVariantstoPeptide(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.peptide = vc.Peptide("FNGIYADPSGHCNFFWPSLFSHYKALMPAGNCI", 'identifier', 'gene')

    def assertVariants(self, variants, targets):
        for i, j in zip(variants, targets):
            self.assertEqual(i.string, j)

    def test_novariant(self):
        variants = vc.Variant([], enzyme_obj)
        testres = vco._allocate_variants_to_peptide(variants, self.peptide)
        self.assertEqual(testres.enzyme_variants, [])
        self.assertEqual(testres.nonenzyme_variants, [])

    def test_variants(self):
        hgvs = [generatevariant(self.peptide, 13, 'W'),
                generatevariant(self.peptide, 20, 'K'),
                generatevariant(self.peptide, 25, 'G')
                ]
        variants = vc.Variant(hgvs, enzyme_obj)
        testres = vco._allocate_variants_to_peptide(variants, self.peptide)
        self.assertVariants(testres.enzyme_variants, ['p.Phe14Trp'])
        self.assertVariants(testres.nonenzyme_variants, ['p.Ser21Lys', 'p.Leu26Gly'])


class TestCleaveBreakerPeptide(unittest.TestCase):

    def test_cleavage_removed(self):
        peptide = vc.Peptide("ADPSGHCNFFWPSLFSHYKALM", 'identifier', 'gene')
        hgvs = [generatevariant(peptide, 10, 'K')]
        variants = vc.Variant(hgvs, enzyme_obj)
        peptide = vco._allocate_variants_to_peptide(variants, peptide)
        cleaved_within = vco._cleave_breaker_peptides(peptide)
        self.assertEqual([str(i) for i in cleaved_within[0]], ['ADPSGHCNFFW', 'PSLFSHYKALM'])
        self.assertEqual(str(cleaved_within[1][0]), 'ADPSGHCNFFKPSLFSHYKALM')

    def test_cleavage_added(self):
        peptide = vc.Peptide("ADPSGHCNFFKPSLFSHYKALM", 'identifier', 'gene')
        hgvs = [generatevariant(peptide, 10, 'W')]
        variants = vc.Variant(hgvs, enzyme_obj)
        peptide = vco._allocate_variants_to_peptide(variants, peptide)
        cleaved_within = vco._cleave_breaker_peptides(peptide)
        self.assertEqual(str(cleaved_within[0][0]), 'ADPSGHCNFFKPSLFSHYKALM')
        self.assertEqual([str(i) for i in cleaved_within[1]], ['ADPSGHCNFFW', 'PSLFSHYKALM'])


class TestDeduplicate(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.peptide = vc.Peptide("FNGIYADPSGHCNFFWPSLFSHYKALMPAGNCI", 'identifier', 'gene')

    def test_deduplicate(self):
        hgvs = [generatevariant(self.peptide, 15, 'K'),
                generatevariant(self.peptide, 22, 'W')]
        variants = vc.Variant(hgvs, enzyme_obj)
        peptide = vco._allocate_variants_to_peptide(variants, self.peptide)
        cleaved_within = vco._cleave_breaker_peptides(peptide)
        cleaved_peptides_within_length = [j for i in cleaved_within for j in i if j.within_length()]
        cleaved_list = vco._deduplicate(cleaved_peptides_within_length)
        self.assertEqual(len(cleaved_list), 3)
        self.assertEqual(len(cleaved_list[1].applied_enzymevariants), 1)
        self.assertEqual(cleaved_list[1].applied_enzymevariants[0].string, 'p.Tyr23Trp')

    def test_novariants(self):
        hgvs = []
        variants = vc.Variant(hgvs, enzyme_obj)
        peptide = vco._allocate_variants_to_peptide(variants, self.peptide)
        cleaved_within = vco._cleave_breaker_peptides(peptide)
        cleaved_peptides_within_length = [j for i in cleaved_within for j in i if j.within_length()]
        cleaved_list = vco._deduplicate(cleaved_peptides_within_length)
        self.assertEqual(len(cleaved_list), 0)


class TestSprinkleVariants(unittest.TestCase):

    def assertsequenceprop(self, peptide, targets):
        for i, j in zip(peptide, targets):
            self.assertEqual(str(i), j)


    def test_sprinkle(self):
        peptide = vc.Peptide("FNGIYADPSGH", 'identifier', 'gene', start=20)
        hgvs = [generatevariant(peptide, 5, 'K'),
                generatevariant(peptide, 7, 'Y')]
        variants = vc.Variant(hgvs, enzyme_obj)
        peptide = vco._allocate_variants_to_peptide(variants, peptide)
        peptide_variant = vco._sprinkle_variants(peptide=peptide)
        self.assertsequenceprop(peptide_variant, ['FNGIYADPSGH',
                                                  'FNGIYADYSGH',
                                                  'FNGIYKDPSGH',
                                                  'FNGIYKDYSGH'])
        self.assertEqual(peptide_variant[0].applied_nonenzymevariants, [])
        variant_list = [j.string for i in peptide_variant[1:] for j in i.applied_nonenzymevariants]
        self.assertEqual(variant_list, ['p.Pro28Tyr', 'p.Ala26Lys', 'p.Ala26Lys', 'p.Pro28Tyr'])


class TestMiscleaveWithinBreakers(unittest.TestCase):

    default_max_length = vc.Peptide.max_length
    default_min_length = vc.Peptide.min_length

    @classmethod
    def setUpClass(cls):
        varpepdb.setpeptidelengths(6, 30)

    @classmethod
    def tearDownClass(cls):
        varpepdb.setpeptidelengths(cls.default_max_length, cls.default_min_length)

    def test_gap(self):
        peptide1 = vc.Peptide("FNGIYADPSG", 'identifier', 'gene', start=20, miscleave_count=0)
        peptide2 = vc.Peptide("FNGIYADPSG", 'identifier', 'gene', start=61, miscleave_count=0)
        peptide_list = [[peptide1, peptide2]]
        miscleaved_peptide = vco._miscleave_within_breakers(peptide_list)
        self.assertEqual(miscleaved_peptide, [])

    def test_nogap(self):
        peptide1 = vc.Peptide("FNGIYADPSG", 'identifier', 'gene', start=20)
        peptide2 = vc.Peptide("FNGIYADPSG", 'identifier', 'gene', start=30)
        peptide_list = [[peptide1, peptide2]]
        miscleaved_peptide = vco._miscleave_within_breakers(peptide_list)
        self.assertEqual(str(miscleaved_peptide[0]), 'FNGIYADPSGFNGIYADPSG')
        self.assertEqual(miscleaved_peptide[0].start, 20)
        self.assertEqual(miscleaved_peptide[0].end, 39)


class MiscleaveBetBreakers(unittest.TestCase):

    def test_2to1(self):
        peptide1 = vc.Peptide("FNGIYADPSG", 'identifier', 'gene', start=20, miscleave_count=0)
        peptide2 = vc.Peptide("DFNDFNDFND", 'identifier', 'gene', start=20, miscleave_count=0)
        peptide_list1 = [peptide1, peptide2]
        peptide3 = vc.Peptide("FNGIYADPSG", 'identifier', 'gene', start=32, miscleave_count=0)
        peptide4 = vc.Peptide("DFNDFNDFND", 'identifier', 'gene', start=31, miscleave_count=0)
        peptide_list2 = [peptide3, peptide4]
        miscl_pep_bet = vco._miscleave_bet_breakers(peptide_list1, peptide_list2)
        self.assertEqual(len(miscl_pep_bet), 0)

    def test_2to1(self):
        peptide1 = vc.Peptide("FNGIYADPSG", 'identifier', 'gene', start=20, miscleave_count=0)
        peptide2 = vc.Peptide("DFNDFNDFND", 'identifier', 'gene', start=20, miscleave_count=0)
        peptide_list1 = [peptide1, peptide2]
        peptide3 = vc.Peptide("FNGIYADPSG", 'identifier', 'gene', start=30, miscleave_count=0)
        peptide4 = vc.Peptide("DFNDFNDFND", 'identifier', 'gene', start=31, miscleave_count=0)
        peptide_list2 = [peptide3, peptide4]
        miscl_pep_bet = vco._miscleave_bet_breakers(peptide_list1, peptide_list2)
        self.assertEqual(str(miscl_pep_bet[0]), 'FNGIYADPSGFNGIYADPSG')
        self.assertEqual(str(miscl_pep_bet[1]), 'DFNDFNDFNDFNGIYADPSG')


if __name__ == "__main__":
    unittest.main()
