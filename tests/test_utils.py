import unittest

from flask import request
from webargs import flaskparser

from tests import factories
from tests.common import ApiBaseTest

from webservices import args
from webservices import rest
from webservices import sorting
from webservices.resources import candidate_aggregates

from webservices.common import models


class TestSort(ApiBaseTest):

    def test_single_column(self):
        candidates = [
            factories.CandidateFactory(district='01'),
            factories.CandidateFactory(district='02'),
        ]
        query, columns = sorting.sort(models.Candidate.query, 'district', model=models.Candidate)
        self.assertEqual(query.all(), candidates)

    def test_single_column_reverse(self):
        candidates = [
            factories.CandidateFactory(district='01'),
            factories.CandidateFactory(district='02'),
        ]
        query, columns = sorting.sort(models.Candidate.query, '-district', model=models.Candidate)
        self.assertEqual(query.all(), candidates[::-1])

    def test_hide_null(self):
        candidates = [
            factories.CandidateFactory(district='01'),
            factories.CandidateFactory(district='02'),
            factories.CandidateFactory(),
        ]
        query, columns = sorting.sort(models.Candidate.query, 'district', model=models.Candidate)
        self.assertEqual(query.all(), candidates)
        query, columns = sorting.sort(models.Candidate.query, 'district', model=models.Candidate, hide_null=True)
        self.assertEqual(query.all(), candidates[:2])

    def test_hide_null_candidate_totals(self):
        candidates = [
            factories.CandidateFactory(candidate_id='C1234'),
            factories.CandidateFactory(candidate_id='C5678'),

        ]
        candidateHistory = [
            factories.CandidateHistoryFactory(candidate_id='C1234', two_year_period=2016),
            factories.CandidateHistoryFactory(candidate_id='C5678', two_year_period=2016)
        ]
        candidateTotals = [
            factories.CandidateTotalFactory(candidate_id='C1234', is_election=False, cycle=2016),
            factories.CandidateTotalFactory(candidate_id='C5678', disbursements='9999.99', is_election=False, cycle=2016)
        ]
        candidateFlags = [
            factories.CandidateFlagsFactory(candidate_id='C1234'),
            factories.CandidateFlagsFactory(candidate_id='C5678')
        ]

        tcv = candidate_aggregates.TotalsCandidateView()
        query, columns = sorting.sort(tcv.build_query(election_full=False), 'disbursements', model=None)
        self.assertEqual(len(query.all()), len(candidates))
        query, columns = sorting.sort(tcv.build_query(election_full=False), 'disbursements', model=None, hide_null=True)
        self.assertEqual(len(query.all()), len(candidates) - 1)
        self.assertTrue(candidates[1].candidate_id in query.all()[0])




class TestArgs(unittest.TestCase):

    def test_currency(self):
        with rest.app.test_request_context('?dollars=$24.50'):
            parsed = flaskparser.parser.parse({'dollars': args.Currency()}, request)
            self.assertEqual(parsed, {'dollars': 24.50})
