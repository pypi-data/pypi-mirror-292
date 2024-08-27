#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `APMSGeneNodeAttributeGenerator`"""

import os
import unittest
import shutil
import tempfile
import csv
from unittest.mock import MagicMock

from cellmaps_ppidownloader.gene import APMSGeneNodeAttributeGenerator

SKIP_REASON = 'CELLMAPS_PPIDOWNLOADER_INTEGRATION_TEST ' \
              'environment variable not set, cannot run integration ' \
              'tests'


class TestAPMSGeneNodeAttributeGenerator(unittest.TestCase):
    """Tests for `APMSGeneNodeAttributeGenerator`"""

    def setUp(self):
        """Set up test fixtures, if any."""
        self.generator = APMSGeneNodeAttributeGenerator()

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def get_test_data_dir(self):
        """
        get test data dir
        :return:
        """
        return os.path.join(os.path.dirname(__file__), 'data')

    def get_test_provenance(self):
        """
        Gets test provenance file path
        :return:
        """
        return os.path.join(self.get_test_data_dir(), 'test_provenance.json')

    def get_baitlist(self):
        """
        Gets baitlist file path
        :return:
        """
        return os.path.join(self.get_test_data_dir(), 'baitlist.tsv')

    def get_edgelist(self):
        """
        Gets edgelist file path
        :return:
        """
        return os.path.join(self.get_test_data_dir(), 'edgelist.tsv')

    def test_get_apms_edgelist_from_tsvfile(self):
        edgelist = APMSGeneNodeAttributeGenerator.get_apms_edgelist_from_tsvfile(self.get_edgelist())
        self.assertEqual(2783, len(edgelist))
        self.assertEqual('101928739', edgelist[0]['GeneID1'])
        self.assertEqual('PIK3CA', edgelist[0]['Symbol1'])
        self.assertEqual('219541', edgelist[0]['GeneID2'])
        self.assertEqual('MED19', edgelist[0]['Symbol2'])

    def test_get_apms_baitlist_from_tsvfile(self):
        baitlist_path = self.get_baitlist()
        baitlist = APMSGeneNodeAttributeGenerator.get_apms_baitlist_from_tsvfile(baitlist_path)
        self.assertGreater(len(baitlist), 0)
        first_entry = baitlist[0]
        self.assertIn('GeneSymbol', first_entry)
        self.assertIn('GeneID', first_entry)
        self.assertIn('NumInteractors', first_entry)

    def test_process_query_results(self):
        query_results = [
            {'query': 'GENE1', 'symbol': 'Symbol1', 'ensembl': {'gene': 'ENSG000001'}},
            {'query': 'GENE2', 'ensembl': {'gene': 'ENSG000002'}}
        ]
        _, symbol_query_dict, symbol_ensembl_dict, _ = self.generator._process_query_results(query_results)
        self.assertIn('Symbol1', symbol_query_dict)
        self.assertIn('GENE2', symbol_query_dict)
        self.assertIn('ENSG000001', symbol_ensembl_dict['Symbol1'])
        self.assertIn('ENSG000002', symbol_ensembl_dict['GENE2'])

    def test_create_gene_node_attributes_dict(self):
        symbol_query_dict = {'Symbol1': {'Query1'}, 'Symbol2': {'Query2'}}
        symbol_ensembl_dict = {'Symbol1': {'ENSG000001'}, 'Symbol2': {'ENSG000002'}}
        bait_set = {'Symbol1'}
        ambiguous_gene_dict = {'Symbol2': 'Symbol2,Symbol3'}
        gene_node_attrs = self.generator._create_gene_node_attributes_dict(
            symbol_query_dict, symbol_ensembl_dict, bait_set, ambiguous_gene_dict)
        self.assertIn('Symbol1', gene_node_attrs)
        self.assertTrue(gene_node_attrs['Symbol1']['bait'])
        self.assertIn('Symbol2,Symbol3', gene_node_attrs['Symbol2']['ambiguous'])

    def test_get_unique_genelist_from_edgelist(self):
        self.generator._apms_edgelist = [
            {'GeneID1': '1', 'Symbol1': 'GeneA', 'GeneID2': '2', 'Symbol2': 'GeneB'},
            {'GeneID1': '2', 'Symbol1': 'GeneB', 'GeneID2': '3', 'Symbol2': 'GeneC'}
        ]
        unique_genes, ambiguous_genes = self.generator._get_unique_genelist_from_edgelist()
        self.assertEqual(len(unique_genes), 3)
        self.assertSetEqual(set(unique_genes), {'1', '2', '3'})
        self.assertEqual(len(ambiguous_genes), 0)

    def test_get_unique_genelist_from_edgelist_with_ambiguous(self):
        self.generator._apms_edgelist = [
            {'GeneID1': '1', 'Symbol1': 'GeneA', 'GeneID2': '2,4', 'Symbol2': 'GeneB,GeneD'},
            {'GeneID1': '3', 'Symbol1': 'GeneC', 'GeneID2': '5', 'Symbol2': 'GeneE'}
        ]
        unique_genes, ambiguous_genes = self.generator._get_unique_genelist_from_edgelist()
        self.assertEqual(len(unique_genes), 5)
        self.assertSetEqual(set(unique_genes), {'1', '2', '3', '4', '5'})
        self.assertEqual(len(ambiguous_genes), 2)
        self.assertDictEqual(ambiguous_genes, {'2': '2,4', '4': '2,4'})

    def test_get_gene_node_attributes_with_input(self):
        edge_list = [
            {'GeneID1': '101928739', 'Symbol1': 'PIK3CA', 'GeneID2': '219541', 'Symbol2': 'MED19'},
            {'GeneID1': '101928739', 'Symbol1': 'PIK3CA', 'GeneID2': '26030', 'Symbol2': 'PLEKHG3'},
            {'GeneID1': '101928739', 'Symbol1': 'PIK3CA', 'GeneID2': '129446', 'Symbol2': 'XIRP2'},
            {'GeneID1': '101928739', 'Symbol1': 'PIK3CA', 'GeneID2': '644815', 'Symbol2': 'FAM83G'},
            {'GeneID1': '101928739', 'Symbol1': 'PIK3CA', 'GeneID2': '23347', 'Symbol2': 'SMCHD1'},
            {'GeneID1': '101928739', 'Symbol1': 'PIK3CA', 'GeneID2': '9124', 'Symbol2': 'PDLIM1'},
            {'GeneID1': '101928739', 'Symbol1': 'PIK3CA', 'GeneID2': '4641', 'Symbol2': 'MYO1C'},
            {'GeneID1': '101928739', 'Symbol1': 'PIK3CA', 'GeneID2': '5717', 'Symbol2': 'PSMD11'}
        ]
        bait_list = [
            {'GeneSymbol': 'PIK3CA', 'GeneID': '101928739', '# Interactors': 2783}
        ]
        mockgenequery = MagicMock()
        mockgenequery.get_symbols_for_genes = MagicMock(return_value=[{'query': '101928739',
                                                                       'ensembl': {'gene': '101928739'},
                                                                       'symbol': 'PIK3CA'
                                                                       }])

        ppigen = APMSGeneNodeAttributeGenerator(apms_edgelist=edge_list, apms_baitlist=bait_list, genequery=mockgenequery)

        gene_node_attrs, errors = ppigen.get_gene_node_attributes()

        self.assertTrue(len(gene_node_attrs) > 0)
        self.assertEqual(len(errors), 0)
