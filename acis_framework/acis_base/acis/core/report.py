#! /usr/bin/env python
# coding=utf-8

import allure
import pytest

class Report(): pass

report = Report()

"""
Trace links.
"""
report.link     = allure.link # For JIRA and Confluence.
report.issue    = allure.issue # Maybe gerrit commit, but not need it.
report.testcase = allure.testcase # Maybe not need it.

"""
Xfail and Skip
"""
report.xfail  = pytest.mark.xfail
report.skipif = pytest.mark.skipif

"""
Tag functions.
"""
report.epic    = allure.epic
report.feature = allure.feature
report.story   = allure.story
report.step    = allure.step

"""
Some Descriptions.
"""
report.description_html = allure.description_html
report.description = allure.description
# Maybe """""" is useful in python.


"""
Display the name of function.
"""
report.title = allure.title # allure.dynamic.title can modify the tile after do it.
#report.dynamic_title = allure.dynamic.title

"""
"""
report.fixture = pytest.fixture
report.mark = pytest.mark
report.parametrize = pytest.mark.parametrize
report.usefixtures_marked = pytest.mark.usefixtures

"""
"""
report.attach = allure.attach
report.attach_file = allure.attach.file
report.attachment_type=allure.attachment_type
# help: allure.attachment_type
