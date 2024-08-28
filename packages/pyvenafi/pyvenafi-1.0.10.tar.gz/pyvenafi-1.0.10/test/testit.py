"""
This Python script requires at least Python 3.8.

Purpose
-------

This script is simply an example script for testing end-to-end performance of certificate
renewal operations. Feel free to modify the test however you wish. This script uses pyVenafi
(https://pyvenafi.readthedocs.io/en/latest/) to connect to Venafi Trust Protection Platform
and execute WebSDK commands. Therefore, the user profile running tests will need to be one
having sufficient permissions to authenticate to the WebSDK, read, create, and renew self-signed
certificates. The intent is to measure each certificate's performance in issuance via the log
events and all certificate requests as a whole.

"""
from __future__ import annotations

import json
import logging
import os
import time
from concurrent.futures import (
    ThreadPoolExecutor,
    wait,
)
from dataclasses import dataclass
from datetime import datetime
from queue import Queue
from statistics import stdev

from pyvenafi.logger import logger
from pyvenafi.tpp import (
    AttributeValues,
    Authenticate,
    DN,
    Features,
    models,
    Scope,
)

# ------------------ CONFIG HERE ---------------------
class TestConfig:
    DEFAULT_LOG_LEVEL = "INFO"
    DEFAULT_RATE_OF_CONCURRENCY = 16
    DEFAULT_NUMBER_OF_RENEWALS = 500
    DEFAULT_OAUTH_SCOPE = Scope() \
        .certificate(read=True, manage=True, delete=True) \
        .configuration(delete=True, read=True, manage=True) \
        .restricted(read=True, delete=True) \
        .to_string()

    def __init__(self):
        config_file_content: dict[str, str] = {}
        if os.path.exists('config.json'):
            with open('config.json', 'r') as config_file:
                config_file_content = json.load(config_file)
        else:
            config_file_content = create_config()

        def get_config_attribute(
            os_var_key: str,
            config_file_key: str,
            default: any = None,
            required: bool = False
        ):
            value = os.getenv(os_var_key, config_file_content.get(config_file_key, default))
            if value is None and required is True:
                raise ValueError(
                    f'{config_file_key} is required. Set this in JSON or "{os_var_key}" in your environment.'
                )
            return value

        self.LOG_LEVEL = getattr(logging, (get_config_attribute('TPP_TEST_LOG_LEVEL', 'logLevel', "INFO")).upper())
        self.HOSTNAME = get_config_attribute('TPP_HOSTNAME', 'hostname')
        self.USERNAME = get_config_attribute('TPP_USERNAME', 'username')
        self.PASSWORD = get_config_attribute('TPP_PASSWORD', 'password')
        self.TOKEN = get_config_attribute('TPP_TOKEN', 'token')
        self.OAUTH_APPLICATION_ID = get_config_attribute(
            'TPP_OAUTH_APPLICATION_ID',
            'applicationId'
        )
        self.OAUTH_SCOPE = get_config_attribute(
            'TPP_OAUTH_SCOPE',
            'scope',
            default=TestConfig.DEFAULT_OAUTH_SCOPE,
        )
        self.ROOT_TEST_FOLDER = DN(
            get_config_attribute('TPP_ROOT_TEST_FOLDER', 'rootTestFolder', required=True)
        )
        self.RATE_OF_CONCURRENCY = int(
            get_config_attribute('TPP_RATE_OF_CONCURRENCY', 'rateOfConcurrency', TestConfig.DEFAULT_RATE_OF_CONCURRENCY)
        )
        self.NUMBER_OF_RENEWALS = int(
            get_config_attribute('TPP_NUMBER_OF_RENEWALS', 'numberOfRenewals', TestConfig.DEFAULT_NUMBER_OF_RENEWALS)
        )
        self.CERTIFICATE_AUTHORITY_DN = get_config_attribute('TPP_CERTIFICATE_AUTHORITY_DN', 'certificateAuthorityDn')

# ------------------ SCRIPT HERE ---------------------
@dataclass
class Benchmark:
    started: datetime = None
    ended: datetime = None

    @property
    def duration(self) -> float:
        if None not in (self.started, self.ended):
            return (self.ended - self.started).total_seconds()
        return -1.0

def run_test():
    config = TestConfig()
    logging.basicConfig(level=logging.WARNING)
    logger.setLevel(config.LOG_LEVEL)

    logger.info(f'Authenticating to {config.HOSTNAME} ...')
    api = Authenticate(
        host=config.HOSTNAME,
        username=config.USERNAME,
        password=config.PASSWORD,
        websdk_token=config.TOKEN,
        application_id=config.OAUTH_APPLICATION_ID,
        scope=config.OAUTH_SCOPE,
    )
    features = Features(api)
    logger.info('Authenticated!')

    # region Create Test Folders
    logger.info('Cleaning up old test objects...')
    root_test_folder = DN(f'{config.ROOT_TEST_FOLDER}\\VenTest')
    if features.objects.exists(object_dn=root_test_folder.dn):
        features.folder.delete(
            folder=root_test_folder,
            concurrency=16
        )
    logger.info('Creating test folders...')
    root_test_folder = features.folder.create(
        name='VenTest',
        parent_folder=config.ROOT_TEST_FOLDER,
        description='Venafi automation created this.',
        create_path=True,
    )
    logger.info('Created test folders!')
    # endregion Create Test Folders

    # region Configure The Certificate Authority
    if config.CERTIFICATE_AUTHORITY_DN is None:
        # region Create Self-Signed CA
        logger.info('Creating a self-signed CA...')
        certificate_authority = features.certificate_authority.self_signed.create(
            name='Test Self-Signed CA',
            parent_folder=root_test_folder,
            description='Venafi automation created this.',
            key_usage=[
                'EncipherOnly',
                'KeyAgreement',
                'DataEncipherment',
                'KeyEncipherment',
                'NonRepudiation',
                'DigitalSignature',
                'DecipherOnly'
            ],
            server_authentication=True,
            client_authentication=True,
            code_signing=True,
            signature_algorithm='SHA512',
            valid_years=1,
        )
        logger.info('Self-signed CA created!')
        # endregion Create Self-Signed CA
    else:
        certificate_authority = features.objects.get(object_dn=config.CERTIFICATE_AUTHORITY_DN)
    # endregion Configure The Certificate Authority

    # region Benchmark Certificate Renewals
    logger.info('Running certificate renewal benchmarks...')

    benchmarks: dict[str, any] = {
        'each': None,
        'total': None,
        'errors': {
            'create': 0,
            'enrollment': 0,
            'benchmark': 0,
        },
    }

    def create(i: int, parent_folder: models.config.Object, q: Queue):
        try:
            q.put(
                features.certificate.create(
                    name=f'certificate-{i}',
                    parent_folder=parent_folder,
                    description='Venafi automation created this.',
                    management_type=AttributeValues.Certificate.ManagementType.enrollment,
                    service_generated_csr=True,
                    generate_key_on_application=False,
                    hash_algorithm=AttributeValues.Certificate.HashAlgorithm.sha256,
                    common_name=f'venafi-auto-certificate-{i}.test',
                    organization='Venafi Testing',
                    organization_unit=['Test 1', 'Test 2'],
                    city='Salt Lake City',
                    state='UT',
                    country='US',
                    key_algorithm=AttributeValues.Certificate.KeyAlgorithm.rsa,
                    key_strength=2048,
                    ca_template=certificate_authority,
                    # san_dns=[
                    #     f'venafi-auto-certificate-{i}.test',
                    #     f'venafi-auto-certificate-{i}{i}.test'
                    # ],
                    # contacts=None,
                    # approvers=None,
                    # san_email=None,
                    # san_upn=None,
                    # san_uri=None,
                    # san_ip=None,
                    # elliptic_curve=None,
                    # disable_automatic_renewal=True,
                    # renewal_window=None,
                )
            )
        except:
            benchmarks['errors']['create'] += 1

    def renew(certificate: models.config.Object):
        try:
            # We shouldn't need this, but in case TPP complains about it...
            # try:
            #     features.certificate.reset(certificate=certificate)
            # except:
            #     pass
            thumbprint = features.certificate.renew(certificate=certificate)
            features.certificate.wait_for_enrollment_to_complete(
                certificate=certificate,
                current_thumbprint=thumbprint,
                timeout=300,  # Let's give this plenty of time to finish.
            )
        except:
            benchmarks['errors']['enrollment'] += 1

    def collect(certificate: models.config.Object, q: Queue):
        if certificate is None:
            return

        renewal_benchmark = Benchmark()

        def _get_certificate_operations_started(events: 'list[models.log.LogEvent]'):
            return next(
                e.client_timestamp for e in events if 'Certificate Operations Started' in e.name
            )

        # def _get_certificate_enrollment_completed(events: 'list[models.log.LogEvent]'):
        #     return next(
        #         e.client_timestamp for e in events if
        #         'Certificate Initial Enrollment Completed' in e.name or 'Certificate Renewal Completed' in e.name
        #     )

        def _get_certificate_operations_completed(events: 'list[models.log.LogEvent]'):
            return next(
                e.client_timestamp for e in events if 'Certificate Operations Completed' in e.name
            )

        def _load_benchmark():
            exc = None
            retries = 50
            while retries > 0:
                events = features._api.websdk.Log.Guid(certificate.guid).get().log_events
                try:
                    certificate_operations_started = _get_certificate_operations_started(events)
                    certificate_operations_completed = _get_certificate_operations_completed(events)

                    # Total
                    renewal_benchmark.started = certificate_operations_started
                    renewal_benchmark.ended = certificate_operations_completed

                    if renewal_benchmark.duration >= 0:
                        return renewal_benchmark
                    exc = AssertionError('Failed to calculate benchmarks for the logs.')
                except:
                    exc = AssertionError('Failed to calculate benchmarks for the logs.')
                time.sleep(1)
                retries -= 1
            raise exc

        try:
            _load_benchmark()
            q.put(renewal_benchmark)
        except:
            benchmarks['errors']['benchmark'] += 1

    def run_renewals():
        overall_benchmark = Benchmark()
        certificates_queue = Queue()
        benchmarks_queue = Queue()

        logger.info(f'Running renewal tests under {root_test_folder}...')
        with ThreadPoolExecutor(config.RATE_OF_CONCURRENCY) as pool:
            logger.info(f'Creating {config.NUMBER_OF_RENEWALS} certificates...')
            futures = [
                pool.submit(create, i, root_test_folder, certificates_queue)
                for i in range(config.NUMBER_OF_RENEWALS)
            ]
            wait(futures)

            overall_benchmark.started = datetime.now()
            logger.info(f'Renewing {config.NUMBER_OF_RENEWALS} certificates...')
            futures = [
                pool.submit(renew, certificate)
                for certificate in list(certificates_queue.queue)
            ]
            wait(futures)
            overall_benchmark.ended = datetime.now()

            logger.info(f'Collecting logs for {config.NUMBER_OF_RENEWALS} certificates...')
            futures = [
                pool.submit(collect, certificate, benchmarks_queue)
                for certificate in list(certificates_queue.queue)
            ]
            wait(futures)

            benchmarks['each'] = list(benchmarks_queue.queue)
            benchmarks['total'] = overall_benchmark

            logger.info(f'Done!')

    run_renewals()

    logger.info('Certificate renewals completed!')
    # endregion Benchmark Certificate Renewals

    # region Format Benchmarks
    def summarize(values: list):
        return {
            'avg'  : sum(values) / len(values) if values else -1.0,
            'max'  : max(values),
            'min'  : min(values),
            'stdev': stdev(values),
        }

    overall = benchmarks['total']
    benchmarks_summary = {
        'numberOfRenewals' : config.NUMBER_OF_RENEWALS,
        'rateOfConcurrency': config.RATE_OF_CONCURRENCY,
        'results': {
            'overall'   : overall.duration,
            'throughput': config.NUMBER_OF_RENEWALS / overall.duration,
            **summarize([bm.duration for bm in benchmarks['each']]),
        },
        'errors': benchmarks['errors']
    }
    print(json.dumps(benchmarks_summary, indent=2))
    # endregion Format Benchmarks

def create_config():
    config = {}
    options = {
        "logLevel"         : (
            "This is the Python log level. Default is INFO.",
            "Log Level: ",
            False,
            str,
        ),
        "hostname"         : (
            "This is the TPP WebSDK service address. Both DNS and IP are supported.",
            "Hostname: ",
            True,
            str,
        ),
        "username"         : (
            "This is the TPP user simulating the test.",
            "Username: ",
            False,
            str,
        ),
        "password"         : (
            "This is the TPP user's password.",
            "Password: ",
            False,
            str,
        ),
        "token"            : (
            'This is the TPP OAuth token. Do not include the "Bearer" in the token.',
            "Token: ",
            False,
            str,
        ),
        "applicationId"    : (
            f"This is the oauth application identifier. The minimum scope required is [{TestConfig.DEFAULT_OAUTH_SCOPE}]",
            "Application ID: ",
            True,
            str,
        ),
        "rootTestFolder"   : (
            "This is the root folder under which testing will occur. The user will create subfolders for testing.",
            "Root Test Folder: ",
            True,
            str,
        ),
        "rateOfConcurrency": (
            "This is the concurrent load of requests that will be sent to the TPP server. Default is 16.",
            "Rate Of Concurrency: ",
            False,
            int,
        ),
        "numberOfRenewals" : (
            "This is the number of renewals to make per engine. Default is 500.",
            "Number Of Renewals: ",
            False,
            int,
        ),
        "certificateAuthorityDn": (
            "This is the absolute DN of the certificate authority that will sign all requests. Default is to create a self-signed certificate authority.",
            "Certificate Authority: ",
            False,
            str,
        )
    }

    print("NOTE: at least one of the username and password or the oauth token is required.")
    for option, params in options.items():
        hint, prompt, required, toType = params
        while True:
            print(hint + (" (Not required)" if not required else " (Required)"))
            choice = input(prompt)
            if choice.strip() == "":
                if required:
                    print("This value is required.")
                    continue
                break
            config[option] = toType(choice)
            break
    with open('./config.json', 'w') as f:
        json.dump(config, f, indent=2)
    proceed = input('Dumped your configuration file to "./config.json". Proceed to run the test? (y/n) ')
    if proceed.lower() == 'y':
        return config
    exit()

def main():
    run_test()

if __name__ == '__main__':
    main()
