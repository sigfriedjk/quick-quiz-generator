# quick-quiz-generator

Generate printable math and music quizzes locally with Python 3.12. No AWS
account, credentials, or password is needed to generate quizzes.

## Run locally

From the repository root:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python src/generate_quiz.py addition 1
python src/generate_quiz.py multiplication --digits-first 2 --digits-second 1
python src/generate_quiz.py division --digits-first 3 --digits-second 1
python src/generate_quiz.py music 3
```

On Windows, activate with `.venv\Scripts\activate` instead.
Each command writes `quiz_<type>.pdf` in the current directory, replacing any
previous PDF of that type. Music selections are 1 (treble), 2 (bass), and 3 (mixed).
For division, the second operand's digit count must not exceed the first's.

To generate and display an individual note:

```sh
python src/generate_music_note.py treble C1
```

This saves `output/music_staff.png` and opens it with the system image viewer.

## Remove the legacy AWS deployment

The **Remove legacy AWS infrastructure** GitHub Action replaces deployment.
It runs when its teardown files change on `main`, or manually via **Actions →
Remove legacy AWS infrastructure → Run workflow**. It never deploys resources.

Keep the existing `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` repository
secrets until cleanup succeeds. The credentials need permission to read and
delete all resources in the Terraform state, delete the Lambda log group,
and list/delete S3 object versions and delete the bucket. The old `iam-policy.json`
is only a historical deployment policy and is not sufficient for this cleanup.
The `PASSWORD` secret is no longer used.

The workflow downloads the existing state from
`s3://sigfriedjk-quickquiz-generator-bundles/terraform.tfstate`, plans and applies
Terraform destruction, and saves updated state even if destruction fails. A
missing or inaccessible state file stops the workflow; do not substitute an empty
state. Fix the underlying error and rerun if destruction fails.

After successful destruction it deletes `/aws/lambda/quiz_lambda` and **all
contents, versions, and delete markers** in the project-specific
`sigfriedjk-quickquiz-generator-bundles` bucket, then deletes that bucket.
This permanently removes hosted quizzes, the API custom domain and its DNS
records, certificate, Lambda execution role, logs, and deployment artifacts.
The shared Route 53 hosted zone, domain registration, AWS-managed IAM policy,
and the credentials used by Actions are not project-owned resources and remain.

`terraform.tf` is retained solely for teardown; do not run `terraform apply`
against it. After a successful cleanup, remove the AWS repository secrets and
retire the teardown workflow and legacy Terraform/policy files. Rerunning after
the bucket has been deleted will stop at the state download, as intended.
