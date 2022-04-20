.. title:: dtaf_core

.. |date| date::

dtaf_core (DPG Test Automation Framework)
================================================


:Version: 1.37.0rc
:Date: |date|
:Author: Intel
:URL: https://gitlab.devtools.intel.com/piv/dtaf_core
:Dev Branch: dev_branch

Unit Test
----------
DTAF Core supports python2 and python3, so unit test should be verified and pass on both of them. Unit test runs in
GitLab runner docker executor, the benefit to use docker executor is that we needn't install python and prepare basic
in pipeline, easy to setup and maintain

- How to setup up GitLab runner docker executor
    + Depends on your needs, you can setup GitLab Runner on Windows/Linux
    + docker environment setup. To CentOS, you can follow below steps
        * yum install docker
        * In China, to speed up pull docker image from `Docker Hub <https://hub.docker.com/>`_ and once you want to pull image from Intel internal dock repo(CAAS), you need to re-config docker daemon.json file, change the content in /etc/docker/daemon.json to:
          
          | {
          |     "registry-mirrors": ["https://registry.docker-cn.com"],
          |     "insecure-registries":["amr-registry.caas.intel.com"]
          | }
        * Config docker proxy if needed in /etc/systemd/system/docker.service.d/http-proxy.conf

          [Service]
          Environment="HTTP_PROXY=http://child-prc.intel.com:913" "HTTPS_PROXY=http://child-prc.intel.com:913"
          NO_PROXY=".intel.com,localhost,127.0.0.1,10.239.219.0/24,10.239.56.0/24,10.96.0.0/12,10.244.0.0/16"

    + Guide for Gitlab runner `installation on Windows <https://docs.gitlab.com/runner/install/windows.html>`_ or `installation on Linux <https://docs.gitlab.com/runner/install/linux-manually.html>`_
    + Register your runner as docker executor
        * Overall reference `register on Windows <https://docs.gitlab.com/runner/register/index.html>`_ or `register on Linux <https://docs.gitlab.com/runner/register/index.html#gnulinux>`_
        * Get Gitlab instance url and registration token from `dtaf_core project > Settings > CI/CD > Runners <https://gitlab.devtools.intel.com/piv/dtaf_core/settings/ci_cd>`_
        * Add tags for the runner. By default, please set 'dtaf_ut' as one tag for the pipeline
        * Select docker as the executor type, and input python:3.7 as the default docker image(you can specify different image for each stage in your pipeline if it is needed)

- How to enable unit test in GitLab pipeline
    * Refer to `Sample dtaf_core gitlab CI/CD config <https://gitlab.devtools.intel.com/pivdevops/dtaf_core_internal/blob/steve/pages/.gitlab-ci.yml>`_
    * The reference of `.gitlab-ci.yml configuration <https://gitlab.devtools.intel.com/help/ci/yaml/README.md>`_

- How to install unit test needed libs
    * You can add all unit test needed python 3rd party libs in requirements_ut.txt file, and use 'pip install -r requirements_ut.txt' to install them before testing
    * setup HTTP_PROXY and HTTPS_PROXY .gitlab-ci.yml variables or using pip --proxy option if pip install needs use proxy

System Test
------------
DTAF core using gitlab as the system test execution framework, pytest as the test case implementation framework. DTAF core supports wide automation hardwares,
so the system test for DTAF core relies on multiple hardware configurations, to understand how to realize it in system test, please refer to System Test Markers.

- How to setup system test gitlab runner
    + How to setup gitlab shell runner executor.
        * Install gitlab runner on `Windows <https://docs.gitlab.com/runner/install/windows.html>`_ or `Linux <https://docs.gitlab.com/runner/install/linux-manually.html>`_.
        * Set register URL **https://gitlab.devtools.intel.com/**
        * Set register token **9q-PJhYWSyigf-7z5qWk**
        * Set register runner description on what this runner is for.
        * Set 'system-test' as one mandatory tag.
        * Set the executor type as 'shell'.

- System Test Markers
    + The reason of why we need system test markers is system test cases will rely on different hardware, and system test environment(SUT) has different hardware config, so gitlab pipeline stage for system test needs to dispatch different test suites to right SUTs, markers can meet this requirements.
    + System test needed markers are defined in setup.cfg file, the 'markers' option in 'tool:pytest' section(e.g. soundwave, rsc2, pdu). If you test case needed hardware doesn't be included in this option, please add it as a new marker.
    + Based on your SUT's real hardware, with the same value of the hardware in 'markers' option add it as the gitlib runner's new tag.
    + .. image:: docs/images/st-runner.PNG
    + Using these markers in the stage of system test to run the marked test case on the right target SUT by tag.

- How to use marker in your test case
    + You can use the markers which are defined in `setup.cfg <./setup.cfg>`_ file as the pytest.mark decorator
    + Refer to below sample test case

.. code-block:: python

   @pytest.mark.pdu
   @pytest.mark.banino
   def test_sample_for_pdu_banino(setup_module):
       print('pdu + banino system test called.')
       assert 2==1+1


- How to run your test cases with specified marker on specified gitlab runner in pipeline stage
    + In the system test job, you can run your test suite by pytest with -m option.
    + config tags by the markers for the SUT hardware.

.. code-block:: yaml

    ST-Sample:
      stage: SystemTest
      script:
        - pytest tests/system -m "pdu and banino" --junit-xml=./st_junit.xml --html=./st_report.html -v
      artifacts:
        reports:
          junit: ./st*.xml
        paths:
          - ./st*.html
          - ./st*.xml
      tags:
        - pdu
        - banino
        - windows


.. |copy|   unicode:: U+000A9 .. COPYRIGHT SIGN
.. |Intel(R)| unicode:: Intel U+00AE .. REGISTERED TM
.. footer::

    Copyright |copy| |Intel(R)| Corporation, 2019, All Rights Reserved.

    Other names and brands may be claimed as the property of others. Legal Notes.

    *The contents of this page are for Intel Internal Usage only*
