FROM python:3.10-slim

WORKDIR /code

# Install Poetry
RUN apt-get update && apt-get install gcc g++ curl build-essential -y
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="${PATH}:/root/.local/bin"

# Copy the pyproject.toml and poetry.lock files
COPY poetry.lock pyproject.toml ./

# Copy the rest of the application codes
COPY ./ ./

# Install dependencies
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

CMD ["python", "-m", "flask", "--app=rbf.web", "run", "--host=0.0.0.0", "--debug"]
