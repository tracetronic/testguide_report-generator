# Copyright (c) 2022-2023 TraceTronic GmbH
#
# SPDX-License-Identifier: MIT
FROM python:3.9
COPY . .
#Install poetry
RUN pip install poetry
#Install dependencies
RUN poetry install
#Run Test
CMD ["poetry","run", "python","-m","pytest","tests/e2e/test_e2e.py"]
