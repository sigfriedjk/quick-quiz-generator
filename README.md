# quick-quiz-generator

## Running the App

1. Start by activating the environment

    ```
    python -m venv env
    source env/bin/activate
    pip install -r requirements.txt
    ```

2. Run the python file to generate a quiz

    `python generate_music_note.py treble c1`

    `python generate_quiz.py music`

    `python generate_quiz.py music && python generate_quiz.py addition 1`




## Setup 
### Terraform
```
wget -O - https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform
```

### AWS
```
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

https://developer.hashicorp.com/terraform/tutorials/aws-get-started/aws-build



## Other Notes
Use pip to remove things not in the requirements
```
pip freeze | grep -v -f requirements.txt - | grep -v '^#' | xargs pip uninstall -y
```

Upload the lambda manually

`aws s3 cp ./quiz-lambda.zip s3://sigfriedjk-quickquiz-generator-bundles/quiz-lambda.zip`

`https://s3.amazonaws.com/sigfriedjk-quickquiz-generator-bundles/quiz-lambda.zip`