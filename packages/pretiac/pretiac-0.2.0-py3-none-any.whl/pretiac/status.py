# Copyright 2017 fmnisme@gmail.com christian@jonak.org
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# @author: Christian Jonak-Moechel, fmnisme, Tobias von der Krone
# @contact: christian@jonak.org, fmnisme@gmail.com, tobias@vonderkrone.info
# @summary: Python library for the Icinga 2 RESTful API

"""
Retrieve status information and statistics for Icinga 2.

https://icinga.com/docs/icinga-2/latest/doc/12-icinga2-api/#status-and-statistics
"""

from __future__ import print_function

import logging
from typing import Any, Literal, Optional

from pretiac.base import Base

LOG = logging.getLogger(__name__)


Component = Literal[
    "ApiListener",
    "CIB",
    "CheckerComponent",
    "ElasticsearchWriter",
    "FileLogger",
    "GelfWriter",
    "GraphiteWriter",
    "IcingaApplication",
    "IdoMysqlConnection",
    "IdoPgsqlConnection",
    "Influxdb2Writer",
    "InfluxdbWriter",
    "JournaldLogger",
    "NotificationComponent",
    "OpenTsdbWriter",
    "PerfdataWriter",
    "SyslogLogger",
]


class Status(Base):
    """
    Icinga 2 API status class
    """

    base_url_path = "v1/status"

    def list(self, component: Optional[Component | str] = None) -> Any:
        """
        Retrieve status information and statistics for Icinga 2

        Example 1:

        .. code-block:: python

            list()

        Example 2:

        .. code-block:: python

            list('IcingaApplication')

        :param component: only list the status of this component

        :returns: status information
        :rtype: dictionary
        """

        url = self.base_url
        if component:
            url += f"/{component}"

        return self._request("GET", url)
