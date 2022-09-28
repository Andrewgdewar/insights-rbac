# Baseline tests for OCM performance 
# 
# 1 request for each tenant (to get tenant's groups)
# 1 request for each group (to get roles)
# 1 request for each tenant (to get the principles)
# 1 request for each principle in each org (to get the principles' groups)

# Populate the database with a large number of tenants, groups, principles, and roles
# ~20k requests = ~2k tenants ~10 principle per tenant 
# optional req: 2 groups per principle, 5 roles per group with 10 permissions each

from http.client import REQUEST_TIMEOUT
from multiprocessing.pool import ThreadPool
import pdb
import time

import concurrent
from concurrent.futures import ThreadPoolExecutor, as_completed
from faker import Faker

from base64 import b64encode
from json import dumps as json_dumps
from urllib import request, response

from django.core.management.base import BaseCommand
import unittest

from django.test import SimpleTestCase, TestCase
from management.role.model import ExtRoleRelation, ExtTenant
from rbac.settings import DATABASES

from rest_framework import status

from api.models import Tenant, User
from api.serializers import create_tenant_name
from rbac.middleware import HttpResponseUnauthorizedRequest, IdentityHeaderMiddleware, TENANTS
from management.models import Access, Group, Permission, Principal, Policy, ResourceDefinition, Role

# for spreadsheeting
import openpyxl as xl

# import test functions
from tests.performance.test_performance import test_full_sync, test_tenant_groups, test_tenant_roles, test_group_roles, test_principals_roles, test_principals_groups

from tests.performance.performance_db_util import setUp, tearDown, N_TENANTS, GROUPS_PER_TENANT, N, PRINCIPLES_PER_TENANT

N_TENANTS = 2
GROUPS_PER_TENANT = 1

N = 1 # number of roles per group, number of principals per group
PRINCIPLES_PER_TENANT = 1

HEADERS = {
            "identity": {
                "account_number": "10001",
                "org_id": "11111",
                "type": "Associate",
                "user": {
                    "username": "user_dev",
                    "email": "user_dev@foo.com",
                    "is_org_admin": True,
                    "is_internal": True,
                    "user_id": "51736777",
                },
                "internal": {"cross_access": False},
            }
        }

THREADS = 10

class Command(BaseCommand):
    help = """
    Run the OCM performance tests. If running locally,
    run the setup command first to populate the database.

    Usage:
        python manage.py command ocm_performance setup
    """

    def add_arguments(self, parser):
        parser.add_argument("mode", type=str, nargs='?', default='test', help="Choice of setup, test, or teardown")

    def handle(self, **options):
        mode = options["mode"]
        if mode == "setup":
            setUp()
        elif mode == "teardown":
            tearDown()
        elif mode == "test":
            # run the ocm performance tests
            test_full_sync()
            test_tenant_groups()
            test_tenant_roles()
            test_group_roles()
            test_principals_roles()
            test_principals_groups()
        else:
            print("Invalid mode. Please choose from setup, test, or teardown.")