pipeline {
    agent any

    environment {
        HEADLESS  = 'true'
        LOGIN_ID  = credentials('E2E_LOGIN_ID')
        LOGIN_PW  = credentials('E2E_LOGIN_PW')
    }

    stages {
        stage('Install dependencies') {
            steps {
                dir('e2e_den') {
                    bat 'pip install -r requirements.txt'
                }
            }
        }

        stage('Run E2E tests') {
            steps {
                dir('e2e_den') {
                    bat 'pytest --browser=chrome'
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'e2e_den/reports/**/*', allowEmptyArchive: true
        }
    }
}
