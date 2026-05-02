# Earth Meteorite Landings Analysis

## Task 1:
Extract programmatically the list of Earth Meteorite Landings from this dataset: [https://dmachek.github.io/meteorites-homework/meteorite_landings.json](https://dmachek.github.io/meteorites-homework/meteorite_landings.json)  
- How many entries are in the dataset?  
- What is the name and mass of the most massive meteorite in this dataset?  
- What is the most frequent year in this dataset?  

⚠️ **Provide your solution as a Pull Request to this repository.** ⚠️

**NOTE:** Please elaborate how did you get the results, provide the code or any means which you used to get to the results (regardless of the format/tools/framework which were used). Result itself is not sufficient.

---

## Solution (Bash + jq)

The dataset is already included in this repo as `docs/meteorite_landings.json` (a JSON array of meteorite objects).

### What the script answers (and current results)

Running:

```bash
bin/meteorites --file docs/meteorite_landings.json
```

prints:

- **How many entries are in the dataset?** `1000`
- **What is the name and mass of the most massive meteorite?** `Sikhote-Alin (23000000g)`
- **What is the most frequent year?** `1933` (16 entries)

### How it works (implementation details)

The CLI is `bin/meteorites`. It uses `jq` to compute everything directly from the JSON array.

### Walkthrough of `bin/meteorites` (step-by-step)

This section explains the script in plain language so it’s easy to review.

#### Inputs and flags

- **Default input file**: `docs/meteorite_landings.json`
- **`--file PATH`**: analyze a different local JSON file (must be a JSON array of objects)
- **`--json`**: output a single JSON object (useful for tests/CI)
- **`--help`**: prints usage

Internally the script:

- Parses the flags with a small `case`/`while` loop
- Checks `jq` is installed
- Checks the input file exists

#### Core computations (the `jq` expressions)

All computations work on the same input: a JSON array like:

- `.[]` iterates through each meteorite object
- Each object can have fields like `name`, `mass`, `year`

##### 1) Count entries

Command:

```bash
jq 'length' docs/meteorite_landings.json
```

- `length` returns the number of items in the array.

##### 2) Find the heaviest meteorite

The script builds `max_json` using:

```bash
jq -c '
  [.[] | select(.mass? and (.mass|tostring|length>0)) | {name, mass_g: (.mass|tonumber?)}]
  | map(select(.mass_g != null))
  | max_by(.mass_g)
'
```

What it does:

- `.mass?` means “mass if present, otherwise null” (avoids errors when missing).
- `(.mass|tostring|length>0)` filters out empty strings.
- `tonumber?` converts `"23000000"` → `23000000` and returns `null` if conversion fails.
- `map(select(.mass_g != null))` drops records with invalid/non-numeric mass.
- `max_by(.mass_g)` returns the object with the largest `mass_g`.

The result is a small JSON object like:

```json
{"name":"Sikhote-Alin","mass_g":23000000}
```

##### 3) Find the most frequent year

The script builds `mode_json` using:

```bash
jq -c '
  [.[] | .year? | select(type=="string" and length>=4) | .[0:4]]
  | group_by(.)
  | map({year: .[0], count: length})
  | max_by(.count)
'
```

What it does:

- `.year?` safely reads the `year` field (or null).
- `select(type=="string" and length>=4)` keeps only valid strings.
- `.[0:4]` slices `"1951-01-01T00:00:00.000"` → `"1951"`.
- `group_by(.)` groups identical years together (note: `jq` sorts for grouping).
- `map({year: .[0], count: length})` turns each group into `{year, count}`.
- `max_by(.count)` selects the year with the most records.

The result is a small JSON object like:

```json
{"year":"1933","count":16}
```

#### How outputs are produced

- If `--json` is passed, the script **combines** the values into one JSON payload using `jq -n` (no input needed, values passed as variables) and prints it as one line.
- Otherwise it prints 3 human-friendly lines matching the homework questions.

#### 1) Count entries

- It compute the number of records using `length` (because the dataset is a JSON array).

#### 2) Find the most massive meteorite

- Each record has a `mass` field (usually a string).
- The script converts `mass` into a number (grams) using `tonumber?` and ignores missing/invalid masses.
- Then it selects the maximum using `max_by(mass_g)`.

#### 3) Find the most frequent year

- Each record has a `year` like `"1951-01-01T00:00:00.000"`.
- The script takes the first 4 characters as `YYYY`, ignores missing/invalid values, then:
  - groups by year (`group_by(.)`)
  - counts entries per year
  - chooses the year with the biggest count (`max_by(.n)`)

#### Output formats

- **Output** (default): 3 lines matching the homework questions.
- **JSON output** (`--json`): prints a single JSON object:
  - `count`
  - `max_mass.name`, `max_mass.mass_g`
  - `most_frequent_year.year`, `most_frequent_year.count`

### Requirements

- `bash`
- `jq`

### Run locally

```bash
chmod +x bin/meteorites
bin/meteorites
```
Other examples:

```bash
bin/meteorites --file docs/meteorite_landings.json
bin/meteorites --json
```

Output:

```bash
bin/meteorites --json
```

### Run with GitHub Actions (CI)

This repo includes a GitHub Actions workflow at `.github/workflows/ci.yml` that runs automatically:

- **On every pull request**
- **On pushes to `main` / `master`**

What it does:

- **`test` job**: checks out the repo, runs `bin/meteorites` on `docs/meteorite_landings.json`, then runs the unit tests (`python -m unittest -v`)
- **`docker` job**: builds the Docker image and runs the CLI inside the container (`--json`)

How to use it:

- **Open a PR** with your changes and GitHub will run the workflow automatically.
- **Push to `main`** and it will run on that push too.
- **See results** in the GitHub UI under the PR “Checks” tab (or “Actions” for branch runs).

### Run with Docker

```bash
docker build -t meteorites .
docker run --rm meteorites --json
```

### Run tests

```bash
make test
```

### What the test checks (and why it’s useful)

The test file is `tests/test_cli.py`. It validates two things:

1) **The script runs successfully**
- The test executes `bin/meteorites --json` via Python `subprocess.run(..., check=True)`.
- If the script exits with a non-zero code, the test fails immediately.

2) **The results are correct for this dataset**
- The test parses the JSON output and asserts exact expected values:
  - `count == 1000`
  - heaviest meteorite is `Sikhote-Alin` with `23000000` grams
  - most frequent year is `1933` with `16` entries

So it’s not just “did the script run?” — it also confirms the computed answers match the known expected results for `docs/meteorite_landings.json`.
