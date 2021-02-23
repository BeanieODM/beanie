FROM python:3.8

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100


RUN pip install --upgrade pip && pip install poetry


# Copy only requirements to cache them in docker layer
WORKDIR /code
COPY poetry.lock pyproject.toml /code/

# Project initialization:
RUN poetry config virtualenvs.create false  && poetry install

# Creating folders, and files for a project:
COPY . /code

# Run the tests
ENTRYPOINT ["python", "-m", "pytest", "--cov-report", "term-missing", "--cov=beanie", "--cov-branch", "--cov-fail-under=85", "tests/"]
